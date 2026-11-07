import sys
import unittest
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.playlist import Playlist
from library.services.library_service import LibraryService


class FakeXspfService:
	"""Simule le service XSPF pour les tests."""

	def __init__(self):
		self.saved_data = None
		self.loaded_path = None
		self.loaded_playlist = Playlist("Playlist ouverte")

	def save_playlist(self, playlist, output_path):
		self.saved_data = (playlist, output_path)
		return "Playlist sauvegardée"

	def load_playlist(self, file_path):
		self.loaded_path = file_path
		return self.loaded_playlist


class FakeFileService:
	"""Retourne une liste de fichiers audio préparée pour le test."""

	def __init__(self, audio_files):
		self.audio_files = audio_files

	def find_audio_files(self, directory_path):
		return self.audio_files


class FakeMetadataService:
	"""Transforme les faux fichiers en faux morceaux."""

	def __init__(self, tracks_by_path):
		self.tracks_by_path = tracks_by_path

	def read_track(self, file_path):
		if file_path not in self.tracks_by_path:
			raise ValueError("Le fichier audio n'est pas valide.")
		return self.tracks_by_path[file_path]


class PlaylistLibraryServiceTests(unittest.TestCase):
	"""Teste le lien entre LibraryService et XspfService."""

	def setUp(self):
		self.xspf_service = FakeXspfService()
		self.library_service = LibraryService(
			file_service=object(),
			metadata_service=object(),
			metadata_input_service=object(),
			xspf_service=self.xspf_service,
		)

	def test_save_playlist_uses_xspf_service(self):
		"""Vérifie que la sauvegarde utilise le service XSPF."""
		playlist = Playlist("Ma playlist")
		output_path = Path("playlist.xspf")

		result = self.library_service.save_playlist(playlist, output_path)

		print("\nSauvegarde transmise à XspfService")
		self.assertEqual(result, "Playlist sauvegardée")
		self.assertEqual(self.xspf_service.saved_data, (playlist, output_path))

	def test_load_playlist_uses_xspf_service(self):
		"""Vérifie que l'ouverture utilise le service XSPF."""
		file_path = Path("playlist.xspf")

		result = self.library_service.load_playlist(file_path)

		print("\nOuverture transmise à XspfService")
		self.assertIs(result, self.xspf_service.loaded_playlist)
		self.assertEqual(self.xspf_service.loaded_path, file_path)

	def test_create_default_playlist_from_directory(self):
		"""Vérifie l'exploration puis la sauvegarde de la playlist par défaut."""
		audio_files = [Path("music/a.mp3"), Path("music/b.flac")]
		tracks = [object(), object()]
		service = LibraryService(
			file_service=FakeFileService(audio_files),
			metadata_service=FakeMetadataService(dict(zip(audio_files, tracks))),
			metadata_input_service=object(),
			xspf_service=self.xspf_service,
		)

		playlist = service.create_playlist_from_directory("music")

		print("\nPlaylist par défaut créée depuis un dossier")
		self.assertEqual(playlist.name, "default_playlist")
		self.assertEqual(playlist.tracks, tracks)
		self.assertEqual(
			self.xspf_service.saved_data,
			(playlist, Path("default_playlist.xspf")),
		)

	def test_create_empty_playlist(self):
		"""Vérifie la création d'une playlist personnalisée vide."""
		playlist = self.library_service.create_empty_playlist("Sport")

		self.assertEqual(playlist.name, "Sport")
		self.assertEqual(playlist.tracks, [])

	def test_add_tracks_preserves_order_and_duplicates(self):
		"""Vérifie l'ajout, l'ordre et l'autorisation des doublons."""
		first_path = Path("music/first.mp3")
		second_path = Path("music/second.flac")
		first_track = object()
		second_track = object()
		service = LibraryService(
			file_service=object(),
			metadata_service=FakeMetadataService({
				first_path: first_track,
				second_path: second_track,
			}),
			metadata_input_service=object(),
			xspf_service=self.xspf_service,
		)
		playlist = Playlist("Sport")

		service.add_track_to_playlist(playlist, first_path)
		service.add_track_to_playlist(playlist, second_path)
		service.add_track_to_playlist(playlist, first_path)

		self.assertEqual(
			playlist.tracks,
			[first_track, second_track, first_track],
		)

	def test_invalid_file_is_not_added(self):
		"""Vérifie qu'un fichier invalide n'est pas ajouté à la playlist."""
		service = LibraryService(
			file_service=object(),
			metadata_service=FakeMetadataService({}),
			metadata_input_service=object(),
			xspf_service=self.xspf_service,
		)
		playlist = Playlist("Sport")

		with self.assertRaises(ValueError):
			service.add_track_to_playlist(playlist, Path("notes.txt"))

		self.assertEqual(playlist.tracks, [])

	def test_remove_track_uses_its_position(self):
		"""Vérifie le retrait d'un morceau sans modifier l'ordre restant."""
		first_track = object()
		second_track = object()
		third_track = object()
		playlist = Playlist(
			"Sport",
			tracks=[first_track, second_track, third_track],
		)

		removed_track = self.library_service.remove_track_from_playlist(
			playlist,
			1,
		)

		self.assertIs(removed_track, second_track)
		self.assertEqual(playlist.tracks, [first_track, third_track])


if __name__ == "__main__":
	unittest.main(verbosity=2)
