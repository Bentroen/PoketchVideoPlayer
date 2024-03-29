import os
import sys
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, List, Optional, Sequence, Tuple, TypeVar

import cv2
from PIL import Image, ImageChops

if TYPE_CHECKING:
    import progressbar

    ProgressType = progressbar.ProgressBar
else:
    ProgressType = TypeVar("ProgressType")


__all__ = ["OutputType", "get_video_frame_count", "process"]

POINT_TABLE = [0] + ([255] * 255)
POKETCH_PALETTE = [(112, 176, 112), (80, 128, 80), (56, 80, 40), (16, 40, 24)]
POKETCH_SCREEN_SIZE = (24, 20)
POKETCH_SCREEN_SIZE_PX = (192, 160)

Color = Tuple[int, int, int]
Palette = Sequence[Color]
Size = Tuple[int, int]


class OutputType(IntEnum):
    NONE = 0
    FRAMES = 1
    DIFF = 2
    BOTH = 3


def difference(a: Image.Image, b: Image.Image) -> Image.Image:
    """
    Return a mask of the different pixels between two images
    (all different pixels set to 255 and all equal pixels set to 0).
    """
    # https://stackoverflow.com/a/16721373/9045426
    diff = ImageChops.difference(a, b)
    diff = diff.convert("L")
    diff = diff.point(POINT_TABLE)
    return diff


def onion_skin(a: Image.Image, b: Image.Image, onion_opacity: int = 0.0) -> Image.Image:
    """
    Return an image containing the different pixels between two images.
    If `onion_opacity` is greater than 0, all other pixels will be set
    to that opacity; otherwise, they will be fully transparent.
    """
    diff = difference(a, b)
    new = diff.convert("RGBA")
    new.paste(b, mask=diff)
    alpha = round(onion_opacity * 255)
    final = b.copy().convert("RGBA")
    final.putalpha(alpha)
    final.paste(a, mask=diff)
    return final


def get_palette(colors: Palette) -> Image.Image:
    """
    Return a Pillow `Image` of a palette containing the given `colors`.
    """
    flattened = [channel for color in colors for channel in color]
    palette = Image.new("P", (16, 16))
    palette.putpalette(flattened * 64)
    return palette


def quantize(img: Image.Image, palette: Image.Image) -> Image.Image:
    """
    Quantize an image to a given palette.
    """
    return img.quantize(palette=palette, dither=Image.Dither.NONE)


def resize_nearest(img: Image.Image, size: Size) -> Image.Image:
    """
    Resize `img` to the given `size` using nearest-neighbor interpolation.
    """
    return img.resize(size, Image.Resampling.NEAREST)


def upscale(img: Image.Image, factor: int) -> Image.Image:
    """
    Resize `img` by `factor` using nearest-neighbor interpolation.
    """
    new_size = (img.width * factor, img.height * factor)
    return resize_nearest(img, new_size)


def stack(a: Image.Image, b: Image.Image) -> Image.Image:
    """
    Stack two images vertically.
    """
    new_size = (max(a.width, b.width), a.height + b.height)
    img = Image.new("RGBA", new_size, color=(0, 0, 0, 0))
    img.paste(a, (0, 0))
    img.paste(b, (0, a.height))
    return img


def get_video_frame_count(input_path) -> int:
    vidcap = cv2.VideoCapture(input_path)
    return int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))


def get_video_frames(
    path: os.PathLike, resize: Optional[Size] = None
) -> Iterator[Image.Image]:
    """
    Yield Pillow `Image`s of each frame of the video located at `path`,
    resized to `resize` (an optional 2-tuple containing the new size).
    """
    vidcap = cv2.VideoCapture(path)
    success, img = vidcap.read()
    while success:
        success, img = vidcap.read()
        if img is None:
            break  # end of video
        if resize:
            resized = cv2.resize(img, resize, interpolation=cv2.INTER_AREA)
        else:
            resized = img
        img_converted = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_converted)
        yield img_pil


def get_pixel_changes(a: Image.Image, b: Image.Image) -> List[tuple[int, int, int]]:
    """
    Given two images in the 'P' mode and equal in size, return a
    list of 3-tuples containing the coordinates of pixels that
    changed between the two images, and the index of the color
    they changed to.
    """
    if a.size != b.size:
        raise ValueError("Images must be the same size")
    if a.mode != "P" or b.mode != "P":
        raise ValueError("Images must be in palette mode")

    diff = difference(a, b)
    bbox = diff.getbbox()
    if bbox is None:
        return []

    changes = []
    x1, y1, x2, y2 = bbox
    for y in range(y1, y2):
        for x in range(x1, x2):
            if diff.getpixel((x, y)) == 255:
                new = b.getpixel((x, y))
                changes.append((x, y, new))
    return changes


def process(
    input_path: str,
    output_type: int = OutputType.NONE,
    output_dir: str = "frames",
    diff_opacity: float = 0.25,
    output_upscale_factor: int = 8,
    progress: Optional[ProgressType] = None,
):
    prev_frame = Image.new("P", POKETCH_SCREEN_SIZE, color=len(POKETCH_PALETTE))
    palette = get_palette(POKETCH_PALETTE)
    diffs = {}

    for i, frame in enumerate(get_video_frames(input_path, resize=POKETCH_SCREEN_SIZE)):
        frame_quantized = quantize(frame, palette)
        changed_pixels = get_pixel_changes(prev_frame, frame_quantized)
        if changed_pixels:
            diffs[i] = changed_pixels

        if output_type != OutputType.NONE:
            diff = onion_skin(prev_frame, frame_quantized, diff_opacity)
            output_path = Path(output_dir) / f"{i:04d}.png"
            if output_type == OutputType.FRAMES:
                upscale(frame_quantized, output_upscale_factor).save(output_path)
            elif output_type == OutputType.DIFF:
                upscale(diff, output_upscale_factor).save(output_path)
            elif output_type == OutputType.BOTH:
                stacked = stack(frame_quantized, diff)
                upscale(stacked, output_upscale_factor).save(output_path)

        prev_frame = frame_quantized
        progress.update(i)

    return diffs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <input_path>")
        sys.exit(1)

    try:
        import progressbar
    except ImportError:
        progressbar = None

    import json

    if progressbar:
        frame_count = get_video_frame_count(sys.argv[1])
        bar = progressbar.ProgressBar(max_value=frame_count)
    else:
        bar = None

    input_path = sys.argv[1]
    print(f"Processing {input_path}")
    diffs = process(input_path, output_type=OutputType.BOTH, progress=bar)
    with open("diffs.json", "w") as f:
        json.dump(diffs, f, indent=4, separators=(",", ": "))
