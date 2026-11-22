import time

import requests

from library.models.album import Album
from library.models.album_track_info import AlbumTrackInfo


class MusicBrainzService:
	"""
	@brief Recherche les informations d'une release avec l'API MusicBrainz.

	Le service respecte la limite publique d'une requête par seconde et utilise
	un User-Agent qui identifie le projet.
	"""

	BASE_URL = "https://musicbrainz.org/ws/2"
	DEFAULT_TIMEOUT = 10
	MINIMUM_REQUEST_INTERVAL = 1.0
	RETRY_STATUS_CODES = (429, 503)
	USER_AGENT = (
		"MusicLibraryManager/1.0 "
		"(https://github.com/FatmaZahraBaarir/music-library-manager)"
	)

	def __init__(
		self,
		session=None,
		timeout=DEFAULT_TIMEOUT,
		sleep_function=None,
		time_function=None,
	):
		"""
		@brief Initialise le client MusicBrainz.

		@param session Session HTTP, ou None pour une session requests réelle.
		@type session requests.Session ou None
		@param timeout Délai maximal d'une requête en secondes.
		@type timeout float
		@param sleep_function Fonction d'attente injectée pour les tests.
		@type sleep_function callable ou None
		@param time_function Fonction donnant le temps monotone pour les tests.
		@type time_function callable ou None
		"""
		self.session = requests.Session() if session is None else session
		self.timeout = timeout
		self.sleep_function = time.sleep if sleep_function is None else sleep_function
		self.time_function = time.monotonic if time_function is None else time_function
		self.last_request_time = None

	@staticmethod
	def _normalize_required_text(value, field_name):
		"""@brief Nettoie un texte requis ou lève une erreur fonctionnelle."""
		if not isinstance(value, str) or not value.strip():
			raise ValueError(f"Le champ {field_name} est obligatoire.")
		return value.strip()

	@staticmethod
	def _escape_query_value(value):
		"""@brief Protège les caractères réservés dans une recherche MusicBrainz."""
		return value.replace("\\", "\\\\").replace('"', '\\"')

	@staticmethod
	def _first_text(value):
		"""@brief Retourne un texte non vide ou None."""
		if value is None:
			return None
		text = str(value).strip()
		return text if text else None

	@staticmethod
	def _artist_name(data, default=None):
		"""@brief Extrait le crédit artiste d'une réponse MusicBrainz."""
		artist_credit = data.get("artist-credit") if isinstance(data, dict) else None
		if isinstance(artist_credit, list):
			names = []
			for credit in artist_credit:
				if not isinstance(credit, dict):
					continue
				name = credit.get("name")
				if name is None and isinstance(credit.get("artist"), dict):
					name = credit["artist"].get("name")
				if name:
					names.append(str(name).strip())
			return " & ".join(name for name in names if name) or default

		phrase = data.get("artist-credit-phrase") if isinstance(data, dict) else None
		return MusicBrainzService._first_text(phrase) or default

	def _wait_for_rate_limit(self):
		"""@brief Attend si nécessaire avant le prochain appel MusicBrainz."""
		if self.last_request_time is None:
			return

		elapsed = self.time_function() - self.last_request_time
		remaining = self.MINIMUM_REQUEST_INTERVAL - elapsed
		if remaining > 0:
			self.sleep_function(remaining)

	@staticmethod
	def _retry_delay(response):
		"""@brief Calcule un délai de nouvelle tentative borné à dix secondes."""
		retry_after = response.headers.get("Retry-After", "1")
		try:
			delay = float(retry_after)
		except (TypeError, ValueError):
			delay = 1.0
		return min(max(delay, 0.0), 10.0)

	def _request_json(self, url, params):
		"""
		@brief Exécute une requête JSON avec une seule nouvelle tentative.

		@raise ValueError Si MusicBrainz reste inaccessible ou répond mal.
		"""
		last_error = None

		for attempt in range(2):
			self._wait_for_rate_limit()
			self.last_request_time = self.time_function()

			try:
				response = self.session.get(
					url,
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
				raise ValueError("MusicBrainz a renvoyé une réponse invalide.")
			return data

		raise ValueError("Impossible de contacter MusicBrainz.") from last_error

	@classmethod
	def _is_exact_official_release(cls, release, artist, album_title):
		"""@brief Vérifie le titre, l'artiste et le statut d'une release."""
		if not isinstance(release, dict):
			return False
		release_title = cls._first_text(release.get("title"))
		release_artist = cls._artist_name(release)
		status = cls._first_text(release.get("status"))
		return (
			release_title is not None
			and release_artist is not None
			and status is not None
			and release_title.casefold() == album_title.casefold()
			and release_artist.casefold() == artist.casefold()
			and status.casefold() == "official"
		)

	@staticmethod
	def _release_score(release):
		"""@brief Convertit le score de recherche MusicBrainz en nombre."""
		try:
			return float(release.get("score", 0))
		except (TypeError, ValueError):
			return 0.0

	def _select_release(self, releases, artist, album_title):
		"""@brief Sélectionne la meilleure édition officielle exacte."""
		exact_releases = [
			release
			for release in releases
			if self._is_exact_official_release(release, artist, album_title)
		]
		if not exact_releases:
			raise ValueError("Aucun album officiel correspondant n'a été trouvé.")
		return max(exact_releases, key=self._release_score)

	@staticmethod
	def _duration_seconds(track):
		"""@brief Convertit la durée MusicBrainz de millisecondes en secondes."""
		length = track.get("length")
		if length is None and isinstance(track.get("recording"), dict):
			length = track["recording"].get("length")
		try:
			return float(length) / 1000 if length is not None else None
		except (TypeError, ValueError):
			return None

	def _build_tracks(self, release, album_artist):
		"""@brief Construit les pistes de tous les disques d'une release."""
		tracks = []
		media = release.get("media")
		if not isinstance(media, list):
			raise ValueError("MusicBrainz n'a renvoyé aucune liste de pistes.")

		for medium in media:
			if not isinstance(medium, dict):
				continue
			disc_number = medium.get("position")
			medium_tracks = medium.get("tracks")
			if not isinstance(medium_tracks, list):
				continue

			for track in medium_tracks:
				if not isinstance(track, dict):
					continue
				recording = track.get("recording")
				if not isinstance(recording, dict):
					recording = {}
				title = self._first_text(track.get("title"))
				if title is None:
					title = self._first_text(recording.get("title"))
				if title is None:
					continue
				track_artist = self._artist_name(track)
				if track_artist is None:
					track_artist = self._artist_name(recording, album_artist)

				tracks.append(
					AlbumTrackInfo(
						title=title,
						artist=track_artist,
						disc_number=disc_number,
						position=track.get("position"),
						duration_seconds=self._duration_seconds(track),
					)
				)

		if not tracks:
			raise ValueError("MusicBrainz n'a renvoyé aucune piste exploitable.")
		return tracks

	def search_album(self, artist, album_title):
		"""
		@brief Recherche une édition officielle et construit son album.

		@param artist Artiste principal recherché.
		@type artist str
		@param album_title Titre exact de l'album recherché.
		@type album_title str
		@return Album complet sans les paroles.
		@rtype Album
		@raise ValueError Si les paramètres, le réseau ou la réponse sont invalides.
		"""
		artist = self._normalize_required_text(artist, "artiste")
		album_title = self._normalize_required_text(album_title, "album")
		query = (
			f'release:"{self._escape_query_value(album_title)}" '
			f'AND artist:"{self._escape_query_value(artist)}"'
		)
		search_data = self._request_json(
			f"{self.BASE_URL}/release/",
			{"query": query, "fmt": "json", "limit": 25},
		)
		releases = search_data.get("releases")
		if not isinstance(releases, list):
			raise ValueError("MusicBrainz a renvoyé une réponse invalide.")

		selected_release = self._select_release(releases, artist, album_title)
		release_id = self._first_text(selected_release.get("id"))
		if release_id is None:
			raise ValueError("La release MusicBrainz ne possède aucun identifiant.")

		release = self._request_json(
			f"{self.BASE_URL}/release/{release_id}",
			{"inc": "recordings+artist-credits", "fmt": "json"},
		)
		album_artist = self._artist_name(release, artist)
		return Album(
			title=self._first_text(release.get("title")) or album_title,
			artist=album_artist,
			musicbrainz_id=release_id,
			release_date=self._first_text(release.get("date")),
			country=self._first_text(release.get("country")),
			status=self._first_text(release.get("status")),
			barcode=self._first_text(release.get("barcode")),
			tracks=self._build_tracks(release, album_artist),
		)
