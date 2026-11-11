import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.interfaces.library_interface import LibraryInterface
from library.models.metadata import Metadata
from library.models.track import AudioFormat, Track
from library.services.library_service import LibraryService


AUDIO_DIRECTORY = Path(__file__).resolve().parents[1] / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"


class FakeFileService:
	"""
	@brief Simule FileService pour vérifier la délégation de la façade.
	"""

	def __init__(self, audio_files=None):
		self.audio_files = [] if audio_files is None else audio_files
		self.received_directory = None

	def find_audio_files(self, directory_path):
		self.received_directory = directory_path
		return self.audio_files


class FakeMetadataService:
	"""
	@brief Simule MetadataService pour vérifier la délégation de la façade.
	"""

	def __init__(self):
		self.read_metadata_result = Metadata(title="Read result")
		self.update_metadata_result = Metadata(title="Update result")
		self.received_read_path = None
		self.received_update = None
		self.received_track_paths = []

	def read_metadata(self, file_path):
		self.received_read_path = file_path
		return self.read_metadata_result

	def update_metadata(self, file_path, metadata):
		self.received_update = (file_path, metadata)
		return self.update_metadata_result

	def read_track(self, file_path):
		self.received_track_paths.append(file_path)
		return Track(file_path, AudioFormat.MP3)


class LibraryServiceTests(unittest.TestCase):
	"""
	@brief Vérifie le point d'entrée commun destiné au CLI et à la GUI.
	"""

	def setUp(self):
		"""
		@brief Crée la façade avec des services simulés.
		"""
		self.audio_files = [Path("first.mp3"), Path("second.mp3")]
		self.file_service = FakeFileService(self.audio_files)
		self.metadata_service = FakeMetadataService()
		self.library_service = LibraryService(
			file_service=self.file_service,
			metadata_service=self.metadata_service,
		)

	def test_library_service_implements_interface(self):
		"""
		@brief Vérifie que la façade respecte LibraryInterface.
		"""
		self.assertIsInstance(self.library_service, LibraryInterface)

	def test_find_audio_files_delegates_to_file_service(self):
		"""
		@brief Vérifie la délégation de l'exploration.
		"""
		directory = Path("music")
		result = self.library_service.find_audio_files(directory)

		self.assertEqual(result, self.audio_files)
		self.assertEqual(self.file_service.received_directory, directory)

	def test_read_metadata_delegates_to_metadata_service(self):
		"""
		@brief Vérifie la délégation de la lecture des métadonnées.
		"""
		file_path = Path("music.mp3")
		result = self.library_service.read_metadata(file_path)

		self.assertIs(result, self.metadata_service.read_metadata_result)
		self.assertEqual(self.metadata_service.received_read_path, file_path)

	def test_update_metadata_delegates_to_metadata_service(self):
		"""
		@brief Vérifie la délégation de la modification des métadonnées.
		"""
		file_path = Path("music.mp3")
		metadata = Metadata(title="New title")
		result = self.library_service.update_metadata(file_path, metadata)

		self.assertIs(result, self.metadata_service.update_metadata_result)
		self.assertEqual(
			self.metadata_service.received_update,
			(file_path, metadata),
		)

	def test_update_metadata_from_text_converts_before_delegation(self):
		"""
		@brief Vérifie la conversion des textes avant la modification.
		"""
		file_path = Path("music.mp3")
		result = self.library_service.update_metadata_from_text(
			file_path=file_path,
			title_text="  New title  ",
			artist_text=" New artist ",
			album_title_text=" New album ",
			track_number_text=" 4 ",
			year_text=" 2026 ",
		)

		received_update = self.metadata_service.received_update
		self.assertIsNotNone(received_update)
		if received_update is None:
			self.fail("La modification n'a pas été déléguée.")
		received_path, received_metadata = received_update
		self.assertIs(result, self.metadata_service.update_metadata_result)
		self.assertEqual(received_path, file_path)
		self.assertEqual(received_metadata.title, "New title")
		self.assertEqual(received_metadata.artist, "New artist")
		self.assertEqual(received_metadata.album_title, "New album")
		self.assertEqual(received_metadata.track_number, 4)
		self.assertEqual(received_metadata.year, 2026)

	def test_scan_library_builds_all_tracks(self):
		"""
		@brief Vérifie l'enchaînement exploration puis construction des morceaux.
		"""
		tracks = self.library_service.scan_library(Path("music"))

		self.assertEqual(len(tracks), len(self.audio_files))
		self.assertEqual(
			self.metadata_service.received_track_paths,
			self.audio_files,
		)
		self.assertTrue(all(isinstance(track, Track) for track in tracks))

	@unittest.skipUnless(
		MP3_FILE.is_file() and FLAC_FILE.is_file(),
		"Ajouter sample.mp3 et sample.flac pour activer ce test.",
	)
	def test_update_real_files_from_text(self):
		"""
		@brief Modifie des copies MP3 et FLAC depuis des chaînes brutes.
		"""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			files_to_test = [MP3_FILE, FLAC_FILE]

			for source_file in files_to_test:
				with self.subTest(extension=source_file.suffix):
					copied_file = root / source_file.name
					shutil.copy2(source_file, copied_file)
					saved_metadata = LibraryService().update_metadata_from_text(
						file_path=copied_file,
						title_text="  Interface title  ",
						artist_text=" Interface artist ",
						album_title_text=" Interface album ",
						track_number_text=" 8 ",
						year_text=" 2026 ",
					)

					self.assertEqual(saved_metadata.title, "Interface title")
					self.assertEqual(saved_metadata.artist, "Interface artist")
					self.assertEqual(saved_metadata.album_title, "Interface album")
					self.assertEqual(saved_metadata.track_number, 8)
					self.assertEqual(saved_metadata.year, 2026)

	@unittest.skipUnless(
		MP3_FILE.is_file() and FLAC_FILE.is_file(),
		"Ajouter sample.mp3 et sample.flac pour activer ce test.",
	)
	def test_scan_real_mp3_and_flac_files(self):
		"""
		@brief Vérifie le point d'entrée complet avec de vrais fichiers audio.
		"""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			nested_directory = root / "nested"
			nested_directory.mkdir()
			mp3_copy = root / "first.mp3"
			flac_copy = nested_directory / "second.flac"
			shutil.copy2(MP3_FILE, mp3_copy)
			shutil.copy2(FLAC_FILE, flac_copy)

			tracks = LibraryService().scan_library(root)

			self.assertEqual(len(tracks), 2)
			self.assertEqual(
				{track.file_path for track in tracks},
				{mp3_copy, flac_copy},
			)
			self.assertEqual(
				{track.format for track in tracks},
				{AudioFormat.MP3, AudioFormat.FLAC},
			)
			self.assertTrue(
				all(track.duration_seconds is not None for track in tracks)
			)


if __name__ == "__main__":
	unittest.main(verbosity=2)
