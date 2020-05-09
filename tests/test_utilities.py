import shutil
import sys
from pathlib import Path
from unittest import TestCase

import pkg_resources
from PIL import Image, ImageChops

from titler.constants import DEFAULT_FONT
from titler.draw import process_images, _convert_file_name_to_title, _process_batch, _process_image, \
    _get_best_top_color, _split_string_by_nearest_middle_space
from titler.parse import parse_input
from titler.store import save_copies

TRC_ICON_PATH = "assets/icons/the-renegade-coder-sample-icon.png"
TRC_RED = (201, 2, 41, 255)

VF_ICON_PATH = "assets/icons/virtual-flat-sample-icon.png"
VF_BLUE = (0, 164, 246, 255)

ASSETS = "assets/"
DEFAULT_IMAGE = "assets/images/23-tech-topics-to-tackle.jpg"
LOGO_RED_IMAGE = "assets/images/3-ways-to-check-if-a-list-is-empty-in-python.jpg"
LOGO_BLUE_IMAGE = "assets/images/hello-world-in-matlab.jpg"
FREE_IMAGE = "assets/images/columbus-drivers-are-among-the-worst.jpg"
PREMIUM_IMAGE = "assets/images/the-guide-to-causing-mass-panic.jpg"
SPECIAL_IMAGE = "assets/images/happy-new-year.jpg"
CUSTOM_FONT_IMAGE = "assets/images/reflecting-on-my-third-semester-of-teaching.jpg"
ONE_LINE_TITLE_IMAGE = "assets/images/minimalism.jpg"

TEST_DUMP = "tests/dump"
TEST_SOLO_DUMP = TEST_DUMP + "/solo"
TEST_BATCH_DUMP = TEST_DUMP + "/batch"
SAMPLE_DUMP = "samples/v" + pkg_resources.require("image-titler")[0].version


class TestUtilities(TestCase):
    pass


class TestIntegration(TestUtilities):

    @classmethod
    def setUpClass(cls) -> None:
        try:
            shutil.rmtree(TEST_SOLO_DUMP)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(SAMPLE_DUMP)
        except FileNotFoundError:
            pass

        Path(TEST_SOLO_DUMP).mkdir(parents=True, exist_ok=True)
        Path(SAMPLE_DUMP).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def generate_image(input_path, title, logo_path=None, tier="", font=DEFAULT_FONT):
        test_image = _process_image(
            path=input_path,
            title=title,
            logo_path=logo_path,
            tier=tier,
            font=font
        )
        test_file = save_copies([test_image], output_path=TEST_SOLO_DUMP, title=title)

        title = _convert_file_name_to_title(path=input_path)
        sample_image = _process_image(
            path=input_path,
            title=title,
            logo_path=logo_path,
            tier=tier,
            font=font
        )
        save_copies([sample_image], output_path=SAMPLE_DUMP)
        return test_file[0]

    def test_custom_title(self):
        test_file = self.generate_image(DEFAULT_IMAGE, "Test Default")
        self.assertTrue(Path(test_file).exists())

    def test_logo_red(self):
        test_file = self.generate_image(LOGO_RED_IMAGE, "Test Red Logo", logo_path=TRC_ICON_PATH)
        self.assertTrue(Path(test_file).exists())

    def test_logo_blue(self):
        self.generate_image(LOGO_BLUE_IMAGE, "Test Blue Logo", logo_path=VF_ICON_PATH)

    def test_free_tier(self):
        self.generate_image(FREE_IMAGE, "Test Free Tier", tier="free")

    def test_premium_tier(self):
        self.generate_image(PREMIUM_IMAGE, "Test Premium Tier", tier="premium")

    def test_custom_font(self):
        self.generate_image(CUSTOM_FONT_IMAGE, "Test Custom Font", font="assets/fonts/arial.ttf")

    def test_custom_font_strange_height(self):
        self.generate_image(
            CUSTOM_FONT_IMAGE,
            title="Test Custom Font Strange Height",
            font="tests/fonts/gadugi.ttf"
        )

    def test_special_chars_in_title(self):
        test_image = _process_image(path=SPECIAL_IMAGE, title="Test Special Chars?")
        save_copies([test_image], output_path=TEST_SOLO_DUMP, title="Test Special Chars?")

    def test_one_line_title(self):
        self.generate_image(ONE_LINE_TITLE_IMAGE, title="TestSingleLineFile")


class TestSaveCopies(TestUtilities):

    def test_default(self):
        image = Image.open(DEFAULT_IMAGE)
        test_file = save_copies(image)[0]
        self.assertTrue(Path(test_file).exists())
        Path(test_file).unlink()


