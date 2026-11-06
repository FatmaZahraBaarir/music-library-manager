from mutagen import MutagenError
from mutagen.id3 import TIT2
from mutagen.mp3 import MP3


class MetadataWriter:
	"""
	@brief Modifie et sauvegarde les tags des fichiers audio validés.

	Cette première version prend uniquement en charge le titre d'un MP3.
	Les champs de Metadata ayant la valeur None ne sont pas modifiés.
	"""

	def write_mp3(self, file_path, metadata):
		"""
		@brief Modifie le titre ID3 d'un fichier MP3.

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
				tags.delall("TIT2")
				tags.add(TIT2(encoding=3, text=metadata.title))

			audio.save()
		except (MutagenError, OSError) as error:
			raise ValueError(
				"Impossible de modifier les métadonnées MP3."
			) from error
