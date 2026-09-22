import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image, ImageDraw

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/figma2code/scripts/compare_images.py'
spec = importlib.util.spec_from_file_location('compare_images', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ComparisonTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reference = self.root / 'reference.png'
        self.actual = self.root / 'actual.png'

    def save_pair(self, a, b):
        a.save(self.reference)
        b.save(self.actual)

    def run_compare(self, **kwargs):
        return module.compare(self.reference, self.actual, self.root / 'out', **kwargs)

    def test_identical_and_cli_output(self):
        self.save_pair(Image.new('RGB', (20, 20), 'white'), Image.new('RGB', (20, 20), 'white'))
        result = subprocess.run([sys.executable, str(SCRIPT), '--reference', str(self.reference), '--actual', str(self.actual), '--out', str(self.root / 'out')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        import json
        report = json.loads(result.stdout)
        self.assertEqual(report['changedPixels'], 0)
        self.assertIsNone(report['changedBounds'])
        self.assertEqual(len(list((self.root / 'out').iterdir())), 5)

    def test_crop_retains_full_image_coordinates(self):
        a = Image.new('RGB', (100, 60), 'white')
        b = a.copy()
        ImageDraw.Draw(b).rectangle((30, 20, 39, 29), fill='black')
        self.save_pair(a, b)
        report = self.run_compare(crop=(20, 10, 40, 40))
        self.assertEqual(report['changedBounds'], [30, 20, 40, 30])
        self.assertEqual(report['changedPixels'], 100)
        self.assertEqual(report['changedFraction'], 100/1600)

    def test_threshold_is_strict(self):
        a = Image.new('RGB', (2, 1), (100, 100, 100))
        b = a.copy()
        b.putpixel((0, 0), (116, 100, 100))
        b.putpixel((1, 0), (117, 100, 100))
        self.save_pair(a, b)
        self.assertEqual(self.run_compare(threshold=16)['changedPixels'], 1)

    def test_transparent_pixels_composite_to_background(self):
        self.save_pair(Image.new('RGBA', (2, 2), (0, 0, 0, 0)), Image.new('RGB', (2, 2), 'white'))
        self.assertEqual(self.run_compare()['changedPixels'], 0)

    def test_bad_dimensions_crop_threshold_and_overwrite(self):
        self.save_pair(Image.new('RGB', (10, 10)), Image.new('RGB', (11, 10)))
        with self.assertRaisesRegex(ValueError, 'Canvas mismatch'):
            self.run_compare()
        self.save_pair(Image.new('RGB', (10, 10)), Image.new('RGB', (10, 10)))
        for crop in ((-1, 0, 5, 5), (0, 0, 11, 5), (0, 0, 0, 5)):
            with self.assertRaises(ValueError):
                self.run_compare(crop=crop)
        with self.assertRaises(ValueError):
            self.run_compare(threshold=256)
        self.run_compare()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.run_compare()


if __name__ == '__main__':
    unittest.main()
