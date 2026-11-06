import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.playlist import Playlist
from library.models.track import AudioFormat, Track
from library.services.playlist.xspf_service import XSPF_TAG, XspfService


class XspfServiceTests(unittest.TestCase):
	"""Teste la sauvegarde des playlists XSPF."""

	def test_save_empty_playlist(self):
		"""Vérifie la sauvegarde d'une playlist vide."""
		with tempfile.TemporaryDirectory() as directory:
			playlist = Playlist("Ma playlist")
			output_path = Path(directory) / "playlist.xspf"

			XspfService().save_playlist(playlist, output_path)
			root = ET.parse(output_path).getroot()

			title = root.findtext(XSPF_TAG + "title")
			version = root.attrib["version"]
			track_list = root.find(XSPF_TAG + "trackList")

			print("\nPlaylist vide sauvegardée :")
			print(f"  Titre   : {title}")
			print(f"  Version : {version}")
			print(f"  Fichier : {output_path}")

			self.assertTrue(output_path.is_file())
			self.assertEqual(title, "Ma playlist")
			self.assertEqual(version, "1")
			self.assertIsNotNone(track_list)

	def test_save_playlist_with_one_track(self):
		"""Vérifie la sauvegarde d'un morceau."""
		with tempfile.TemporaryDirectory() as directory:
			music_path = Path(directory) / "music.mp3"
			track = Track(music_path, AudioFormat.MP3)
			playlist = Playlist("Ma playlist", tracks=[track])
			output_path = Path(directory) / "playlist.xspf"

			XspfService().save_playlist(playlist, output_path)
			root = ET.parse(output_path).getroot()

			location_tag = (
				XSPF_TAG + "trackList/"
				+ XSPF_TAG + "track/"
				+ XSPF_TAG + "location"
			)
			location = root.findtext(location_tag)
			expected_location = music_path.resolve().as_uri()

			print("\nMorceau sauvegardé :")
			print(f"  Chemin obtenu  : {location}")
			print(f"  Chemin attendu : {expected_location}")

			self.assertEqual(location, expected_location)

	def test_load_empty_playlist(self):
		"""Vérifie l'ouverture d'une playlist vide."""
		with tempfile.TemporaryDirectory() as directory:
			output_path = Path(directory) / "playlist.xspf"
			service = XspfService()

			service.save_playlist(Playlist("Ma playlist"), output_path)
			loaded_playlist = service.load_playlist(output_path)

			print("\nPlaylist ouverte :")
			print(f"  Titre   : {loaded_playlist.name}")
			print(f"  Fichier : {loaded_playlist.file_path}")

			self.assertEqual(loaded_playlist.name, "Ma playlist")
			self.assertEqual(loaded_playlist.file_path, output_path)
			self.assertEqual(loaded_playlist.tracks, [])

	def test_load_playlist_with_one_track(self):
		"""Vérifie la récupération d'un morceau."""
		with tempfile.TemporaryDirectory() as directory:
			music_path = Path(directory) / "music.mp3"
			track = Track(music_path, AudioFormat.MP3)
			output_path = Path(directory) / "playlist.xspf"
			service = XspfService()

			service.save_playlist(Playlist("Ma playlist", tracks=[track]), output_path)
			loaded_playlist = service.load_playlist(output_path)
			loaded_track = loaded_playlist.tracks[0]

			print("\nMorceau récupéré :")
			print(f"  Chemin : {loaded_track.file_path}")
			print(f"  Format : {loaded_track.format.value}")

			self.assertEqual(len(loaded_playlist.tracks), 1)
			self.assertEqual(loaded_track.file_path, music_path.resolve())
			self.assertEqual(loaded_track.format, AudioFormat.MP3)

	def test_load_missing_file(self):
		"""Vérifie le refus d'un fichier inexistant."""
		with tempfile.TemporaryDirectory() as directory:
			missing_file = Path(directory) / "missing.xspf"

			print("\nFichier inexistant refusé :")
			print(f"  Fichier : {missing_file}")

			with self.assertRaisesRegex(
				ValueError,
				"Le fichier XSPF n'existe pas.",
			):
				XspfService().load_playlist(missing_file)


if __name__ == "__main__":
	unittest.main(verbosity=2)
