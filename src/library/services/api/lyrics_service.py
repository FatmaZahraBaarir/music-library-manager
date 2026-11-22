import time

import requests


class LyricsService:
	"""
	@brief Recherche les paroles d'une piste avec l'API LRCLIB.
	"""

	BASE_URL = "https://lrclib.net/api/get"
	DEFAULT_TIMEOUT = 10
	RETRY_STATUS_CODES = (429, 503)
	USER_AGENT = (
		"MusicLibraryManager/1.0 "
		"(https://github.com/FatmaZahraBaarir/music-library-manager)"
	)

	def __init__(self, session=None, timeout=DEFAULT_TIMEOUT, sleep_function=None):
		"""
		@brief Initialise le client LRCLIB.

		@param session Session HTTP, ou None pour une session requests réelle.
		@type session requests.Session ou None
		@param timeout Délai maximal d'une requête en secondes.
		@type timeout float
		@param sleep_function Fonction d'attente injectée pour les tests.
		@type sleep_function callable ou None
		"""
		self.session = requests.Session() if session is None else session
		self.timeout = timeout
		self.sleep_function = time.sleep if sleep_function is None else sleep_function

	@staticmethod
	def _normalize_required_text(value, field_name):
		"""@brief Nettoie un texte requis ou lève une erreur fonctionnelle."""
		if not isinstance(value, str) or not value.strip():
			raise ValueError(f"Le champ {field_name} est obligatoire.")
		return value.strip()

	@staticmethod
	def _retry_delay(response):
		"""@brief Calcule un délai de nouvelle tentative borné à dix secondes."""
		retry_after = response.headers.get("Retry-After", "1")
		try:
			delay = float(retry_after)
		except (TypeError, ValueError):
			delay = 1.0
		return min(max(delay, 0.0), 10.0)

	@staticmethod
	def _optional_lyrics(value):
		"""@brief Nettoie une valeur de paroles facultative."""
		if not isinstance(value, str):
			return None
		lyrics = value.strip()
		return lyrics if lyrics else None

	def _request(self, params):
		"""@brief Exécute un appel LRCLIB avec une seule nouvelle tentative."""
		last_error = None

		for attempt in range(2):
			try:
				response = self.session.get(
					self.BASE_URL,
					params=params,
					headers={"User-Agent": self.USER_AGENT},
					timeout=self.timeout,
				)
			except requests.RequestException as error:
				last_error = error
				if attempt == 0:
					self.sleep_function(1.0)
					continue
				break

			if response.status_code == 404:
				return None
			if response.status_code in self.RETRY_STATUS_CODES and attempt == 0:
				self.sleep_function(self._retry_delay(response))
				continue

			try:
				response.raise_for_status()
				data = response.json()
			except (requests.RequestException, ValueError) as error:
				last_error = error
				break

			if not isinstance(data, dict):
				raise ValueError("LRCLIB a renvoyé une réponse invalide.")
			return data

		raise ValueError("Impossible de contacter LRCLIB.") from last_error

	def get_lyrics(
		self,
		title,
		artist,
		album_title,
		duration_seconds=None,
	):
		"""
		@brief Recherche les paroles d'une piste.

		@param title Titre de la piste.
		@type title str
		@param artist Artiste de la piste.
		@type artist str
		@param album_title Titre de l'album.
		@type album_title str
		@param duration_seconds Durée en secondes, ou None.
		@type duration_seconds float ou None
		@return Paroles simples, synchronisées ou None.
		@rtype str ou None
		@raise ValueError Si les paramètres ou la réponse réseau sont invalides.
		"""
		title = self._normalize_required_text(title, "titre")
		artist = self._normalize_required_text(artist, "artiste")
		album_title = self._normalize_required_text(album_title, "album")
		params: dict[str, object] = {
			"track_name": title,
			"artist_name": artist,
			"album_name": album_title,
		}
		if duration_seconds is not None:
			try:
				duration = int(round(float(duration_seconds)))
			except (TypeError, ValueError):
				duration = None
			if duration is not None and 1 <= duration <= 3600:
				params["duration"] = duration

		data = self._request(params)
		if data is None or data.get("instrumental") is True:
			return None
		plain_lyrics = self._optional_lyrics(data.get("plainLyrics"))
		if plain_lyrics is not None:
			return plain_lyrics
		return self._optional_lyrics(data.get("syncedLyrics"))
