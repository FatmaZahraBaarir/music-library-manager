import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


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
		self.pause_calls = 0
		self.resume_calls = 0
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

	def pause_playback(self):
		"""@brief Enregistre la mise en pause demandée par le CLI."""
		self.pause_calls += 1

	def resume_playback(self):
		"""@brief Enregistre la reprise demandée par le CLI."""
		self.resume_calls += 1


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

	def test_q_stops_playback_without_keyboard_interrupt(self):
		"""@brief La touche q arrête le morceau sans utiliser Ctrl+C."""
		service = FakeAudioLibraryService(playback_states=[True])
		stdout = io.StringIO()

		with patch("cli.main.read_command", return_value="q"), \
				redirect_stdout(stdout):
			result = main(["-p", "music.mp3"], library_service=service)

		self.assertEqual(result, 0)
		self.assertTrue(service.stop_called)
		self.assertEqual(service.state_checks, 1)
		self.assertIn("q puis Entrée pour arrêter", stdout.getvalue())
		self.assertIn("Lecture arrêtée", stdout.getvalue())

	def test_k_pauses_then_resumes_playback(self):
		"""@brief Deux pressions sur k mettent en pause puis reprennent le morceau."""
		service = FakeAudioLibraryService(playback_states=[True, False])
		stdout = io.StringIO()

		with patch("cli.main.read_command", side_effect=["k", "k"]), \
				redirect_stdout(stdout):
			result = main(["-p", "music.mp3"], library_service=service)

		output = stdout.getvalue()
		self.assertEqual(result, 0)
		self.assertEqual(service.pause_calls, 1)
		self.assertEqual(service.resume_calls, 1)
		self.assertFalse(service.stop_called)
		self.assertIn("Lecture en pause", output)
		self.assertIn("Lecture reprise", output)

	def test_q_stops_playback_while_paused(self):
		"""@brief La touche q reste utilisable après une mise en pause."""
		service = FakeAudioLibraryService(playback_states=[True])
		stdout = io.StringIO()

		with patch("cli.main.read_command", side_effect=["k", "q"]), \
				redirect_stdout(stdout):
			result = main(["-p", "music.mp3"], library_service=service)

		self.assertEqual(result, 0)
		self.assertEqual(service.pause_calls, 1)
		self.assertTrue(service.stop_called)
		self.assertIn("Lecture arrêtée", stdout.getvalue())


if __name__ == "__main__":
	unittest.main(verbosity=2)
