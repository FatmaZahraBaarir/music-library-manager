from pathlib import Path

from library.services.file.filter.file_filtrer import FileFiltrer


class FileService:
	"""
	@brief Explore les dossiers et sélectionne les fichiers audio valides.

	La validation de l'extension et du type MIME est déléguée à FileFiltrer.
	"""

	@staticmethod
	def find_audio_files(directory_path):
		"""
		@brief Explore récursivement un dossier et filtre ses fichiers audio.

		@param directory_path Chemin du dossier à explorer.
		@type directory_path str ou pathlib.Path
		@return Liste triée des fichiers MP3 et FLAC valides.
		@rtype list de pathlib.Path
		@raise ValueError Si le chemin n'existe pas, n'est pas un dossier ou
		       si l'exploration échoue.
		"""
		directory = Path(directory_path)

		if not directory.exists():
			raise ValueError("Le dossier à explorer n'existe pas.")

		if not directory.is_dir():
			raise ValueError("Le chemin à explorer n'est pas un dossier.")

		audio_files = []

		try:
			for file_path in directory.rglob("*"):
				if not file_path.is_file():
					continue

				if (
					FileFiltrer.is_mp3_file(file_path)
					or FileFiltrer.is_flac_file(file_path)
				):
					audio_files.append(file_path)
		except OSError as error:
			raise ValueError(
				"Impossible d'explorer complètement le dossier."
			) from error

		return sorted(audio_files, key=lambda path: str(path).lower())
