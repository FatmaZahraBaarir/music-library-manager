import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[1]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.metadata import Metadata
from library.services.metadata.reader.metadata_reader import MetadataReader
from library.services.metadata.writer.metadata_writer import MetadataWriter


AUDIO_DIRECTORY = Path(__file__).parent / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"


class MetadataWriterIntegrationTests(unittest.TestCase):
	"""
	@brief Vérifie l'écriture des tags sur des copies temporaires.
	"""

	def setUp(self):
		"""
		@brief Crée le reader et le writer utilisés par chaque test.
		"""
		self.metadata_reader = MetadataReader()
		self.metadata_writer = MetadataWriter()
		self.expected_metadata = Metadata(
			title="Test title",
			artist="Test artist",
			album_title="Test album",
			track_number=7,
			year=2026,
		)

	def create_temporary_copy(self, source_file, directory):
		"""
		@brief Copie un fichier audio dans un dossier temporaire.

		@param source_file Fichier audio de référence.
		@type source_file pathlib.Path
		@param directory Dossier temporaire de destination.
		@type directory str
		@return Chemin de la copie.
		@rtype pathlib.Path
		"""
		copied_file = Path(directory) / f"copied_{source_file.name}"
		shutil.copy2(source_file, copied_file)
		return copied_file

	def assert_expected_metadata(self, metadata):
		"""
		@brief Vérifie que tous les tags de test ont été sauvegardés.

		@param metadata Métadonnées relues après sauvegarde.
		@type metadata Metadata
		"""
		self.assertEqual(metadata.title, self.expected_metadata.title)
		self.assertEqual(metadata.artist, self.expected_metadata.artist)
		self.assertEqual(metadata.album_title, self.expected_metadata.album_title)
		self.assertEqual(
			metadata.track_number,
			self.expected_metadata.track_number,
		)
		self.assertEqual(metadata.year, self.expected_metadata.year)

	@unittest.skipUnless(
		MP3_FILE.is_file(),
		"Ajouter sample.mp3 pour activer ce test.",
	)
	def test_write_all_mp3_tags_on_copy(self):
		"""
		@brief Modifie tous les tags d'une copie MP3 puis les relit.
		"""
		original_metadata = self.metadata_reader.read_mp3(MP3_FILE)

		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_copy(MP3_FILE, directory)
			self.metadata_writer.write_mp3(
				copied_file,
				self.expected_metadata,
			)
			saved_metadata = self.metadata_reader.read_mp3(copied_file)

			print("\nTags MP3 sauvegardés sur la copie :")
			print(f"  Titre   : {saved_metadata.title}")
			print(f"  Artiste : {saved_metadata.artist}")
			print(f"  Album   : {saved_metadata.album_title}")
			print(f"  Piste   : {saved_metadata.track_number}")
			print(f"  Année   : {saved_metadata.year}")
			self.assert_expected_metadata(saved_metadata)

		unchanged_metadata = self.metadata_reader.read_mp3(MP3_FILE)
		self.assertEqual(unchanged_metadata.title, original_metadata.title)
		self.assertEqual(unchanged_metadata.artist, original_metadata.artist)

	@unittest.skipUnless(
		FLAC_FILE.is_file(),
		"Ajouter sample.flac pour activer ce test.",
	)
	def test_write_all_flac_tags_on_copy(self):
		"""
		@brief Modifie tous les tags d'une copie FLAC puis les relit.
		"""
		original_metadata = self.metadata_reader.read_flac(FLAC_FILE)

		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_copy(FLAC_FILE, directory)
			self.metadata_writer.write_flac(
				copied_file,
				self.expected_metadata,
			)
			saved_metadata = self.metadata_reader.read_flac(copied_file)

			print("\nTags FLAC sauvegardés sur la copie :")
			print(f"  Titre   : {saved_metadata.title}")
			print(f"  Artiste : {saved_metadata.artist}")
			print(f"  Album   : {saved_metadata.album_title}")
			print(f"  Piste   : {saved_metadata.track_number}")
			print(f"  Année   : {saved_metadata.year}")
			self.assert_expected_metadata(saved_metadata)

		unchanged_metadata = self.metadata_reader.read_flac(FLAC_FILE)
		self.assertEqual(unchanged_metadata.title, original_metadata.title)
		self.assertEqual(unchanged_metadata.artist, original_metadata.artist)

	@unittest.skipUnless(
		MP3_FILE.is_file(),
		"Ajouter sample.mp3 pour activer ce test.",
	)
	def test_none_keeps_existing_mp3_title(self):
		"""
		@brief Vérifie que title=None ne supprime pas le titre existant.
		"""
		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_copy(MP3_FILE, directory)
			title_before_update = self.metadata_reader.read_mp3(copied_file).title

			self.metadata_writer.write_mp3(copied_file, Metadata(title=None))
			title_after_update = self.metadata_reader.read_mp3(copied_file).title

			self.assertEqual(title_after_update, title_before_update)


if __name__ == "__main__":
	unittest.main(verbosity=2)
