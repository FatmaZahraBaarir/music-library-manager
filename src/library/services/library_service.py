from pathlib import Path

from library.interfaces.library_interface import LibraryInterface
from library.models.playlist import Playlist


class LibraryService(LibraryInterface):
	"""
	@brief Centralise les fonctionnalités utilisées par le CLI et la GUI.

	Cette façade utilise les services de fichiers, de métadonnées et de playlists.
	"""

	def __init__(
		self,
		file_service=None,
		metadata_service=None,
		metadata_input_service=None,
		xspf_service=None,
	):
		"""
		@brief Initialise la façade avec ses services techniques.

		@param file_service Service d'exploration, ou None pour le service réel.
		@type file_service FileService ou None
		@param metadata_service Service de métadonnées, ou None pour le service réel.
		@type metadata_service MetadataService ou None
		@param metadata_input_service Service de conversion des saisies, ou None.
		@type metadata_input_service MetadataInputService ou None
		@param xspf_service Service de playlists, ou None pour le service réel.
		@type xspf_service XspfService ou None
		"""
		if file_service is None:
			from library.services.file.file_service import FileService
			file_service = FileService()
		if metadata_service is None:
			from library.services.metadata.metadata_service import MetadataService
			metadata_service = MetadataService()
		if metadata_input_service is None:
			from library.services.metadata.metadata_input_service import MetadataInputService
			metadata_input_service = MetadataInputService()
		if xspf_service is None:
			from library.services.playlist.xspf_service import XspfService
			xspf_service = XspfService()

		self.file_service = file_service
		self.metadata_service = metadata_service
		self.metadata_input_service = metadata_input_service
		self.xspf_service = xspf_service

	def find_audio_files(self, directory_path):
		"""
		@brief Explore récursivement un dossier et trouve ses fichiers audio.

		@param directory_path Chemin du dossier à explorer.
		@type directory_path str ou pathlib.Path
		@return Liste triée des fichiers MP3 et FLAC valides.
		@rtype list de pathlib.Path
		"""
		return self.file_service.find_audio_files(directory_path)

	def read_metadata(self, file_path):
		"""
		@brief Lit les métadonnées d'un fichier audio valide.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@return Métadonnées extraites du fichier.
		@rtype Metadata
		"""
		return self.metadata_service.read_metadata(file_path)

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
		return self.metadata_service.update_metadata(file_path, metadata)

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
		@raise ValueError Si une saisie est invalide ou le fichier non modifiable.
		"""
		metadata = self.metadata_input_service.create_metadata(
			title_text=title_text,
			artist_text=artist_text,
			album_title_text=album_title_text,
			track_number_text=track_number_text,
			year_text=year_text,
		)
		return self.update_metadata(file_path, metadata)

	def read_track(self, file_path):
		"""
		@brief Construit un morceau depuis un fichier audio.

		@param file_path Chemin du fichier MP3 ou FLAC.
		@type file_path str ou pathlib.Path
		@return Morceau contenant son format, sa durée et ses métadonnées.
		@rtype Track
		"""
		return self.metadata_service.read_track(file_path)

	def scan_library(self, directory_path):
		"""
		@brief Explore un dossier et construit tous les morceaux reconnus.

		@param directory_path Chemin du dossier à explorer.
		@type directory_path str ou pathlib.Path
		@return Liste triée des morceaux trouvés.
		@rtype list de Track
		"""
		audio_files = self.find_audio_files(directory_path)
		return [self.read_track(file_path) for file_path in audio_files]

	def create_empty_playlist(self, name):
		"""
		@brief Crée une playlist personnalisée sans morceau.

		@param name Nom de la nouvelle playlist.
		@type name str
		@return Playlist vide portant le nom demandé.
		@rtype Playlist
		"""
		return Playlist(name)

	def add_track_to_playlist(self, playlist, file_path):
		"""
		@brief Valide un fichier audio puis l'ajoute à la fin d'une playlist.

		Les doublons sont acceptés et l'ordre d'ajout est conservé.

		@param playlist Playlist à modifier.
		@type playlist Playlist
		@param file_path Chemin du fichier MP3 ou FLAC à ajouter.
		@type file_path str ou pathlib.Path
		@return Morceau ajouté à la playlist.
		@rtype Track
		@raise ValueError Si le fichier n'est pas un MP3 ou un FLAC valide.
		"""
		# read_track vérifie le format avant de construire le morceau
		track = self.read_track(file_path)
		playlist.tracks.append(track)

		return track

	def remove_track_from_playlist(self, playlist, position):
		"""
		@brief Retire un morceau d'une playlist selon sa position.

		@param playlist Playlist à modifier.
		@type playlist Playlist
		@param position Position du morceau dans la playlist.
		@type position int
		@return Morceau retiré de la playlist.
		@rtype Track
		@raise IndexError Si la position n'existe pas.
		"""
		return playlist.tracks.pop(position)

	def create_playlist_from_directory(
		self,
		directory_path,
		output_path="default_playlist.xspf",
	):
		"""Explore un dossier puis sauvegarde les morceaux dans une playlist XSPF."""
		output_path = Path(output_path)
		tracks = self.scan_library(directory_path)
		playlist = Playlist(output_path.stem, tracks=tracks)
		self.save_playlist(playlist, output_path)
		return playlist

	def save_playlist(self, playlist, output_path):
		"""Sauvegarde une playlist dans un fichier XSPF."""
		return self.xspf_service.save_playlist(playlist, output_path)

	def load_playlist(self, file_path):
		"""Ouvre une playlist depuis un fichier XSPF."""
		return self.xspf_service.load_playlist(file_path)
