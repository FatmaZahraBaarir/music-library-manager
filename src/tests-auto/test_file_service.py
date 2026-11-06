import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[1]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.services.file.file_service import FileService


AUDIO_DIRECTORY = Path(__file__).parent / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"


class FileServiceIntegrationTests(unittest.TestCase):
	"""
	@brief Vérifie l'exploration récursive et le filtrage des fichiers audio.
	"""

	@unittest.skipUnless(
		MP3_FILE.is_file() and FLAC_FILE.is_file(),
		"Ajouter sample.mp3 et sample.flac pour activer ce test.",
	)
	def test_find_audio_files_recursively(self):
		"""
		@brief Conserve uniquement les vrais MP3 et FLAC de l'arborescence.
		"""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			first_level = root / "first_level"
			second_level = first_level / "second_level"
			second_level.mkdir(parents=True)

			mp3_copy = root / "music.MP3"
			flac_copy = second_level / "music.FLAC"
			shutil.copy2(MP3_FILE, mp3_copy)
			shutil.copy2(FLAC_FILE, flac_copy)

			(root / "notes.txt").write_text(
				"Ce fichier n'est pas un fichier audio.",
				encoding="utf-8",
			)
			(first_level / "fake.mp3").write_text(
				"Ce texte possède une fausse extension MP3.",
				encoding="utf-8",
			)
			shutil.copy2(MP3_FILE, first_level / "wrong_extension.flac")

			result = FileService.find_audio_files(root)
			expected = sorted(
				[mp3_copy, flac_copy],
				key=lambda path: str(path).lower(),
			)

			self.assertEqual(result, expected)
			self.assertTrue(all(isinstance(path, Path) for path in result))

	def test_empty_directory_returns_empty_list(self):
		"""
		@brief Vérifie qu'un dossier vide produit une liste vide.
		"""
		with tempfile.TemporaryDirectory() as directory:
			self.assertEqual(FileService.find_audio_files(directory), [])

	def test_missing_directory_is_rejected(self):
		"""
		@brief Vérifie le rejet d'un dossier inexistant.
		"""
		with tempfile.TemporaryDirectory() as directory:
			missing_directory = Path(directory) / "missing"
			with self.assertRaises(ValueError):
				FileService.find_audio_files(missing_directory)

	def test_file_path_is_rejected(self):
		"""
		@brief Vérifie qu'un chemin de fichier n'est pas traité comme un dossier.
		"""
		with tempfile.TemporaryDirectory() as directory:
			file_path = Path(directory) / "file.txt"
			file_path.write_text("test", encoding="utf-8")

			with self.assertRaises(ValueError):
				FileService.find_audio_files(file_path)


if __name__ == "__main__":
	unittest.main(verbosity=2)
