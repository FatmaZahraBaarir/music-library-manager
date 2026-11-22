from library.services.api.lyrics_service import LyricsService
from library.services.api.musicbrainz_service import MusicBrainzService


class AlbumService:
	"""
	@brief Orchestre la recherche d'un album et des paroles de ses pistes.
	"""

	def __init__(self, musicbrainz_service=None, lyrics_service=None):
		"""
		@brief Initialise le service et son cache mémoire.

		@param musicbrainz_service Service MusicBrainz injecté, ou None.
		@type musicbrainz_service MusicBrainzService ou None
		@param lyrics_service Service LRCLIB injecté, ou None.
		@type lyrics_service LyricsService ou None
		"""
		if musicbrainz_service is None:
			musicbrainz_service = MusicBrainzService()
		if lyrics_service is None:
			lyrics_service = LyricsService()
		self.musicbrainz_service = musicbrainz_service
		self.lyrics_service = lyrics_service
		self.album_cache = {}

	@staticmethod
	def _normalize_required_text(value, field_name):
		"""@brief Nettoie un texte requis ou lève une erreur fonctionnelle."""
		if not isinstance(value, str) or not value.strip():
			raise ValueError(f"Le champ {field_name} est obligatoire.")
		return value.strip()

	@classmethod
	def _cache_key(cls, artist, album_title):
		"""@brief Construit une clé insensible à la casse et aux espaces externes."""
		return (
			cls._normalize_required_text(artist, "artiste").casefold(),
			cls._normalize_required_text(album_title, "album").casefold(),
		)

	def get_album(self, artist, album_title):
		"""
		@brief Recherche un album et enrichit ses pistes avec leurs paroles.

		@param artist Artiste principal recherché.
		@type artist str
		@param album_title Titre de l'album recherché.
		@type album_title str
		@return Album enrichi, éventuellement avec des paroles absentes.
		@rtype Album
		@raise ValueError Si l'album ne peut pas être récupéré.
		"""
		artist = self._normalize_required_text(artist, "artiste")
		album_title = self._normalize_required_text(album_title, "album")
		key = self._cache_key(artist, album_title)
		if key in self.album_cache:
			return self.album_cache[key]

		album = self.musicbrainz_service.search_album(artist, album_title)
		for track in album.tracks:
			try:
				track.lyrics = self.lyrics_service.get_lyrics(
					title=track.title,
					artist=track.artist or album.artist,
					album_title=album.title,
					duration_seconds=track.duration_seconds,
				)
			except ValueError:
				track.lyrics = None

		self.album_cache[key] = album
		return album
