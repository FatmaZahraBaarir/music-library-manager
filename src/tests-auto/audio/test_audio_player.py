import os
import sys
import unittest
from pathlib import Path

# Le pilote factice vérifie le décodage sans produire de son pendant les tests.
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

import pygame

from library.services.audio.player.audio_player import AudioPlayer


AUDIO_DIRECTORY = Path(__file__).parents[1] / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"


class AudioPlayerIntegrationTests(unittest.TestCase):
	"""
	@brief Vérifie le lecteur pygame avec de vrais fichiers MP3 et FLAC.
	"""

	def tearDown(self):
		"""Libère le mixer après chaque test."""
		if pygame.mixer.get_init() is not None:
			pygame.mixer.music.stop()
			pygame.mixer.quit()

	@unittest.skipUnless(
		MP3_FILE.is_file() and FLAC_FILE.is_file(),
		"Ajouter sample.mp3 et sample.flac pour activer ce test.",
	)
	def test_load_and_play_mp3_and_flac(self):
		"""Charge et démarre réellement le décodage des deux formats."""
		for audio_file in [MP3_FILE, FLAC_FILE]:
			with self.subTest(extension=audio_file.suffix):
				player = AudioPlayer()
				player.load(audio_file)
				player.play()
				player.pause()
				player.resume()
				player.stop()

				self.assertEqual(player.loaded_file, audio_file)

	def test_missing_file_is_rejected(self):
		"""Refuse le chargement d'un fichier inexistant."""
		player = AudioPlayer()
		with self.assertRaises(ValueError):
			player.load(AUDIO_DIRECTORY / "missing.mp3")

	def test_play_without_loaded_file_is_rejected(self):
		"""Refuse la lecture lorsqu'aucun fichier n'a été chargé."""
		player = AudioPlayer()
		with self.assertRaises(ValueError):
			player.play()


if __name__ == "__main__":
	unittest.main(verbosity=2)
