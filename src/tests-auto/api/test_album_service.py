import sys
import unittest
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.album import Album
from library.models.album_track_info import AlbumTrackInfo
from library.services.api.album_service import AlbumService


class FakeMusicBrainzService:
	"""@brief Simule la construction d'un album distant."""

	def __init__(self):
		self.calls = []

	def search_album(self, artist, album_title):
		self.calls.append((artist, album_title))
		return Album(
			title=album_title,
			artist=artist,
			musicbrainz_id="release-id",
			tracks=[
				AlbumTrackInfo(
					title="First",
					artist=artist,
					duration_seconds=120,
				),
				AlbumTrackInfo(
					title="Second",
					artist=artist,
					duration_seconds=180,
				),
			],
		)


class FakeLyricsService:
	"""@brief Retourne une parole et simule une erreur partielle."""

	def __init__(self):
		self.calls = []

	def get_lyrics(self, title, artist, album_title, duration_seconds=None):
		self.calls.append((title, artist, album_title, duration_seconds))
		if title == "Second":
			raise ValueError("LRCLIB indisponible")
		return "First lyrics"


class AlbumServiceTests(unittest.TestCase):
	"""@brief Vérifie l'orchestration des albums, paroles et cache."""

	def setUp(self):
		self.musicbrainz_service = FakeMusicBrainzService()
		self.lyrics_service = FakeLyricsService()
		self.album_service = AlbumService(
			musicbrainz_service=self.musicbrainz_service,
			lyrics_service=self.lyrics_service,
		)

	def test_album_is_enriched_without_losing_tracks_with_missing_lyrics(self):
		album = self.album_service.get_album(" Artist ", " Album ")

		self.assertEqual(album.tracks[0].lyrics, "First lyrics")
		self.assertIsNone(album.tracks[1].lyrics)
		self.assertEqual(
			self.musicbrainz_service.calls,
			[("Artist", "Album")],
		)
		self.assertEqual(len(self.lyrics_service.calls), 2)

	def test_same_normalized_album_is_returned_from_cache(self):
		first_album = self.album_service.get_album("Artist", "Album")
		second_album = self.album_service.get_album(" artist ", " album ")

		self.assertIs(second_album, first_album)
		self.assertEqual(len(self.musicbrainz_service.calls), 1)
		self.assertEqual(len(self.lyrics_service.calls), 2)

	def test_missing_required_fields_are_rejected(self):
		with self.assertRaisesRegex(ValueError, "artiste"):
			self.album_service.get_album(" ", "Album")
		with self.assertRaisesRegex(ValueError, "album"):
			self.album_service.get_album("Artist", None)


if __name__ == "__main__":
	unittest.main(verbosity=2)
