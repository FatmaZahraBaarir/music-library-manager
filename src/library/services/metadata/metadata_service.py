from pathlib import Path

from library.models.track import AudioFormat, Track
from library.services.file.filter.file_filtrer import FileFiltrer
from library.services.metadata.reader.metadata_reader import MetadataReader
from library.services.metadata.writer.metadata_writer import MetadataWriter


class MetadataService:
	"""
	@brief Valide le format et orchestre la lecture et l'écriture des tags.

	Le service choisit les traitements MP3 ou FLAC sans connaître les détails
	des tags ID3 ou des commentaires Vorbis.
	"""

	def __init__(self, metadata_reader=None, metadata_writer=None):
		"""
		@brief Initialise le service de métadonnées.

		@param metadata_reader Lecteur à utiliser, ou None pour le lecteur réel.
		@type metadata_reader MetadataReader ou None
		@param metadata_writer Writer à utiliser, ou None pour le writer réel.
		@type metadata_writer MetadataWriter ou None
		"""
		if metadata_reader is None:
			metadata_reader = MetadataReader()
		if metadata_writer is None:
			metadata_writer = MetadataWriter()

		self.metadata_reader = metadata_reader
		self.metadata_writer = metadata_writer

	@staticmethod
	def _detect_format(file_path):
		"""
		@brief Valide un fichier et détermine son format audio.

		@param file_path Chemin du fichier à vérifier.
		@type file_path str ou pathlib.Path
		@return Format MP3 ou FLAC.
		@rtype AudioFormat
		@raise ValueError Si le fichier n'est ni un MP3 ni un FLAC valide.
		"""
		if FileFiltrer.is_mp3_file(file_path):
			return AudioFormat.MP3

		if FileFiltrer.is_flac_file(file_path):
			return AudioFormat.FLAC

		raise ValueError(
			"Le fichier n'est pas un MP3 ou un FLAC valide."
		)

	def read_metadata(self, file_path):
		"""
		@brief Valide un fichier puis extrait ses métadonnées.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@return Métadonnées extraites du fichier.
		@rtype Metadata
		@raise ValueError Si le fichier n'est ni un MP3 ni un FLAC valide.
		"""
		audio_format = self._detect_format(file_path)

		if audio_format == AudioFormat.MP3:
			return self.metadata_reader.read_mp3(file_path)

		return self.metadata_reader.read_flac(file_path)

	def update_metadata(self, file_path, metadata):
		"""
		@brief Valide un fichier, sauvegarde ses tags puis les relit.

		Les champs de Metadata ayant la valeur None restent inchangés.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@param metadata Nouvelles métadonnées à appliquer.
		@type metadata Metadata
		@return Métadonnées sauvegardées et relues.
		@rtype Metadata
		@raise ValueError Si le fichier n'est pas valide ou modifiable.
		"""
		audio_format = self._detect_format(file_path)

		if audio_format == AudioFormat.MP3:
			self.metadata_writer.write_mp3(file_path, metadata)
		else:
			self.metadata_writer.write_flac(file_path, metadata)

		return self.read_metadata(file_path)

	def read_track(self, file_path):
		"""
		@brief Construit un Track avec son format, sa durée et ses métadonnées.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@return Morceau construit à partir du fichier.
		@rtype Track
		@raise ValueError Si le fichier n'est pas un MP3 ou un FLAC valide.
		"""
		audio_format = self._detect_format(file_path)

		if audio_format == AudioFormat.MP3:
			metadata = self.metadata_reader.read_mp3(file_path)
			duration_seconds = self.metadata_reader.read_mp3_duration(file_path)
		else:
			metadata = self.metadata_reader.read_flac(file_path)
			duration_seconds = self.metadata_reader.read_flac_duration(file_path)

		return Track(
			file_path=Path(file_path),
			format=audio_format,
			metadata=metadata,
			duration_seconds=duration_seconds,
		)
