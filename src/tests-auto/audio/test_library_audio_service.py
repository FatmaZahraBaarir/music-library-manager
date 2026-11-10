import sys
import unittest
from pathlib import Path

SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.playlist import Playlist
from library.models.track import AudioFormat, Track
from library.services.library_service import LibraryService


class FakeMetadataService:
	"""Construit des Track sans ouvrir les fichiers."""

	def __init__(self):
		self.received_paths = []

	def read_track(self, file_path):
		path = Path(file_path)
		self.received_paths.append(path)
		audio_format = (
			AudioFormat.FLAC
			if path.suffix.lower() == ".flac"
			else AudioFormat.MP3
		)
		return Track(path, audio_format)


class FakeAudioService:
	"""Enregistre les appels audio sans produire de son."""

	def __init__(self):
		self.played_track = None
		self.played_playlist = None
		self.pause_called = False
		self.resume_called = False
		self.stop_called = False
		self.update_called = False
		self.playing = False

	def play_track(self, track):
		self.played_track = track
		self.playing = True

	def play_playlist(self, playlist):
		self.played_playlist = playlist
		self.playing = True

	def update_playlist_playback(self):
		self.update_called = True
		return self.played_track

	def pause_playback(self):
		self.pause_called = True
		self.playing = False

	def resume_playback(self):
		self.resume_called = True
		self.playing = True

	def stop_playback(self):
		self.stop_called = True
		self.playing = False

	def is_playing(self):
		return self.playing


class LibraryAudioServiceTests(unittest.TestCase):
	"""
	@brief Vérifie la connexion entre LibraryService et AudioService.
	"""

	def setUp(self):
		self.metadata_service = FakeMetadataService()
		self.audio_service = FakeAudioService()
		self.library_service = LibraryService(
			metadata_service=self.metadata_service,
			audio_service=self.audio_service,
		)

	def test_play_track_validates_then_delegates(self):
		"""Construit un Track avant de demander sa lecture."""
		file_path = Path("music.mp3")
		track = self.library_service.play_track(file_path)

		self.assertEqual(self.metadata_service.received_paths, [file_path])
		self.assertIs(self.audio_service.played_track, track)
		self.assertEqual(track.file_path, file_path)

	def test_play_playlist_validates_every_track(self):
		"""Valide chaque chemin avant de lire une playlist."""
		playlist = Playlist(
			"Test",
			tracks=[
				Track(Path("first.mp3"), AudioFormat.MP3),
				Track(Path("second.flac"), AudioFormat.FLAC),
			],
		)
		validated_playlist = self.library_service.play_playlist(playlist)

		self.assertEqual(
			self.metadata_service.received_paths,
			[Path("first.mp3"), Path("second.flac")],
		)
		self.assertIs(
			self.audio_service.played_playlist,
			validated_playlist,
		)
		self.assertEqual(len(validated_playlist.tracks), 2)

	def test_playback_controls_are_delegated(self):
		"""Délègue pause, reprise, arrêt et état au service audio."""
		self.library_service.pause_playback()
		self.library_service.resume_playback()
		self.library_service.update_playlist_playback()
		self.assertTrue(self.library_service.is_playing())
		self.library_service.stop_playback()

		self.assertTrue(self.audio_service.pause_called)
		self.assertTrue(self.audio_service.resume_called)
		self.assertTrue(self.audio_service.update_called)
		self.assertTrue(self.audio_service.stop_called)
		self.assertFalse(self.library_service.is_playing())


if __name__ == "__main__":
	unittest.main(verbosity=2)
