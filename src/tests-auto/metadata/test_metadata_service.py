import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.metadata import Metadata
from library.models.track import AudioFormat, Track
from library.services.file.filter.file_filtrer import FileFiltrer
from library.services.metadata.metadata_service import MetadataService


AUDIO_DIRECTORY = Path(__file__).resolve().parents[1] / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"


class MetadataServiceIntegrationTests(unittest.TestCase):
	"""
	@brief Vérifie le service avec de vrais fichiers audio locaux.
	"""

	def setUp(self):
		"""
		@brief Crée le service utilisé par chaque test.
		"""
		self.metadata_service = MetadataService()
		self.updated_metadata = Metadata(
			title="Service test title",
			artist="Service test artist",
			album_title="Service test album",
			track_number=9,
			year=2026,
		)

	def display_metadata(self, file_path, metadata):
		"""
		@brief Affiche temporairement les métadonnées lues pendant les tests.

		@param file_path Chemin du fichier testé.
		@type file_path pathlib.Path
		@param metadata Métadonnées extraites du fichier.
		@type metadata Metadata
		"""
		print(f"\nMétadonnées de {file_path.name} :")
		print(f"  Titre            : {metadata.title}")
		print(f"  Artiste          : {metadata.artist}")
		print(f"  Album            : {metadata.album_title}")
		print(f"  Numéro de piste  : {metadata.track_number}")
		print(f"  Année            : {metadata.year}")

	def assert_metadata_was_extracted(self, metadata):
		"""
		@brief Vérifie les types, même si les tags sont absents.

		@param metadata Métadonnées renvoyées par le service.
		@type metadata Metadata
		"""
		self.assertIsInstance(metadata, Metadata)
		self.assertTrue(metadata.title is None or isinstance(metadata.title, str))
		self.assertTrue(metadata.artist is None or isinstance(metadata.artist, str))
		self.assertTrue(
			metadata.album_title is None
			or isinstance(metadata.album_title, str)
		)
		self.assertTrue(
			metadata.track_number is None
			or isinstance(metadata.track_number, int)
		)
		self.assertTrue(metadata.year is None or isinstance(metadata.year, int))

	def assert_updated_metadata(self, metadata):
		"""
		@brief Vérifie les tags sauvegardés par MetadataService.
		"""
		self.assertEqual(metadata.title, self.updated_metadata.title)
		self.assertEqual(metadata.artist, self.updated_metadata.artist)
		self.assertEqual(metadata.album_title, self.updated_metadata.album_title)
		self.assertEqual(
			metadata.track_number,
			self.updated_metadata.track_number,
		)
		self.assertEqual(metadata.year, self.updated_metadata.year)

	def create_temporary_copy(self, source_file, directory):
		"""
		@brief Crée une copie temporaire d'un fichier audio.
		"""
		copied_file = Path(directory) / f"service_{source_file.name}"
		shutil.copy2(source_file, copied_file)
		return copied_file

	@unittest.skipUnless(MP3_FILE.is_file(), "Ajouter sample.mp3.")
	def test_read_real_mp3_metadata(self):
		"""
		@brief Valide puis lit les métadonnées d'un vrai fichier MP3.
		"""
		self.assertTrue(FileFiltrer.is_mp3_file(MP3_FILE))
		metadata = self.metadata_service.read_metadata(MP3_FILE)
		self.display_metadata(MP3_FILE, metadata)
		self.assert_metadata_was_extracted(metadata)

	@unittest.skipUnless(FLAC_FILE.is_file(), "Ajouter sample.flac.")
	def test_read_real_flac_metadata(self):
		"""
		@brief Valide puis lit les métadonnées d'un vrai fichier FLAC.
		"""
		self.assertTrue(FileFiltrer.is_flac_file(FLAC_FILE))
		metadata = self.metadata_service.read_metadata(FLAC_FILE)
		self.display_metadata(FLAC_FILE, metadata)
		self.assert_metadata_was_extracted(metadata)

	@unittest.skipUnless(MP3_FILE.is_file(), "Ajouter sample.mp3.")
	def test_update_mp3_metadata_via_service(self):
		"""
		@brief Modifie tous les tags d'une copie MP3 via le service.
		"""
		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_copy(MP3_FILE, directory)
			saved_metadata = self.metadata_service.update_metadata(
				copied_file,
				self.updated_metadata,
			)
			self.assert_updated_metadata(saved_metadata)

	@unittest.skipUnless(FLAC_FILE.is_file(), "Ajouter sample.flac.")
	def test_update_flac_metadata_via_service(self):
		"""
		@brief Modifie tous les tags d'une copie FLAC via le service.
		"""
		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_copy(FLAC_FILE, directory)
			saved_metadata = self.metadata_service.update_metadata(
				copied_file,
				self.updated_metadata,
			)
			self.assert_updated_metadata(saved_metadata)

	@unittest.skipUnless(MP3_FILE.is_file(), "Ajouter sample.mp3.")
	def test_read_mp3_track_with_duration(self):
		"""
		@brief Construit un Track MP3 avec une durée positive.
		"""
		with patch.object(
			self.metadata_service,
			"read_metadata",
			wraps=self.metadata_service.read_metadata,
		) as read_metadata:
			track = self.metadata_service.read_track(MP3_FILE)

		read_metadata.assert_called_once_with(MP3_FILE, AudioFormat.MP3)
		self.assertIsInstance(track, Track)
		self.assertEqual(track.file_path, MP3_FILE)
		self.assertEqual(track.format, AudioFormat.MP3)
		duration_seconds = track.duration_seconds
		self.assertIsNotNone(duration_seconds)
		if duration_seconds is not None:
			self.assertGreater(duration_seconds, 0)
		self.assertIsInstance(track.metadata, Metadata)

	@unittest.skipUnless(FLAC_FILE.is_file(), "Ajouter sample.flac.")
	def test_read_flac_track_with_duration(self):
		"""
		@brief Construit un Track FLAC avec une durée positive.
		"""
		track = self.metadata_service.read_track(FLAC_FILE)
		self.assertIsInstance(track, Track)
		self.assertEqual(track.file_path, FLAC_FILE)
		self.assertEqual(track.format, AudioFormat.FLAC)
		duration_seconds = track.duration_seconds
		self.assertIsNotNone(duration_seconds)
		if duration_seconds is not None:
			self.assertGreater(duration_seconds, 0)
		self.assertIsInstance(track.metadata, Metadata)


if __name__ == "__main__":
	unittest.main(verbosity=2)
