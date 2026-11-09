import sys
import unittest
from pathlib import Path

# Rend le package library accessible, même sans définir PYTHONPATH.
SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.playlist import Playlist
from library.models.track import AudioFormat, Track
from library.services.audio.audio_service import AudioService


class FakeAudioPlayer:
	"""
	@brief Simule le lecteur technique sans produire de son.
	"""

	def __init__(self):
		self.loaded_files = []
		self.play_count = 0
		self.pause_count = 0
		self.resume_count = 0
		self.stop_count = 0
		self.playing = False

	def load(self, file_path):
		self.loaded_files.append(Path(file_path))

	def play(self):
		self.play_count += 1
		self.playing = True

	def pause(self):
		self.pause_count += 1

	def resume(self):
		self.resume_count += 1

	def stop(self):
		self.stop_count += 1
		self.playing = False

	def is_playing(self):
		return self.playing

	def finish_track(self):
		self.playing = False


class AudioServiceTests(unittest.TestCase):
	"""
	@brief Vérifie l'orchestration audio avec un faux lecteur.
	"""

	def setUp(self):
		"""Crée un service audio sans sortie sonore."""
		self.audio_player = FakeAudioPlayer()
		self.audio_service = AudioService(self.audio_player)
		self.first_track = Track(Path("first.mp3"), AudioFormat.MP3)
		self.second_track = Track(Path("second.flac"), AudioFormat.FLAC)

	def tearDown(self):
		"""Arrête la lecture après chaque test."""
		self.audio_service.stop_playback()

	def test_play_track_loads_and_starts_file(self):
		"""Vérifie le chargement et la lecture d'un morceau."""
		result = self.audio_service.play_track(self.first_track)

		self.assertIs(result, self.first_track)
		self.assertEqual(self.audio_player.loaded_files, [Path("first.mp3")])
		self.assertEqual(self.audio_player.play_count, 1)
		self.assertIs(self.audio_service.current_track, self.first_track)
		self.assertTrue(self.audio_service.is_playing())

	def test_pause_and_resume_playback(self):
		"""Vérifie la pause puis la reprise de la lecture."""
		self.audio_service.play_track(self.first_track)

		self.audio_service.pause_playback()
		self.assertEqual(self.audio_player.pause_count, 1)
		self.assertTrue(self.audio_service.is_paused)
		self.assertFalse(self.audio_service.is_playing())

		self.audio_service.resume_playback()
		self.assertEqual(self.audio_player.resume_count, 1)
		self.assertFalse(self.audio_service.is_paused)
		self.assertTrue(self.audio_service.is_playing())

	def test_stop_playback_clears_current_track(self):
		"""Vérifie l'arrêt et la remise à zéro du service."""
		self.audio_service.play_track(self.first_track)
		self.audio_service.stop_playback()

		self.assertIsNone(self.audio_service.current_track)
		self.assertIsNone(self.audio_service.current_playlist)
		self.assertFalse(self.audio_service.is_paused)
		self.assertFalse(self.audio_service.is_playing())

	def test_pause_without_track_is_rejected(self):
		"""Vérifie qu'une pause sans lecture produit une erreur fonctionnelle."""
		with self.assertRaises(ValueError):
			self.audio_service.pause_playback()

	def test_empty_playlist_is_rejected(self):
		"""Vérifie qu'une playlist vide ne peut pas être lue."""
		with self.assertRaises(ValueError):
			self.audio_service.play_playlist(Playlist("Empty"))

	def test_playlist_plays_tracks_in_order(self):
		"""Vérifie le passage au morceau suivant dans le thread appelant."""
		playlist = Playlist(
			"Test playlist",
			tracks=[self.first_track, self.second_track],
		)
		self.audio_service.play_playlist(playlist)
		self.audio_player.finish_track()

		second_track = self.audio_service.update_playlist_playback()
		self.assertIs(second_track, self.second_track)
		self.assertEqual(
			self.audio_player.loaded_files,
			[Path("first.mp3"), Path("second.flac")],
		)
		self.assertIs(self.audio_service.current_track, self.second_track)

		self.audio_player.finish_track()
		finished_track = self.audio_service.update_playlist_playback()
		self.assertIsNone(finished_track)
		self.assertIsNone(self.audio_service.current_track)
		self.assertIsNone(self.audio_service.current_playlist)


if __name__ == "__main__":
	unittest.main(verbosity=2)