class TestProcessImage(TestUtilities):

    def setUp(self) -> None:
        self.size = (1920, 960)
        self.input_image = Image.open(DEFAULT_IMAGE)
        self.default_image = _process_image(path=DEFAULT_IMAGE, title="Test Default Image")
        self.different_title_image = _process_image(path=DEFAULT_IMAGE, title="Test Different Logo Image")

    def test_default(self):
        self.assertEqual(self.size, self.default_image.size)
        self.assertIsNone(ImageChops.difference(self.default_image, self.default_image).getbbox())
        self.assertIsNotNone(ImageChops.difference(self.input_image, self.default_image).getbbox())

    def test_compare_all(self):
        images = [
            self.default_image,
            self.different_title_image
        ]
        for i1 in images:
            for i2 in images:
                if i1 is not i2:
                    self.assertIsNotNone(ImageChops.difference(i1, i2).getbbox())


class TestProcessBatch(TestUtilities):

    @classmethod
    def setUpClass(cls) -> None:
        try:
            shutil.rmtree(TEST_BATCH_DUMP)
        except FileNotFoundError:
            pass

        Path(TEST_BATCH_DUMP + "/default").mkdir(parents=True, exist_ok=True)
        Path(TEST_BATCH_DUMP + "/free-tier").mkdir(parents=True, exist_ok=True)
        Path(TEST_BATCH_DUMP + "/premium-tier").mkdir(parents=True, exist_ok=True)

    def test_batch_default(self):
        _process_batch(path=ASSETS, output_path=TEST_BATCH_DUMP + "/default")

    def test_batch_free_tier(self):
        _process_batch(path=ASSETS, tier="free", output_path=TEST_BATCH_DUMP + "/free-tier")

    def test_batch_premium_tier(self):
        _process_batch(path=ASSETS, tier="premium", output_path=TEST_BATCH_DUMP + "/premium-tier")


class TestConvertFileNameToTitle(TestUtilities):

    def test_default(self):
        title = _convert_file_name_to_title()
        self.assertEqual(None, title)

    def test_custom_title(self):
        title = _convert_file_name_to_title(title="How to Loop in Python")
        self.assertEqual("How to Loop in Python", title)

    def test_custom_path(self):
        title = _convert_file_name_to_title(path="how-to-loop-in-python.png")
        self.assertEqual("How to Loop in Python", title)

    def test_custom_separator(self):
        title = _convert_file_name_to_title(path="how.to.loop.in.python.png", separator=".")
        self.assertEqual("How to Loop in Python", title)


class TestGetBestTopColor(TestUtilities):

    def test_renegade_coder_icon(self):
        img: Image.Image = Image.open(TRC_ICON_PATH)
        color = _get_best_top_color(img)
        self.assertEqual(color, TRC_RED)
        img.close()

    def test_virtual_flat_icon(self):
        img: Image.Image = Image.open(VF_ICON_PATH)
        color = _get_best_top_color(img)
        self.assertEqual(color, VF_BLUE)
        img.close()


class TestSplitString(TestUtilities):

    def test_first_space(self):
        top, bottom = _split_string_by_nearest_middle_space("Split first one")
        self.assertEqual(top, "Split")
        self.assertEqual(bottom, "first one")

    def test_middle_space(self):
        top, bottom = _split_string_by_nearest_middle_space("Hello World")
        self.assertEqual(top, "Hello")
        self.assertEqual(bottom, "World")

    def test_last_space(self):
        top, bottom = _split_string_by_nearest_middle_space("Split last opening")
        self.assertEqual(top, "Split last")
        self.assertEqual(bottom, "opening")


class TestParseInput(TestUtilities):

    def setUp(self) -> None:
        sys.argv = sys.argv[:1]  # clears args for each tests

    def test_default(self):
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, None)
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, None)

    def test_title(self):
        sys.argv.append("-t")
        sys.argv.append("Hello World")
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, None)
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, "Hello World")

    def test_path(self):
        sys.argv.append("-p")
        sys.argv.append("path/to/stuff")
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, "path/to/stuff")
        self.assertEqual(args.tier, None)
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, None)

    def test_output_path(self):
        sys.argv.append("-o")
        sys.argv.append("path/to/stuff")
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, None)
        self.assertEqual(args.output_path, "path/to/stuff")
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, None)

    def test_logo_path(self):
        sys.argv.append("-l")
        sys.argv.append("path/to/stuff")
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, None)
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, "path/to/stuff")
        self.assertEqual(args.title, None)

    def test_batch(self):
        sys.argv.append("-b")
        args = parse_input()
        self.assertEqual(args.batch, True)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, None)
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, None)

    def test_tier_premium(self):
        sys.argv.append("-r")
        sys.argv.append("premium")
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, "premium")
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, None)

    def test_tier_free(self):
        sys.argv.append("-r")
        sys.argv.append("free")
        args = parse_input()
        self.assertEqual(args.batch, False)
        self.assertEqual(args.path, None)
        self.assertEqual(args.tier, "free")
        self.assertEqual(args.output_path, None)
        self.assertEqual(args.logo_path, None)
        self.assertEqual(args.title, None)
