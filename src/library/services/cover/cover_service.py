from pathlib import Path

import magic
from mutagen import MutagenError
from mutagen.flac import FLAC
from mutagen.id3 import ID3, ID3NoHeaderError

from library.models.album import Album
from library.models.cover import Cover
from library.models.track import AudioFormat, Track


class CoverService:
	"""
	@brief Recherche, valide, met en cache et sauvegarde les pochettes.

	Le service traite les fichiers locaux et délègue uniquement le téléchargement
	HTTP au client Cover Art Archive.
	"""

	ACCEPTED_MIME_TYPES = ("image/jpeg", "image/png")
	MAX_COVER_SIZE = 10 * 1024 * 1024
	LOCAL_COVER_NAMES = (
		"cover.jpg",
		"cover.jpeg",
		"cover.png",
		"folder.jpg",
		"folder.jpeg",
		"folder.png",
		"front.jpg",
		"front.jpeg",
		"front.png",
	)

	def __init__(self, cover_art_archive_client=None, magic_function=None):
		"""
		@brief Initialise le service et ses caches mémoire.

		@param cover_art_archive_client Client HTTP, ou None pour le client réel.
		@type cover_art_archive_client CoverArtArchiveClient ou None
		@param magic_function Fonction de détection MIME injectée pour les tests.
		@type magic_function callable ou None
		"""
		if cover_art_archive_client is None:
			from library.services.cover.cover_art_archive_client import (
				CoverArtArchiveClient,
			)
			cover_art_archive_client = CoverArtArchiveClient()

		self.cover_art_archive_client = cover_art_archive_client
		if magic_function is None:
			self.magic_function = lambda data: magic.from_buffer(data, mime=True)
		else:
			self.magic_function = magic_function
		self.local_cover_cache = {}
		self.remote_cover_cache = {}

	@staticmethod
	def _validate_track(track):
		"""@brief Vérifie qu'un morceau local exploitable est fourni."""
		if not isinstance(track, Track):
			raise ValueError("La recherche de pochette attend un objet Track.")
		file_path = Path(track.file_path)
		if not file_path.is_file():
			raise ValueError("Le fichier audio du morceau est introuvable.")
		if track.format not in (AudioFormat.MP3, AudioFormat.FLAC):
			raise ValueError("Le format audio du morceau n'est pas pris en charge.")
		return file_path

	@staticmethod
	def _cache_key(file_path):
		"""@brief Produit une clé stable pour un chemin de fichier."""
		return str(Path(file_path).resolve())

	def _validate_cover_data(self, data):
		"""
		@brief Vérifie le contenu, la taille et le type MIME réel d'une image.

		@param data Données binaires à contrôler.
		@type data bytes
		@return Type MIME réel normalisé.
		@rtype str
		@raise ValueError Si les données ne décrivent pas un JPEG ou un PNG valide.
		"""
		if not isinstance(data, (bytes, bytearray)) or not data:
			raise ValueError("La pochette ne contient aucune donnée binaire valide.")
		if len(data) > self.MAX_COVER_SIZE:
			raise ValueError("La pochette dépasse la taille maximale de 10 Mio.")

		mime_type = self.magic_function(bytes(data))
		if isinstance(mime_type, bytes):
			mime_type = mime_type.decode("utf-8", errors="replace")
		mime_type = str(mime_type).split(";", 1)[0].strip().lower()
		if mime_type not in self.ACCEPTED_MIME_TYPES:
			raise ValueError("La pochette doit être une image JPEG ou PNG valide.")
		return mime_type

	def _create_local_cover(self, data, source):
		"""@brief Construit une pochette locale après validation réelle."""
		mime_type = self._validate_cover_data(data)
		return Cover(
			data=bytes(data),
			mime_type=mime_type,
			source=str(source),
			is_validated=True,
		)

	def _find_saved_cover(self, directory_path):
		"""@brief Cherche une image déjà enregistrée dans un dossier."""
		for file_name in self.LOCAL_COVER_NAMES:
			cover_path = Path(directory_path) / file_name
			if not cover_path.is_file():
				continue
			try:
				return self._create_local_cover(cover_path.read_bytes(), cover_path)
			except (OSError, ValueError):
				continue
		return None

	def _extract_mp3_cover(self, file_path):
		"""@brief Extrait en priorité le cadre ID3 APIC de couverture avant."""
		try:
			frames = ID3(file_path).getall("APIC")
		except (ID3NoHeaderError, MutagenError, OSError):
			return None

		ordered_frames = sorted(frames, key=lambda frame: 0 if frame.type == 3 else 1)
		for frame in ordered_frames:
			try:
				return self._create_local_cover(frame.data, "embedded:mp3")
			except ValueError:
				continue
		return None

	def _extract_flac_cover(self, file_path):
		"""@brief Extrait en priorité l'image FLAC de couverture avant."""
		try:
			pictures = FLAC(file_path).pictures
		except (MutagenError, OSError):
			return None

		ordered_pictures = sorted(
			pictures,
			key=lambda picture: 0 if picture.type == 3 else 1,
		)
		for picture in ordered_pictures:
			try:
				return self._create_local_cover(picture.data, "embedded:flac")
			except ValueError:
				continue
		return None

	def find_local_cover(self, track):
		"""
		@brief Cherche une pochette dans le cache, le dossier puis le fichier audio.

		@param track Morceau local à inspecter.
		@type track Track
		@return Pochette locale validée, ou None.
		@rtype Cover ou None
		@raise ValueError Si le morceau ou son fichier sont invalides.
		"""
		file_path = self._validate_track(track)
		cache_key = self._cache_key(file_path)
		if cache_key in self.local_cover_cache:
			return self.local_cover_cache[cache_key]

		cover = self._find_saved_cover(file_path.parent)
		if cover is None and track.format == AudioFormat.MP3:
			cover = self._extract_mp3_cover(file_path)
		if cover is None and track.format == AudioFormat.FLAC:
			cover = self._extract_flac_cover(file_path)
		if cover is not None:
			self.local_cover_cache[cache_key] = cover
		return cover

	def download_cover(self, album):
		"""
		@brief Télécharge puis valide une candidate pour un album MusicBrainz.

		@param album Album possédant un identifiant MusicBrainz.
		@type album Album
		@return Pochette distante non confirmée, ou None.
		@rtype Cover ou None
		@raise ValueError Si l'album ou les données téléchargées sont invalides.
		"""
		if not isinstance(album, Album):
			raise ValueError("Le téléchargement de pochette attend un objet Album.")
		musicbrainz_id = album.musicbrainz_id
		if not isinstance(musicbrainz_id, str) or not musicbrainz_id.strip():
			raise ValueError("L'album ne possède aucun identifiant MusicBrainz.")
		cache_key = musicbrainz_id.strip()
		if cache_key in self.remote_cover_cache:
			return self.remote_cover_cache[cache_key]

		candidate = self.cover_art_archive_client.download_front_cover(cache_key)
		if candidate is None:
			return None
		if not isinstance(candidate, Cover):
			raise ValueError("Cover Art Archive a renvoyé une pochette invalide.")

		mime_type = self._validate_cover_data(candidate.data)
		validated_candidate = Cover(
			data=bytes(candidate.data),
			mime_type=mime_type,
			source=candidate.source,
			is_validated=False,
		)
		self.remote_cover_cache[cache_key] = validated_candidate
		return validated_candidate

	@staticmethod
	def _cover_extension(mime_type):
		"""@brief Retourne l'extension correspondant au MIME réel validé."""
		return ".jpg" if mime_type == "image/jpeg" else ".png"

	def save_cover(self, track, cover):
		"""
		@brief Enregistre une pochette confirmée dans le dossier du morceau.

		@param track Morceau déterminant le dossier de destination.
		@type track Track
		@param cover Pochette déjà confirmée par l'interface.
		@type cover Cover
		@return Chemin de l'image enregistrée.
		@rtype pathlib.Path
		@raise ValueError Si le morceau ou la pochette sont invalides.
		@raise FileExistsError Si une autre pochette porte déjà ce nom.
		"""
		file_path = self._validate_track(track)
		if not isinstance(cover, Cover):
			raise ValueError("La sauvegarde attend un objet Cover.")
		if not cover.is_validated:
			raise ValueError("La pochette doit être confirmée avant sa sauvegarde.")

		mime_type = self._validate_cover_data(cover.data)
		output_path = file_path.parent / f"cover{self._cover_extension(mime_type)}"
		data = bytes(cover.data)
		if output_path.exists():
			if output_path.is_file() and output_path.read_bytes() == data:
				cover.mime_type = mime_type
				cover.source = str(output_path)
				self.local_cover_cache[self._cache_key(file_path)] = cover
				return output_path
			raise FileExistsError(
				f"Une autre pochette existe déjà : {output_path}"
			)

		output_path.write_bytes(data)
		cover.mime_type = mime_type
		cover.source = str(output_path)
		self.local_cover_cache[self._cache_key(file_path)] = cover
		return output_path
