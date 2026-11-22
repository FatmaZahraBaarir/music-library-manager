import sys
import unittest
from pathlib import Path

import requests


SRC_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SRC_DIRECTORY) not in sys.path:
	sys.path.insert(0, str(SRC_DIRECTORY))

from library.services.api.lyrics_service import LyricsService


class FakeResponse:
	"""@brief Simule une réponse LRCLIB."""

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
	"""@brief Retourne les réponses LRCLIB préparées."""

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


class LyricsServiceTests(unittest.TestCase):
	"""@brief Vérifie les paroles simples, synchronisées et absentes."""

	def create_service(self, responses):
		self.sleep_calls = []
		self.session = FakeSession(responses)
		return LyricsService(
			session=self.session,
			sleep_function=self.sleep_calls.append,
		)

	def test_plain_lyrics_have_priority(self):
		service = self.create_service(
			[
				FakeResponse(
					payload={
						"plainLyrics": " Plain lyrics ",
						"syncedLyrics": "[00:01] Synced lyrics",
					}
				)
			]
		)

		lyrics = service.get_lyrics(
			"Track",
			"Artist",
			"Album",
			duration_seconds=123.4,
		)

		self.assertEqual(lyrics, "Plain lyrics")
		self.assertEqual(self.session.calls[0]["params"]["duration"], 123)
		self.assertEqual(self.session.calls[0]["timeout"], 10)
		self.assertIn("MusicLibraryManager", self.session.calls[0]["headers"]["User-Agent"])

	def test_synced_lyrics_are_used_as_fallback(self):
		service = self.create_service(
			[
				FakeResponse(
					payload={
						"plainLyrics": None,
						"syncedLyrics": " [00:01] Synced lyrics ",
					}
				)
			]
		)

		lyrics = service.get_lyrics("Track", "Artist", "Album")

		self.assertEqual(lyrics, "[00:01] Synced lyrics")

	def test_missing_lyrics_return_none(self):
		service = self.create_service([FakeResponse(status_code=404)])

		lyrics = service.get_lyrics("Track", "Artist", "Album")

		self.assertIsNone(lyrics)

	def test_temporary_error_is_retried_once(self):
		service = self.create_service(
			[
				FakeResponse(status_code=429, headers={"Retry-After": "3"}),
				FakeResponse(payload={"plainLyrics": "Lyrics"}),
			]
		)

		lyrics = service.get_lyrics("Track", "Artist", "Album")

		self.assertEqual(lyrics, "Lyrics")
		self.assertEqual(len(self.session.calls), 2)
		self.assertIn(3.0, self.sleep_calls)


if __name__ == "__main__":
	unittest.main(verbosity=2)
