import time

import requests

from library.models.cover import Cover


class CoverArtArchiveClient:
	"""
	@brief Télécharge les pochettes proposées par Cover Art Archive.

	Ce client limite la quantité de données reçues et ne sauvegarde jamais
	l'image sur le disque.
	"""

	BASE_URL = "https://coverartarchive.org/release"
	DEFAULT_TIMEOUT = 10
	MAX_COVER_SIZE = 10 * 1024 * 1024
	RETRY_STATUS_CODES = (429, 503)
	USER_AGENT = (
		"MusicLibraryManager/1.0 "
		"(https://github.com/FatmaZahraBaarir/music-library-manager)"
	)

	def __init__(self, session=None, timeout=DEFAULT_TIMEOUT, sleep_function=None):
		"""
		@brief Initialise le client Cover Art Archive.

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
	def _normalize_musicbrainz_id(musicbrainz_id):
		"""@brief Nettoie l'identifiant MusicBrainz requis."""
		if not isinstance(musicbrainz_id, str) or not musicbrainz_id.strip():
			raise ValueError("L'identifiant MusicBrainz est obligatoire.")
		return musicbrainz_id.strip()

	@staticmethod
	def _retry_delay(response):
		"""@brief Calcule un délai de nouvelle tentative borné à dix secondes."""
		retry_after = response.headers.get("Retry-After", "1")
		try:
			delay = float(retry_after)
		except (TypeError, ValueError):
			delay = 1.0
		return min(max(delay, 0.0), 10.0)

	def _read_limited_content(self, response):
		"""
		@brief Lit une réponse sans dépasser la taille maximale autorisée.

		@param response Réponse HTTP à lire.
		@type response requests.Response
		@return Données binaires téléchargées.
		@rtype bytes
		@raise ValueError Si la réponse dépasse dix mébioctets.
		"""
		content_length = response.headers.get("Content-Length")
		try:
			declared_size = int(content_length) if content_length is not None else None
		except (TypeError, ValueError):
			declared_size = None
		if declared_size is not None and declared_size > self.MAX_COVER_SIZE:
			raise ValueError("La pochette dépasse la taille maximale de 10 Mio.")

		chunks = []
		total_size = 0
		for chunk in response.iter_content(chunk_size=64 * 1024):
			if not chunk:
				continue
			total_size += len(chunk)
			if total_size > self.MAX_COVER_SIZE:
				raise ValueError("La pochette dépasse la taille maximale de 10 Mio.")
			chunks.append(chunk)
		return b"".join(chunks)

	def download_front_cover(self, musicbrainz_id):
		"""
		@brief Télécharge la couverture avant d'une release MusicBrainz.

		@param musicbrainz_id Identifiant MusicBrainz de la release.
		@type musicbrainz_id str
		@return Pochette candidate non validée, ou None après une réponse 404.
		@rtype Cover ou None
		@raise ValueError Si le réseau ou la réponse empêchent le téléchargement.
		"""
		musicbrainz_id = self._normalize_musicbrainz_id(musicbrainz_id)
		url = f"{self.BASE_URL}/{musicbrainz_id}/front-500"
		last_error = None

		for attempt in range(2):
			try:
				response = self.session.get(
					url,
					headers={"User-Agent": self.USER_AGENT},
					timeout=self.timeout,
					allow_redirects=True,
					stream=True,
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
				data = self._read_limited_content(response)
			except requests.RequestException as error:
				last_error = error
				break
			except ValueError:
				raise

			if not data:
				raise ValueError("Cover Art Archive a renvoyé une image vide.")
			mime_type = response.headers.get("Content-Type", "").split(";", 1)[0]
			return Cover(
				data=data,
				mime_type=mime_type.strip().lower(),
				source=getattr(response, "url", url),
				is_validated=False,
			)

		raise ValueError("Impossible de contacter Cover Art Archive.") from last_error
