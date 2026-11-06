import sys
import unittest
from pathlib import Path

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[1]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.metadata import Metadata
from library.services.file.filter.file_filtrer import FileFiltrer
from library.services.metadata.metadata_service import MetadataService


AUDIO_DIRECTORY = Path(__file__).parent / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"


class MetadataServiceIntegrationTests(unittest.TestCase):
	"""
	@brief Vérifie le service avec de vrais fichiers audio locaux.

	Les tests sont ignorés tant que les fichiers sample.mp3 et sample.flac
	ne sont pas présents dans le dossier fixtures/audio.
	"""

	def setUp(self):
		"""
		@brief Crée le service utilisé par chaque test.
		"""
		self.metadata_service = MetadataService()

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
		@brief Vérifie le type des métadonnées, même si les tags sont absents.

		Un fichier audio valide peut ne contenir aucun tag descriptif. Dans ce
		cas, les attributs correspondants doivent valoir None.

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

	@unittest.skipUnless(
		MP3_FILE.is_file(),
		"Ajouter src/tests-auto/fixtures/audio/sample.mp3 pour activer ce test.",
	)
	def test_read_real_mp3_metadata(self):
		"""
		@brief Valide puis lit les métadonnées d'un vrai fichier MP3.
		"""
		self.assertTrue(FileFiltrer.is_mp3_file(MP3_FILE))

		metadata = self.metadata_service.read_metadata(MP3_FILE)

		self.display_metadata(MP3_FILE, metadata)
		self.assert_metadata_was_extracted(metadata)

	@unittest.skipUnless(
		FLAC_FILE.is_file(),
		"Ajouter src/tests-auto/fixtures/audio/sample.flac pour activer ce test.",
	)
	def test_read_real_flac_metadata(self):
		"""
		@brief Valide puis lit les métadonnées d'un vrai fichier FLAC.
		"""
		self.assertTrue(FileFiltrer.is_flac_file(FLAC_FILE))

		metadata = self.metadata_service.read_metadata(FLAC_FILE)

		self.display_metadata(FLAC_FILE, metadata)
		self.assert_metadata_was_extracted(metadata)


if __name__ == "__main__":
	unittest.main(verbosity=2)
