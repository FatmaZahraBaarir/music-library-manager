import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from cli.main import format_duration, main
from library.models.metadata import Metadata


class FakeLibraryService:
	"""@brief Simule la lecture des métadonnées d'un fichier audio."""

	def __init__(self):
		self.received_file = None
		self.received_update = None
		self.update_calls = 0

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

	def read_track(self, file_path):
		"""@brief Retourne les métadonnées et une durée préparée."""
		return SimpleNamespace(
			metadata=self.read_metadata(file_path),
			duration_seconds=185,
		)

	def update_metadata_from_text(self, **metadata_fields):
		"""@brief Enregistre la modification et retourne les valeurs sauvegardées."""
		self.received_update = metadata_fields
		self.update_calls += 1
		return Metadata(
			title=metadata_fields["title_text"],
			artist=metadata_fields["artist_text"],
			album_title=metadata_fields["album_title_text"],
			track_number=int(metadata_fields["track_number_text"]),
			year=int(metadata_fields["year_text"]),
		)


class CliFileTests(unittest.TestCase):
	"""@brief Teste l'affichage des métadonnées avec l'option -f."""

	def test_duration_under_one_hour_uses_minutes_and_seconds(self):
		"""@brief Formate une durée courte avec deux blocs."""
		self.assertEqual(format_duration(65), "01:05")

	def test_duration_over_one_hour_uses_hours_minutes_and_seconds(self):
		"""@brief Formate une durée longue avec trois blocs."""
		self.assertEqual(format_duration(3661), "01:01:01")

	def test_missing_duration_is_displayed_as_unknown(self):
		"""@brief Rend une durée absente lisible dans le CLI."""
		self.assertEqual(format_duration(None), "Non renseignée")

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
		self.assertIn("Durée : 03:05", output)

	def test_file_updates_and_displays_metadata(self):
		"""@brief Vérifie la modification puis l'affichage des métadonnées relues."""
		service = FakeLibraryService()
		stdout = io.StringIO()

		with redirect_stdout(stdout):
			result = main([
				"-f",
				"music.mp3",
				"--title",
				"New title",
				"--artist",
				"New artist",
				"--album",
				"New album",
				"--track-number",
				"7",
				"--year",
				"2027",
			], library_service=service)

		self.assertEqual(result, 0)
		self.assertEqual(service.received_update, {
			"file_path": "music.mp3",
			"title_text": "New title",
			"artist_text": "New artist",
			"album_title_text": "New album",
			"track_number_text": "7",
			"year_text": "2027",
		})
		output = stdout.getvalue()
		self.assertEqual(service.update_calls, 1)
		self.assertIn("Avant modification", output)
		self.assertIn("Titre : Test title", output)
		self.assertIn("Après modification", output)
		self.assertIn("Titre : New title", output)
		self.assertLess(
			output.index("Avant modification"),
			output.index("Après modification"),
		)


if __name__ == "__main__":
	unittest.main(verbosity=2)
