import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("merge-episodes.py")
SPEC = importlib.util.spec_from_file_location("merge_episodes", MODULE_PATH)
merge_episodes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(merge_episodes)


class MergeEpisodesTests(unittest.TestCase):
    def test_null_episode_is_kept_as_a_separate_record(self):
        data = [{"title": "周放送番", "episode": None, "schedule_kind": "weekly"}]

        self.assertEqual(merge_episodes.merge(data), data)

    def test_known_episodes_are_merged(self):
        data = [{"title": "连播番", "episode": 1}, {"title": "连播番", "episode": 2}]

        self.assertEqual(merge_episodes.merge(data)[0]["episode"], "1~2")

    def test_duplicate_episode_is_not_rendered_as_range(self):
        data = [{"title": "多发行版本", "episode": 10}, {"title": "多发行版本", "episode": 10}]

        self.assertEqual(merge_episodes.merge(data)[0]["episode"], "10")

    def test_duplicate_and_out_of_order_episodes_use_numeric_range(self):
        data = [
            {"title": "乱序番", "episode": 23},
            {"title": "乱序番", "episode": 21},
            {"title": "乱序番", "episode": 23},
        ]

        self.assertEqual(merge_episodes.merge(data)[0]["episode"], "21~23")


if __name__ == "__main__":
    unittest.main()
