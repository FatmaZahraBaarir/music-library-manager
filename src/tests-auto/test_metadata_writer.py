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


@unittest.skipUnless(
	MP3_FILE.is_file(),
	"Ajouter src/tests-auto/fixtures/audio/sample.mp3 pour activer ces tests.",
)
class MetadataWriterIntegrationTests(unittest.TestCase):
	"""
	@brief Vérifie l'écriture des tags sur des copies temporaires du MP3.
	"""

	def setUp(self):
		"""
		@brief Crée le reader et le writer utilisés par chaque test.
		"""
		self.metadata_reader = MetadataReader()
		self.metadata_writer = MetadataWriter()

	def create_temporary_mp3_copy(self, directory):
		"""
		@brief Copie le MP3 de référence dans un dossier temporaire.

		@param directory Dossier temporaire de destination.
		@type directory str
		@return Chemin de la copie.
		@rtype pathlib.Path
		"""
		copied_file = Path(directory) / "copied_sample.mp3"
		shutil.copy2(MP3_FILE, copied_file)
		return copied_file

	def test_write_mp3_title_on_copy(self):
		"""
		@brief Modifie le titre d'une copie puis vérifie sa sauvegarde.
		"""
		original_title = self.metadata_reader.read_mp3(MP3_FILE).title
		expected_title = "Test title written by MetadataWriter"

		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_mp3_copy(directory)
			new_metadata = Metadata(title=expected_title)

			self.metadata_writer.write_mp3(copied_file, new_metadata)
			saved_metadata = self.metadata_reader.read_mp3(copied_file)

			print("\nModification temporaire du MP3 :")
			print(f"  Ancien titre : {original_title}")
			print(f"  Nouveau titre : {saved_metadata.title}")
			self.assertEqual(saved_metadata.title, expected_title)

		unchanged_original_title = self.metadata_reader.read_mp3(MP3_FILE).title
		self.assertEqual(unchanged_original_title, original_title)

	def test_none_keeps_existing_mp3_title(self):
		"""
		@brief Vérifie que title=None ne supprime pas le titre existant.
		"""
		with tempfile.TemporaryDirectory() as directory:
			copied_file = self.create_temporary_mp3_copy(directory)
			title_before_update = self.metadata_reader.read_mp3(copied_file).title

			self.metadata_writer.write_mp3(copied_file, Metadata(title=None))
			title_after_update = self.metadata_reader.read_mp3(copied_file).title

			self.assertEqual(title_after_update, title_before_update)


if __name__ == "__main__":
	unittest.main(verbosity=2)
