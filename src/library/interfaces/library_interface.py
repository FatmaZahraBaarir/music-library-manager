from abc import ABC, abstractmethod


class LibraryInterface(ABC):
	"""
	@brief Définit le point d'entrée commun du CLI et de la GUI.

	Cette interface masque les services techniques utilisés pour explorer les
	dossiers et gérer les métadonnées.
	"""

	@abstractmethod
	def find_audio_files(self, directory_path):
		"""
		@brief Explore récursivement un dossier et trouve ses fichiers audio.

		@param directory_path Chemin du dossier à explorer.
		@type directory_path str ou pathlib.Path
		@return Liste triée des fichiers MP3 et FLAC valides.
		@rtype list de pathlib.Path
		"""
		raise NotImplementedError

	@abstractmethod
	def read_metadata(self, file_path):
		"""
		@brief Lit les métadonnées d'un fichier audio valide.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@return Métadonnées extraites du fichier.
		@rtype Metadata
		"""
		raise NotImplementedError

	@abstractmethod
	def update_metadata(self, file_path, metadata):
		"""
		@brief Modifie puis relit les métadonnées d'un fichier audio.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@param metadata Métadonnées à appliquer.
		@type metadata Metadata
		@return Métadonnées sauvegardées et relues.
		@rtype Metadata
		"""
		raise NotImplementedError

	@abstractmethod
	def update_metadata_from_text(
		self,
		file_path,
		title_text=None,
		artist_text=None,
		album_title_text=None,
		track_number_text=None,
		year_text=None,
	):
		"""
		@brief Convertit les saisies textuelles puis modifie les métadonnées.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@param title_text Titre saisi, ou None.
		@type title_text str ou None
		@param artist_text Artiste saisi, ou None.
		@type artist_text str ou None
		@param album_title_text Album saisi, ou None.
		@type album_title_text str ou None
		@param track_number_text Numéro de piste saisi, ou None.
		@type track_number_text str ou None
		@param year_text Année saisie, ou None.
		@type year_text str ou None
		@return Métadonnées sauvegardées et relues.
		@rtype Metadata
		"""
		raise NotImplementedError

	@abstractmethod
	def read_track(self, file_path):
		"""
		@brief Construit un morceau depuis un fichier audio.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@return Morceau contenant son format, sa durée et ses métadonnées.
		@rtype Track
		"""
		raise NotImplementedError

	@abstractmethod
	def scan_library(self, directory_path):
		"""
		@brief Explore un dossier et construit tous les morceaux reconnus.

		@param directory_path Chemin du dossier à explorer.
		@type directory_path str ou pathlib.Path
		@return Liste triée des morceaux trouvés.
		@rtype list de Track
		"""
		raise NotImplementedError

	@abstractmethod
	def create_empty_playlist(self, name):
		"""Crée une playlist personnalisée sans morceau."""
		raise NotImplementedError

	@abstractmethod
	def add_track_to_playlist(self, playlist, file_path):
		"""Valide un fichier audio puis l'ajoute à la fin d'une playlist."""
		raise NotImplementedError

	@abstractmethod
	def remove_track_from_playlist(self, playlist, position):
		"""Retire et retourne le morceau situé à la position demandée."""
		raise NotImplementedError

	@abstractmethod
	def create_playlist_from_directory(
		self,
		directory_path,
		output_path="default_playlist.xspf",
	):
		"""Explore un dossier et sauvegarde la playlist XSPF obtenue."""
		raise NotImplementedError

	@abstractmethod
	def save_playlist(self, playlist, output_path):
		"""Sauvegarde une playlist dans un fichier XSPF."""
		raise NotImplementedError

	@abstractmethod
	def load_playlist(self, file_path):
		"""Ouvre une playlist depuis un fichier XSPF."""
		raise NotImplementedError
