import importlib.util
import io
import json
from pathlib import Path
import unittest
from PIL import Image


MODULE_PATH = Path(__file__).with_name("make-grid.py")
SPEC = importlib.util.spec_from_file_location("make_grid", MODULE_PATH)
make_grid = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(make_grid)


class MakeGridPathTests(unittest.TestCase):
    def test_default_paths_follow_skill_directory(self):
        skill_root = MODULE_PATH.parents[1]

        self.assertEqual(make_grid.SKILL_ROOT, skill_root)
        self.assertEqual(make_grid.FONT_CJK, skill_root / "scripts" / "SourceHanSansSC.otf")
        self.assertEqual(make_grid.CACHE_DIR, skill_root / "cover_cache")
        self.assertEqual(make_grid.OUTPUT_DIR, skill_root / "output")

    def test_stdin_json_is_decoded_as_utf8(self):
        payload = [{"title": "中文标题", "title_cn": "中文名"}]

        result = make_grid.read_input(io.BytesIO(json.dumps(payload, ensure_ascii=False).encode("utf-8")))

        self.assertEqual(result, payload)

    def test_long_text_wraps_without_ellipsis(self):
        class FakeFont:
            def getbbox(self, text):
                return (0, 0, len(text) * 10, 10)

        lines = make_grid.wrap_text("一二三四五六七八九十一二三四五", FakeFont(), 50)

        self.assertGreater(len(lines), 2)
        self.assertNotIn("…", "".join(lines))
        self.assertTrue(all(len(line) * 10 <= 50 for line in lines))

    def test_render_card_returns_one_bounded_card(self):
        card = make_grid.render_card({
            "title": "原名",
            "title_cn": "中文标题",
            "episode": None,
            "time": None,
            "description": "简介",
        }, 460)

        self.assertIsInstance(card, Image.Image)
        self.assertEqual(card.size[0], 460)
        self.assertGreaterEqual(card.size[1], make_grid.MIN_CARD_H)

    def test_card_keeps_translated_and_original_titles(self):
        fonts = make_grid.load_fonts(1.0)

        metrics = make_grid.card_metrics({"title": "English Original", "title_cn": "中文译名"}, 460, fonts)

        self.assertIn("中文译名", "".join(metrics[2]))
        self.assertIn("English Original", "".join(metrics[3]))

    def test_compose_grid_uses_rows_and_columns(self):
        cards = [Image.new("RGB", (460, 200), "black") for _ in range(3)]

        page = make_grid.compose_grid(cards, rows=2, cols=2, gap=12)

        self.assertEqual(page.size, (932, 412))

    def test_paginate_uses_rows_times_columns(self):
        pages = make_grid.paginate(list(range(9)), rows=4, cols=2)

        self.assertEqual([len(page) for page in pages], [8, 1])


if __name__ == "__main__":
    unittest.main()
