#!/usr/bin/env python3
"""Compare aligned screenshots without hiding layout errors through resizing."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageColor


def compare(reference, actual, output, crop=None, threshold=16, background='#ffffff'):
    if not 0 <= threshold <= 255:
        raise ValueError('threshold must be between 0 and 255')
    color = ImageColor.getrgb(background)
    if len(color) != 3:
        raise ValueError('background must be an opaque RGB color')

    def load(path):
        with Image.open(path) as source:
            rgba = source.convert('RGBA')
            return Image.alpha_composite(Image.new('RGBA', rgba.size, (*color, 255)), rgba).convert('RGB')

    reference, actual = load(reference), load(actual)
    if reference.size != actual.size:
        raise ValueError(f'Canvas mismatch: {reference.size} vs {actual.size}; normalize capture scale/region explicitly')
    full_size = reference.size
    x, y, width, height = crop if crop is not None else (0, 0, *full_size)
    if min(x, y) < 0 or width <= 0 or height <= 0 or x + width > full_size[0] or y + height > full_size[1]:
        raise ValueError('Crop must have positive dimensions and fit inside both images')
    box = (x, y, x + width, y + height)
    reference, actual = reference.crop(box), actual.crop(box)
    channels = ImageChops.difference(reference, actual).split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    mask = maximum.point(lambda value: 255 if value > threshold else 0)
    changed = mask.histogram()[255]
    bounds = mask.getbbox()
    report = {
        'canvasSize': list(full_size), 'crop': [x, y, width, height],
        'threshold': threshold, 'background': background,
        'changedPixels': changed, 'totalPixels': width * height,
        'changedFraction': changed / (width * height),
        'changedBounds': [bounds[0] + x, bounds[1] + y, bounds[2] + x, bounds[3] + y] if bounds else None,
        'boundsConvention': 'full-image pixels; right and bottom exclusive',
        'acceptance': 'not-evaluated',
    }
    output = Path(output)
    destinations = [output / name for name in ('reference.png', 'actual.png', 'diff.png', 'overlay.png', 'report.json')]
    # Never overwrite an existing evidence set. Use a fresh directory per run.
    if any(path.exists() for path in destinations):
        raise ValueError('Output evidence already exists; use a fresh output directory')
    output.mkdir(parents=True, exist_ok=True)
    reference.save(destinations[0])
    actual.save(destinations[1])
    Image.composite(Image.new('RGB', actual.size, '#ff0033'), actual.convert('L').convert('RGB'), mask).save(destinations[2])
    Image.blend(reference, actual, 0.5).save(destinations[3])
    destinations[4].write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--actual', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--crop', nargs=4, type=int, metavar=('X', 'Y', 'WIDTH', 'HEIGHT'))
    parser.add_argument('--threshold', type=int, default=16)
    parser.add_argument('--background', default='#ffffff')
    args = parser.parse_args()
    try:
        report = compare(args.reference, args.actual, args.out, args.crop, args.threshold, args.background)
    except (ValueError, OSError) as error:
        parser.exit(2, f'error: {error}\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
