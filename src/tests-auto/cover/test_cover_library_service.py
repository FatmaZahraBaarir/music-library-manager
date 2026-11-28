import sys
import unittest
from pathlib import Path

SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.album import Album
from library.models.cover import Cover
from library.models.metadata import Metadata
from library.models.track import AudioFormat, Track
from library.services.library_service import LibraryService


class FakeAlbumService:
	"""@brief Simule la récupération d'un album distant."""

	def __init__(self):
		self.album = Album(
			"Album",
			"Artist",
			musicbrainz_id="release-id",
		)
		self.calls = []

	def get_album(self, artist, album_title):
		self.calls.append((artist, album_title))
		return self.album


class FakeCoverService:
	"""@brief Simule les opérations du service de pochettes."""

	def __init__(self, local_cover=None, remote_cover=None):
		self.local_cover = local_cover
		self.remote_cover = remote_cover
		self.local_calls = []
		self.download_calls = []
		self.save_calls = []
		self.save_error = None

	def find_local_cover(self, track):
		self.local_calls.append(track)
		return self.local_cover

	def download_cover(self, album):
		self.download_calls.append(album)
		return self.remote_cover

	def save_cover(self, track, cover):
		self.save_calls.append((track, cover, cover.is_validated))
		if self.save_error is not None:
			raise self.save_error
		return Path("cover.png")


class CoverLibraryServiceTests(unittest.TestCase):
	"""@brief Vérifie l'accès aux pochettes par la façade commune."""

	def _library_service(self, cover_service, album_service=None):
		return LibraryService(
			file_service=object(),
			metadata_service=object(),
			metadata_input_service=object(),
			xspf_service=object(),
			audio_service=object(),
			album_service=FakeAlbumService() if album_service is None else album_service,
			cover_service=cover_service,
		)

	@staticmethod
	def _track(album=None):
		return Track(
			Path("song.mp3"),
			AudioFormat.MP3,
			metadata=Metadata(
				artist="Artist",
				album_title="Album",
				year=2026,
			),
			album=album,
		)

	def test_returns_the_cover_already_associated_with_the_album(self):
		"""@brief Évite toute nouvelle recherche lorsque l'album a sa pochette."""
		cover = Cover(b"image", "image/png", is_validated=True)
		album = Album("Album", "Artist", cover=cover)
		cover_service = FakeCoverService()
		library_service = self._library_service(cover_service)

		result = library_service.find_cover_for_track(self._track(album=album))

		self.assertIs(result, cover)
		self.assertEqual(cover_service.local_calls, [])
		self.assertEqual(cover_service.download_calls, [])

	def test_associates_a_local_cover_without_calling_album_api(self):
		"""@brief Crée un album partiel lorsque la pochette est locale."""
		cover = Cover(b"image", "image/png", is_validated=True)
		cover_service = FakeCoverService(local_cover=cover)
		album_service = FakeAlbumService()
		library_service = self._library_service(cover_service, album_service)
		track = self._track()

		result = library_service.find_cover_for_track(track)

		self.assertIs(result, cover)
		self.assertEqual(album_service.calls, [])
		self.assertIsNotNone(track.album)
		self.assertEqual(track.album.title, "Album")
		self.assertEqual(track.album.artist, "Artist")
		self.assertEqual(track.album.release_date, "2026")
		self.assertIs(track.album.cover, cover)

	def test_downloads_a_candidate_only_after_album_lookup(self):
		"""@brief Utilise MusicBrainz seulement lorsqu'aucune image locale n'existe."""
		candidate = Cover(b"image", "image/png", is_validated=False)
		cover_service = FakeCoverService(remote_cover=candidate)
		album_service = FakeAlbumService()
		library_service = self._library_service(cover_service, album_service)
		track = self._track()

		result = library_service.find_cover_for_track(track)

		self.assertIs(result, candidate)
		self.assertEqual(album_service.calls, [("Artist", "Album")])
		self.assertIs(track.album, album_service.album)
		self.assertEqual(cover_service.download_calls, [album_service.album])
		self.assertIsNone(track.album.cover)

	def test_confirms_saves_and_associates_a_remote_candidate(self):
		"""@brief La sauvegarde de façade représente la confirmation utilisateur."""
		candidate = Cover(b"image", "image/png", is_validated=False)
		album = Album("Album", "Artist", musicbrainz_id="release-id")
		track = self._track(album=album)
		cover_service = FakeCoverService()
		library_service = self._library_service(cover_service)

		output_path = library_service.save_cover_for_track(track, candidate)

		self.assertEqual(output_path, Path("cover.png"))
		self.assertTrue(candidate.is_validated)
		self.assertIs(album.cover, candidate)
		self.assertEqual(cover_service.save_calls, [(track, candidate, True)])

	def test_restores_validation_when_saving_fails(self):
		"""@brief N'annonce pas une validation si l'écriture a échoué."""
		candidate = Cover(b"image", "image/png", is_validated=False)
		cover_service = FakeCoverService()
		cover_service.save_error = OSError("disk full")
		library_service = self._library_service(cover_service)

		with self.assertRaises(OSError):
			library_service.save_cover_for_track(self._track(), candidate)

		self.assertFalse(candidate.is_validated)


if __name__ == "__main__":
	unittest.main(verbosity=2)
