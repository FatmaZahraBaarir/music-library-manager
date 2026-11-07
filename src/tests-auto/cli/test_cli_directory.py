import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from cli.main import main
from library.models.playlist import Playlist


class FakeLibraryService:
	"""@brief Simule la création d'une playlist depuis un dossier."""

	def __init__(self, error=None):
		self.error = error
		self.received_data = None

	def create_playlist_from_directory(self, directory_path, output_path):
		"""@brief Enregistre l'appel et retourne une playlist préparée."""
		if self.error is not None:
			raise self.error

		self.received_data = (directory_path, output_path)
		tracks = [
			SimpleNamespace(file_path=Path("music/a.mp3")),
			SimpleNamespace(file_path=Path("music/b.flac")),
		]
		return Playlist(output_path.stem, file_path=output_path, tracks=tracks)


class CliDirectoryTests(unittest.TestCase):
	"""@brief Teste le traitement de l'option -d et de sa sortie XSPF."""

	def test_directory_uses_default_output(self):
		"""@brief Vérifie le nom default_playlist.xspf sans option -o."""
		service = FakeLibraryService()
		stdout = io.StringIO()

		with redirect_stdout(stdout):
			result = main(["-d", "music"], library_service=service)

		self.assertEqual(result, 0)
		self.assertEqual(
			service.received_data,
			("music", Path("default_playlist.xspf")),
		)
		self.assertIn("default_playlist.xspf", stdout.getvalue())
		self.assertIn("2 morceau(x)", stdout.getvalue())
		self.assertIn("music/a.mp3", stdout.getvalue())
		self.assertIn("music/b.flac", stdout.getvalue())

	def test_directory_uses_requested_output(self):
		"""@brief Vérifie que -o transmet le chemin demandé au service."""
		service = FakeLibraryService()
		stdout = io.StringIO()

		with redirect_stdout(stdout):
			result = main(
				["-d", "music", "-o", "playlists/sport.xspf"],
				library_service=service,
			)

		self.assertEqual(result, 0)
		self.assertEqual(
			service.received_data,
			("music", Path("playlists/sport.xspf")),
		)
		self.assertIn("playlists/sport.xspf", stdout.getvalue())

	def test_directory_error_has_no_traceback(self):
		"""@brief Vérifie qu'une erreur du service est affichée proprement."""
		service = FakeLibraryService(ValueError("Le dossier n'existe pas."))
		stderr = io.StringIO()

		with redirect_stderr(stderr):
			result = main(["-d", "missing"], library_service=service)

		self.assertEqual(result, 1)
		self.assertIn("Erreur : Le dossier n'existe pas.", stderr.getvalue())
		self.assertNotIn("Traceback", stderr.getvalue())

	def test_missing_dependency_has_functional_error(self):
		"""@brief Vérifie qu'une dépendance absente ne produit pas de traceback."""
		service = FakeLibraryService(ImportError("module absent"))
		stderr = io.StringIO()

		with redirect_stderr(stderr):
			result = main(["-d", "music"], library_service=service)

		self.assertEqual(result, 1)
		self.assertIn("dépendance Python absente", stderr.getvalue())
		self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
	unittest.main(verbosity=2)
