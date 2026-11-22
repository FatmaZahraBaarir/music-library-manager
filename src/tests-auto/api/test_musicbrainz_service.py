import sys
import unittest
from pathlib import Path

import requests


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.services.api.musicbrainz_service import MusicBrainzService


class FakeResponse:
	"""@brief Simule une réponse HTTP JSON."""

	def __init__(self, status_code=200, payload=None, headers=None):
		self.status_code = status_code
		self.payload = {} if payload is None else payload
		self.headers = {} if headers is None else headers

	def raise_for_status(self):
		if self.status_code >= 400:
			raise requests.HTTPError(f"HTTP {self.status_code}")

	def json(self):
		return self.payload


class FakeSession:
	"""@brief Retourne les réponses préparées et enregistre les appels."""

	def __init__(self, responses):
		self.responses = list(responses)
		self.calls = []

	def get(self, url, params, headers, timeout):
		self.calls.append(
			{
				"url": url,
				"params": params,
				"headers": headers,
				"timeout": timeout,
			}
		)
		return self.responses.pop(0)


class MusicBrainzServiceTests(unittest.TestCase):
	"""@brief Vérifie la recherche et la conversion des albums MusicBrainz."""

	def create_service(self, responses):
		self.sleep_calls = []
		self.session = FakeSession(responses)
		return MusicBrainzService(
			session=self.session,
			sleep_function=self.sleep_calls.append,
			time_function=lambda: 0.0,
		)

	@staticmethod
	def search_payload():
		return {
			"releases": [
				{
					"id": "lower-score",
					"title": "Example Album",
					"status": "Official",
					"score": 80,
					"artist-credit": [{"name": "Example Artist"}],
				},
				{
					"id": "best-release",
					"title": "Example Album",
					"status": "Official",
					"score": 100,
					"artist-credit": [{"name": "Example Artist"}],
				},
				{
					"id": "deluxe",
					"title": "Example Album Deluxe",
					"status": "Official",
					"score": 100,
					"artist-credit": [{"name": "Example Artist"}],
				},
			]
		}

	@staticmethod
	def release_payload():
		return {
			"id": "best-release",
			"title": "Example Album",
			"artist-credit": [{"name": "Example Artist"}],
			"date": "2026-01-02",
			"country": "FR",
			"status": "Official",
			"barcode": "123456789",
			"media": [
				{
					"position": 1,
					"tracks": [
						{
							"position": 1,
							"title": "First",
							"length": 123000,
							"recording": {
								"artist-credit": [
									{"name": "Example Artist"}
								]
							},
						}
					],
				},
				{
					"position": 2,
					"tracks": [
						{
							"position": 1,
							"recording": {
								"title": "Second",
								"length": 234500,
							},
						}
					],
				},
			],
		}

	def test_search_album_selects_best_exact_official_release(self):
		service = self.create_service(
			[
				FakeResponse(payload=self.search_payload()),
				FakeResponse(payload=self.release_payload()),
			]
		)

		album = service.search_album(" Example Artist ", " Example Album ")

		self.assertEqual(album.musicbrainz_id, "best-release")
		self.assertEqual(album.title, "Example Album")
		self.assertEqual(album.artist, "Example Artist")
		self.assertEqual(album.release_date, "2026-01-02")
		self.assertEqual(album.country, "FR")
		self.assertEqual(album.status, "Official")
		self.assertEqual(album.barcode, "123456789")
		self.assertEqual(len(album.tracks), 2)
		self.assertEqual(album.tracks[0].disc_number, 1)
		self.assertEqual(album.tracks[0].duration_seconds, 123.0)
		self.assertEqual(album.tracks[1].disc_number, 2)
		self.assertEqual(album.tracks[1].title, "Second")
		self.assertEqual(album.tracks[1].duration_seconds, 234.5)
		self.assertEqual(len(self.session.calls), 2)
		self.assertEqual(self.session.calls[0]["timeout"], 10)
		self.assertIn("MusicLibraryManager", self.session.calls[0]["headers"]["User-Agent"])
		self.assertIn("/release/best-release", self.session.calls[1]["url"])
		self.assertTrue(any(delay >= 1.0 for delay in self.sleep_calls))

	def test_search_album_rejects_missing_exact_official_release(self):
		service = self.create_service(
			[
				FakeResponse(
					payload={
						"releases": [
							{
								"id": "deluxe",
								"title": "Example Album Deluxe",
								"status": "Official",
								"artist-credit": [{"name": "Example Artist"}],
							}
						]
					}
				)
			]
		)

		with self.assertRaisesRegex(ValueError, "Aucun album officiel"):
			service.search_album("Example Artist", "Example Album")

	def test_temporary_error_is_retried_once(self):
		service = self.create_service(
			[
				FakeResponse(status_code=503, headers={"Retry-After": "2"}),
				FakeResponse(payload=self.search_payload()),
				FakeResponse(payload=self.release_payload()),
			]
		)

		album = service.search_album("Example Artist", "Example Album")

		self.assertEqual(album.musicbrainz_id, "best-release")
		self.assertIn(2.0, self.sleep_calls)
		self.assertEqual(len(self.session.calls), 3)


if __name__ == "__main__":
	unittest.main(verbosity=2)
