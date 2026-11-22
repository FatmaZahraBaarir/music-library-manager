import sys
import unittest
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.album import Album
from library.models.album_track_info import AlbumTrackInfo
from library.models.metadata import Metadata
from library.models.track import AudioFormat, Track


class AlbumModelsTests(unittest.TestCase):
	"""@brief Vérifie les modèles d'album et leur relation avec Track."""

	def test_album_copies_track_list_and_accepts_partial_information(self):
		"""@brief Construit un album local avant son enrichissement distant."""
		album_track = AlbumTrackInfo(title="First track", position=1)
		tracks = [album_track]
		album = Album(title="Album", artist="Artist", tracks=tracks)
		tracks.clear()

		self.assertIsNone(album.musicbrainz_id)
		self.assertIsNone(album.cover)
		self.assertEqual(album.tracks, [album_track])

	def test_album_track_info_is_not_a_local_audio_track(self):
		"""@brief Vérifie qu'une piste distante ne prétend pas être lisible."""
		track_info = AlbumTrackInfo(
			title="Remote track",
			artist="Artist",
			disc_number=1,
			position=2,
			duration_seconds=125.5,
			lyrics="Lyrics",
		)

		self.assertFalse(hasattr(track_info, "file_path"))
		self.assertFalse(hasattr(track_info, "format"))

	def test_local_track_holds_album_instead_of_cover(self):
		"""@brief Vérifie la relation facultative entre Track et Album."""
		album = Album(title="Album", artist="Artist")
		track = Track(
			file_path=Path("song.mp3"),
			format=AudioFormat.MP3,
			metadata=Metadata(artist="Artist", album_title="Album"),
			album=album,
		)

		self.assertIs(track.album, album)
		self.assertFalse(hasattr(track, "cover"))


if __name__ == "__main__":
	unittest.main(verbosity=2)
