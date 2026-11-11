import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from cli.main import main


class FakeAudioLibraryService:
	"""@brief Simule la lecture audio utilisée par le CLI."""

	def __init__(self, playback_states=None, interrupt=False):
		self.received_file = None
		self.playback_states = iter(playback_states or [False])
		self.interrupt = interrupt
		self.stop_called = False
		self.state_checks = 0

	def play_track(self, file_path):
		"""@brief Enregistre le fichier dont la lecture est demandée."""
		self.received_file = file_path

	def is_playing(self):
		"""@brief Retourne les états successifs de lecture."""
		self.state_checks += 1
		if self.interrupt:
			raise KeyboardInterrupt
		return next(self.playback_states)

	def stop_playback(self):
		"""@brief Enregistre l'arrêt demandé par le CLI."""
		self.stop_called = True


class CliPlayTests(unittest.TestCase):
	"""@brief Teste le branchement de l'option -p au service audio existant."""

	def test_play_starts_track_and_waits_until_it_finishes(self):
		"""@brief Démarre le morceau et garde le CLI actif pendant la lecture."""
		service = FakeAudioLibraryService(playback_states=[True, False])
		stdout = io.StringIO()

		with redirect_stdout(stdout):
			result = main(["-p", "music.mp3"], library_service=service)

		self.assertEqual(result, 0)
		self.assertEqual(service.received_file, "music.mp3")
		self.assertEqual(service.state_checks, 2)
		self.assertIn("Lecture terminée", stdout.getvalue())

	def test_keyboard_interrupt_stops_playback_cleanly(self):
		"""@brief Ctrl+C arrête le lecteur sans afficher de traceback."""
		service = FakeAudioLibraryService(interrupt=True)
		stdout = io.StringIO()

		with redirect_stdout(stdout):
			result = main(["-p", "music.mp3"], library_service=service)

		self.assertEqual(result, 0)
		self.assertTrue(service.stop_called)
		self.assertIn("Lecture arrêtée", stdout.getvalue())


if __name__ == "__main__":
	unittest.main(verbosity=2)
