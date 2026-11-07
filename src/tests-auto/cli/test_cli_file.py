import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from cli.main import main
from library.models.metadata import Metadata


class FakeLibraryService:
	"""@brief Simule la lecture des métadonnées d'un fichier audio."""

	def __init__(self):
		self.received_file = None

	def read_metadata(self, file_path):
		"""@brief Enregistre le chemin et retourne des métadonnées préparées."""
		self.received_file = file_path
		return Metadata(
			title="Test title",
			artist="Test artist",
			album_title="Test album",
			track_number=4,
			year=2026,
		)


class CliFileTests(unittest.TestCase):
	"""@brief Teste l'affichage des métadonnées avec l'option -f."""

	def test_file_displays_metadata(self):
		"""@brief Vérifie que -f lit et affiche les cinq métadonnées."""
		service = FakeLibraryService()
		stdout = io.StringIO()

		with redirect_stdout(stdout):
			result = main(["-f", "music.mp3"], library_service=service)

		output = stdout.getvalue()
		self.assertEqual(result, 0)
		self.assertEqual(service.received_file, "music.mp3")
		self.assertIn("Titre : Test title", output)
		self.assertIn("Artiste : Test artist", output)
		self.assertIn("Album : Test album", output)
		self.assertIn("Piste : 4", output)
		self.assertIn("Année : 2026", output)


if __name__ == "__main__":
	unittest.main(verbosity=2)
