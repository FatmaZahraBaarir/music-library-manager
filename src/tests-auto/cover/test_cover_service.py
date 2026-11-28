import base64
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from mutagen.flac import FLAC, Picture
from mutagen.id3 import APIC, ID3

SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.models.album import Album
from library.models.cover import Cover
from library.models.track import AudioFormat, Track
from library.services.cover.cover_service import CoverService


AUDIO_DIRECTORY = Path(__file__).resolve().parents[1] / "fixtures" / "audio"
MP3_FILE = AUDIO_DIRECTORY / "sample.mp3"
FLAC_FILE = AUDIO_DIRECTORY / "sample.flac"
PNG_DATA = base64.b64decode(
	"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
JPEG_DATA = b"\xff\xd8\xff\xe0test-jpeg"


def detect_test_mime(data):
	"""@brief Détecte les signatures minimales utilisées par ces tests."""
	if data.startswith(b"\x89PNG\r\n\x1a\n"):
		return "image/png"
	if data.startswith(b"\xff\xd8\xff"):
		return "image/jpeg"
	return "text/html"


class FakeCoverArtArchiveClient:
	"""@brief Simule le téléchargement d'une pochette distante."""

	def __init__(self, result=None):
		self.result = result
		self.received_ids = []

	def download_front_cover(self, musicbrainz_id):
		self.received_ids.append(musicbrainz_id)
		return self.result


class CoverServiceTests(unittest.TestCase):
	"""@brief Vérifie la recherche, la validation et la sauvegarde des pochettes."""

	def _service(self, client=None):
		return CoverService(
			cover_art_archive_client=(
				FakeCoverArtArchiveClient() if client is None else client
			),
			magic_function=detect_test_mime,
		)

	@staticmethod
	def _track(file_path, audio_format):
		return Track(Path(file_path), audio_format)

	def test_detects_real_png_with_python_magic(self):
		"""@brief Vérifie la configuration MIME réelle de python-magic."""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			audio_path = root / "song.mp3"
			audio_path.write_bytes(b"audio")
			(root / "cover.png").write_bytes(PNG_DATA)
			service = CoverService(
				cover_art_archive_client=FakeCoverArtArchiveClient(),
			)

			cover = service.find_local_cover(
				self._track(audio_path, AudioFormat.MP3)
			)

			self.assertIsNotNone(cover)
			self.assertEqual(cover.mime_type, "image/png")

	def test_finds_saved_cover_before_embedded_cover(self):
		"""@brief Donne la priorité à l'image déjà enregistrée dans le dossier."""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			audio_path = root / "song.mp3"
			audio_path.write_bytes(b"not-needed")
			(root / "cover.png").write_bytes(PNG_DATA)
			(root / "folder.jpg").write_bytes(JPEG_DATA)
			service = self._service()

			cover = service.find_local_cover(
				self._track(audio_path, AudioFormat.MP3)
			)

			self.assertEqual(cover.data, PNG_DATA)
			self.assertEqual(cover.mime_type, "image/png")
			self.assertTrue(cover.is_validated)
			self.assertEqual(cover.source, str(root / "cover.png"))

	def test_skips_a_saved_file_with_a_false_image_extension(self):
		"""@brief Ignore un fichier local dont le contenu n'est pas une image."""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			audio_path = root / "song.mp3"
			audio_path.write_bytes(b"not-an-id3-file")
			(root / "cover.jpg").write_bytes(b"<html>error</html>")

			cover = self._service().find_local_cover(
				self._track(audio_path, AudioFormat.MP3)
			)

			self.assertIsNone(cover)

	@unittest.skipUnless(MP3_FILE.is_file(), "Ajouter sample.mp3 pour ce test.")
	def test_extracts_front_cover_from_a_real_mp3_copy(self):
		"""@brief Extrait un cadre APIC depuis une copie de la fixture MP3."""
		with tempfile.TemporaryDirectory() as directory:
			mp3_copy = Path(directory) / "copy.mp3"
			shutil.copy2(MP3_FILE, mp3_copy)
			tags = ID3(mp3_copy)
			tags.delall("APIC")
			tags.add(APIC(mime="image/jpeg", type=0, desc="Other", data=JPEG_DATA))
			tags.add(APIC(mime="image/png", type=3, desc="Front", data=PNG_DATA))
			tags.save(mp3_copy)

			cover = self._service().find_local_cover(
				self._track(mp3_copy, AudioFormat.MP3)
			)

			self.assertEqual(cover.data, PNG_DATA)
			self.assertEqual(cover.source, "embedded:mp3")
			self.assertTrue(cover.is_validated)

	@unittest.skipUnless(FLAC_FILE.is_file(), "Ajouter sample.flac pour ce test.")
	def test_extracts_front_cover_from_a_real_flac_copy(self):
		"""@brief Extrait une image PICTURE depuis une copie de la fixture FLAC."""
		with tempfile.TemporaryDirectory() as directory:
			flac_copy = Path(directory) / "copy.flac"
			shutil.copy2(FLAC_FILE, flac_copy)
			audio = FLAC(flac_copy)
			audio.clear_pictures()
			other_picture = Picture()
			other_picture.type = 0
			other_picture.mime = "image/jpeg"
			other_picture.data = JPEG_DATA
			front_picture = Picture()
			front_picture.type = 3
			front_picture.mime = "image/png"
			front_picture.data = PNG_DATA
			audio.add_picture(other_picture)
			audio.add_picture(front_picture)
			audio.save()

			cover = self._service().find_local_cover(
				self._track(flac_copy, AudioFormat.FLAC)
			)

			self.assertEqual(cover.data, PNG_DATA)
			self.assertEqual(cover.source, "embedded:flac")
			self.assertTrue(cover.is_validated)

	def test_reuses_the_local_memory_cache(self):
		"""@brief Évite de relire l'image locale lorsque le morceau revient."""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			audio_path = root / "song.mp3"
			cover_path = root / "cover.png"
			audio_path.write_bytes(b"audio")
			cover_path.write_bytes(PNG_DATA)
			service = self._service()
			track = self._track(audio_path, AudioFormat.MP3)

			first_cover = service.find_local_cover(track)
			cover_path.unlink()
			second_cover = service.find_local_cover(track)

			self.assertIs(second_cover, first_cover)

	def test_downloads_validates_and_caches_a_remote_candidate(self):
		"""@brief Vérifie le MIME réel et évite un second téléchargement."""
		client = FakeCoverArtArchiveClient(
			Cover(PNG_DATA, "text/html", source="https://example.test/cover")
		)
		service = self._service(client)
		album = Album("Album", "Artist", musicbrainz_id="release-id")

		first_cover = service.download_cover(album)
		second_cover = service.download_cover(album)

		self.assertIs(second_cover, first_cover)
		self.assertEqual(first_cover.mime_type, "image/png")
		self.assertFalse(first_cover.is_validated)
		self.assertEqual(client.received_ids, ["release-id"])

	def test_rejects_non_image_downloaded_content(self):
		"""@brief Refuse une page HTML même déclarée comme une image."""
		client = FakeCoverArtArchiveClient(
			Cover(b"<html>error</html>", "image/jpeg", source="remote")
		)
		service = self._service(client)
		album = Album("Album", "Artist", musicbrainz_id="release-id")

		with self.assertRaisesRegex(ValueError, "JPEG ou PNG"):
			service.download_cover(album)

	def test_saves_a_confirmed_cover_and_refuses_silent_overwrite(self):
		"""@brief Sauvegarde cover.png sans remplacer une autre image."""
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			audio_path = root / "song.mp3"
			audio_path.write_bytes(b"audio")
			track = self._track(audio_path, AudioFormat.MP3)
			service = self._service()
			cover = Cover(PNG_DATA, "image/png", is_validated=True)

			output_path = service.save_cover(track, cover)

			self.assertEqual(output_path, root / "cover.png")
			self.assertEqual(output_path.read_bytes(), PNG_DATA)
			self.assertEqual(cover.source, str(output_path))

			other_cover = Cover(
				PNG_DATA + b"different",
				"image/png",
				is_validated=True,
			)
			with self.assertRaises(FileExistsError):
				service.save_cover(track, other_cover)

	def test_refuses_to_save_an_unconfirmed_cover(self):
		"""@brief Interdit la sauvegarde directe d'une candidate distante."""
		with tempfile.TemporaryDirectory() as directory:
			audio_path = Path(directory) / "song.mp3"
			audio_path.write_bytes(b"audio")
			track = self._track(audio_path, AudioFormat.MP3)
			cover = Cover(PNG_DATA, "image/png", is_validated=False)

			with self.assertRaisesRegex(ValueError, "confirmée"):
				self._service().save_cover(track, cover)


if __name__ == "__main__":
	unittest.main(verbosity=2)
