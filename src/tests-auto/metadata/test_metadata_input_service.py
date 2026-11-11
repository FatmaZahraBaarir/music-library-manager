import sys
import unittest
from pathlib import Path

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.metadata import Metadata
from library.services.metadata.metadata_input_service import MetadataInputService


class MetadataInputServiceTests(unittest.TestCase):
	"""
	@brief Vérifie la conversion des saisies du CLI et de la GUI.
	"""

	def setUp(self):
		"""
		@brief Crée le service de conversion utilisé par chaque test.
		"""
		self.input_service = MetadataInputService()

	def test_create_metadata_cleans_and_converts_texts(self):
		"""
		@brief Nettoie les textes et convertit les valeurs numériques.
		"""
		metadata = self.input_service.create_metadata(
			title_text="  New title  ",
			artist_text=" New artist ",
			album_title_text=" New album ",
			track_number_text=" 7 ",
			year_text=" 2026 ",
		)

		self.assertIsInstance(metadata, Metadata)
		self.assertEqual(metadata.title, "New title")
		self.assertEqual(metadata.artist, "New artist")
		self.assertEqual(metadata.album_title, "New album")
		self.assertEqual(metadata.track_number, 7)
		self.assertEqual(metadata.year, 2026)

	def test_empty_texts_become_none(self):
		"""
		@brief Transforme les champs absents ou vides en None.
		"""
		metadata = self.input_service.create_metadata(
			title_text="   ",
			artist_text="",
			album_title_text=None,
			track_number_text=" ",
			year_text=None,
		)

		self.assertIsNone(metadata.title)
		self.assertIsNone(metadata.artist)
		self.assertIsNone(metadata.album_title)
		self.assertIsNone(metadata.track_number)
		self.assertIsNone(metadata.year)

	def test_invalid_integer_text_is_rejected(self):
		"""
		@brief Rejette un numéro de piste ou une année non entière.
		"""
		invalid_values = ["abc", "12.5"]

		for invalid_value in invalid_values:
			with self.subTest(value=invalid_value):
				with self.assertRaises(ValueError):
					self.input_service.create_metadata(
						track_number_text=invalid_value,
					)

	def test_non_positive_integer_is_rejected(self):
		"""
		@brief Rejette les valeurs numériques nulles ou négatives.
		"""
		invalid_values = ["0", "-1"]

		for invalid_value in invalid_values:
			with self.subTest(value=invalid_value):
				with self.assertRaises(ValueError):
					self.input_service.create_metadata(
						year_text=invalid_value,
					)

	def test_non_string_input_is_rejected(self):
		"""
		@brief Rejette une valeur déjà convertie par une interface.
		"""
		with self.assertRaises(ValueError):
			self.input_service.create_metadata(track_number_text=4)


if __name__ == "__main__":
	unittest.main(verbosity=2)
