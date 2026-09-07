import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from adapters import fetch_tsuzuki


class FakeResponse:
    status_code = 200
    ok = True

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse(self.payload)


class TsuzukiAdapterTests(unittest.TestCase):
    def test_converts_schedule_episode_to_common_record(self):
        session = FakeSession({
            "ok": True,
            "episodes": [{
                "mediaId": 169582,
                "episode": 10,
                "airingAt": 1788782220,
                "title": "Original Title",
                "coverImage": "https://example.test/cover.jpg",
            }],
        })
        config = {
            "name": "tsuzuki",
            "url": "https://tsuzuki.top/api/v1/schedule",
            "timeout": 20,
        }

        result = fetch_tsuzuki(session, config, __import__("datetime").date(2026, 9, 7))

        self.assertEqual(result[0]["source"], "tsuzuki")
        self.assertEqual(result[0]["schedule_kind"], "episode")
        self.assertEqual(result[0]["source_id"], 169582)
        self.assertEqual(result[0]["title"], "Original Title")
        self.assertEqual(result[0]["episode"], 10)
        self.assertEqual(result[0]["cover"], "https://example.test/cover.jpg")
        self.assertEqual(session.calls[0][2]["params"], {"start": "2026-09-07", "days": 1})


if __name__ == "__main__":
    unittest.main()
