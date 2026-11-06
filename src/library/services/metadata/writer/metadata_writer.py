from mutagen import MutagenError
from mutagen.flac import FLAC
from mutagen.id3 import TALB, TDRC, TIT2, TPE1, TRCK
from mutagen.mp3 import MP3


class MetadataWriter:
	"""
	@brief Modifie et sauvegarde les tags des fichiers MP3 et FLAC validés.

	Les champs de Metadata ayant la valeur None ne sont pas modifiés.
	"""

	@staticmethod
	def _replace_id3_frame(tags, frame_id, frame):
		"""
		@brief Remplace toutes les occurrences d'un cadre ID3.

		@param tags Collection de tags ID3 à modifier.
		@param frame_id Identifiant du cadre ID3.
		@type frame_id str
		@param frame Nouveau cadre ID3.
		"""
		tags.delall(frame_id)
		tags.add(frame)

	def write_mp3(self, file_path, metadata):
		"""
		@brief Modifie et sauvegarde les tags ID3 d'un fichier MP3.

		@param file_path Chemin du fichier MP3 à modifier.
		@type file_path str ou pathlib.Path
		@param metadata Nouvelles métadonnées à appliquer.
		@type metadata Metadata
		@raise ValueError Si Mutagen ne peut pas modifier le fichier.
		"""
		try:
			audio = MP3(file_path)

			if audio.tags is None:
				audio.add_tags()

			tags = audio.tags
			if tags is None:
				raise ValueError("Impossible de créer les tags ID3.")

			if metadata.title is not None:
				self._replace_id3_frame(
					tags,
					"TIT2",
					TIT2(encoding=3, text=metadata.title),
				)

			if metadata.artist is not None:
				self._replace_id3_frame(
					tags,
					"TPE1",
					TPE1(encoding=3, text=metadata.artist),
				)

			if metadata.album_title is not None:
				self._replace_id3_frame(
					tags,
					"TALB",
					TALB(encoding=3, text=metadata.album_title),
				)

			if metadata.track_number is not None:
				self._replace_id3_frame(
					tags,
					"TRCK",
					TRCK(encoding=3, text=str(metadata.track_number)),
				)

			if metadata.year is not None:
				self._replace_id3_frame(
					tags,
					"TDRC",
					TDRC(encoding=3, text=str(metadata.year)),
				)

			audio.save()
		except (MutagenError, OSError) as error:
			raise ValueError(
				"Impossible de modifier les métadonnées MP3."
			) from error

	def write_flac(self, file_path, metadata):
		"""
		@brief Modifie et sauvegarde les commentaires Vorbis d'un fichier FLAC.

		@param file_path Chemin du fichier FLAC à modifier.
		@type file_path str ou pathlib.Path
		@param metadata Nouvelles métadonnées à appliquer.
		@type metadata Metadata
		@raise ValueError Si Mutagen ne peut pas modifier le fichier.
		"""
		try:
			audio = FLAC(file_path)

			if metadata.title is not None:
				audio["title"] = metadata.title
			if metadata.artist is not None:
				audio["artist"] = metadata.artist
			if metadata.album_title is not None:
				audio["album"] = metadata.album_title
			if metadata.track_number is not None:
				audio["tracknumber"] = str(metadata.track_number)
			if metadata.year is not None:
				audio["date"] = str(metadata.year)

			audio.save()
		except (MutagenError, OSError) as error:
			raise ValueError(
				"Impossible de modifier les métadonnées FLAC."
			) from error
