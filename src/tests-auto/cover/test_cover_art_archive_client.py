import sys
import unittest
from pathlib import Path

import requests

SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.services.cover.cover_art_archive_client import CoverArtArchiveClient


class FakeResponse:
	"""@brief Simule une réponse HTTP diffusée par morceaux."""

	def __init__(self, status_code=200, data=b"image", headers=None, url=None):
		self.status_code = status_code
		self.data = data
		self.headers = {} if headers is None else headers
		self.url = url or "https://archive.example/final-cover"

	def raise_for_status(self):
		if self.status_code >= 400:
			raise requests.HTTPError(f"HTTP {self.status_code}")

	def iter_content(self, chunk_size):
		for position in range(0, len(self.data), chunk_size):
			yield self.data[position:position + chunk_size]


class FakeSession:
	"""@brief Retourne des réponses ou erreurs préparées."""

	def __init__(self, results):
		self.results = list(results)
		self.calls = []

	def get(self, url, **kwargs):
		self.calls.append((url, kwargs))
		result = self.results.pop(0)
		if isinstance(result, Exception):
			raise result
		return result


class CoverArtArchiveClientTests(unittest.TestCase):
	"""@brief Vérifie les requêtes effectuées vers Cover Art Archive."""

	def test_downloads_a_front_cover_candidate(self):
		"""@brief Retourne une candidate distante sans la valider."""
		response = FakeResponse(
			data=b"downloaded-image",
			headers={"Content-Type": "image/jpeg; charset=binary"},
		)
		session = FakeSession([response])
		client = CoverArtArchiveClient(session=session, sleep_function=lambda delay: None)

		cover = client.download_front_cover(" release-id ")

		self.assertEqual(cover.data, b"downloaded-image")
		self.assertEqual(cover.mime_type, "image/jpeg")
		self.assertFalse(cover.is_validated)
		self.assertEqual(cover.source, response.url)
		url, arguments = session.calls[0]
		self.assertEqual(
			url,
			"https://coverartarchive.org/release/release-id/front-500",
		)
		self.assertEqual(arguments["timeout"], 10)
		self.assertTrue(arguments["allow_redirects"])
		self.assertTrue(arguments["stream"])
		self.assertIn("User-Agent", arguments["headers"])

	def test_returns_none_after_a_not_found_response(self):
		"""@brief Une release sans couverture ne provoque pas d'erreur."""
		client = CoverArtArchiveClient(
			session=FakeSession([FakeResponse(status_code=404)]),
			sleep_function=lambda delay: None,
		)

		self.assertIsNone(client.download_front_cover("release-id"))

	def test_retries_once_after_a_temporary_status(self):
		"""@brief Retente une fois après une réponse 503."""
		delays = []
		session = FakeSession([
			FakeResponse(status_code=503, headers={"Retry-After": "2"}),
			FakeResponse(data=b"image", headers={"Content-Type": "image/png"}),
		])
		client = CoverArtArchiveClient(
			session=session,
			sleep_function=delays.append,
		)

		cover = client.download_front_cover("release-id")

		self.assertEqual(cover.data, b"image")
		self.assertEqual(len(session.calls), 2)
		self.assertEqual(delays, [2.0])

	def test_retries_once_after_a_network_error(self):
		"""@brief Retente une fois lorsqu'une erreur réseau est temporaire."""
		session = FakeSession([
			requests.ConnectionError("offline"),
			FakeResponse(data=b"image", headers={"Content-Type": "image/png"}),
		])
		client = CoverArtArchiveClient(
			session=session,
			sleep_function=lambda delay: None,
		)

		cover = client.download_front_cover("release-id")

		self.assertEqual(cover.data, b"image")
		self.assertEqual(len(session.calls), 2)

	def test_reports_a_persistent_network_error(self):
		"""@brief Remonte une erreur fonctionnelle après deux échecs réseau."""
		client = CoverArtArchiveClient(
			session=FakeSession([
				requests.ConnectionError("offline"),
				requests.ConnectionError("still offline"),
			]),
			sleep_function=lambda delay: None,
		)

		with self.assertRaisesRegex(ValueError, "Impossible de contacter"):
			client.download_front_cover("release-id")

	def test_refuses_content_larger_than_ten_mebibytes(self):
		"""@brief Bloque une image trop grande avant de lire son contenu."""
		response = FakeResponse(
			headers={"Content-Length": str(10 * 1024 * 1024 + 1)},
		)
		client = CoverArtArchiveClient(
			session=FakeSession([response]),
			sleep_function=lambda delay: None,
		)

		with self.assertRaisesRegex(ValueError, "10 Mio"):
			client.download_front_cover("release-id")


if __name__ == "__main__":
	unittest.main(verbosity=2)
