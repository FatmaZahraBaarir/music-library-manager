import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from cli.main import parse_arguments


class CliArgumentsTests(unittest.TestCase):
	"""@brief Teste les options et les erreurs de la ligne de commande."""

	def test_short_options(self):
		"""@brief Vérifie les lettres demandées par le sujet."""
		file_args = parse_arguments(["-f", "music.mp3"])
		directory_args = parse_arguments([
			"-d",
			"music",
			"-o",
			"playlist.xspf",
		])
		play_args = parse_arguments(["-p", "music.mp3"])

		self.assertEqual(file_args.file, "music.mp3")
		self.assertEqual(directory_args.directory, "music")
		self.assertEqual(directory_args.output, "playlist.xspf")
		self.assertEqual(play_args.play, "music.mp3")

	def test_long_options(self):
		"""@brief Vérifie les noms longs ajoutés en complément."""
		args = parse_arguments([
			"--directory",
			"music",
			"--output",
			"playlist.xspf",
		])

		self.assertEqual(args.directory, "music")
		self.assertEqual(args.output, "playlist.xspf")

	def test_file_and_directory_are_mutually_exclusive(self):
		"""@brief Vérifie que -f et -d ne peuvent pas être utilisés ensemble."""
		with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
			parse_arguments(["-f", "music.mp3", "-d", "music"])

		self.assertEqual(error.exception.code, 2)

	def test_missing_argument_displays_functional_error(self):
		"""@brief Vérifie le message demandé lorsqu'aucun argument n'est fourni."""
		stderr = io.StringIO()

		with redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
			parse_arguments([])

		self.assertEqual(error.exception.code, 2)
		self.assertIn("aucun argument fourni", stderr.getvalue())
		self.assertIn("-h", stderr.getvalue())

	def test_output_requires_directory(self):
		"""@brief Vérifie que -o ne peut être utilisé qu'avec -d."""
		with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
			parse_arguments(["-f", "music.mp3", "-o", "playlist.xspf"])

		self.assertEqual(error.exception.code, 2)

	def test_help_lists_expected_options(self):
		"""@brief Vérifie que -h affiche toutes les options du sujet."""
		stdout = io.StringIO()

		with redirect_stdout(stdout), self.assertRaises(SystemExit) as result:
			parse_arguments(["-h"])

		help_message = stdout.getvalue()
		self.assertEqual(result.exception.code, 0)
		for option in ("-f", "-d", "-o", "-p", "-h"):
			self.assertIn(option, help_message)


if __name__ == "__main__":
	unittest.main(verbosity=2)
