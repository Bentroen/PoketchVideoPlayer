import os
from enum import IntEnum
from pathlib import Path
from typing import Iterator, Sequence, Tuple

import cv2
from PIL import Image, ImageChops

POINT_TABLE = [0] + ([255] * 255)
POKETCH_PALETTE = [(112, 176, 112), (80, 128, 80), (56, 80, 40), (16, 40, 24)]
POKETCH_SCREEN_SIZE = (24, 20)
POKETCH_SCREEN_SIZE_PX = (192, 160)


class OutputType(IntEnum):
    NONE = 0
    FRAMES = 1
    DIFF = 2
    BOTH = 3


def difference(a: Image.Image, b: Image.Image, onion_opacity: int = 0.0) -> Image.Image:
    """
    Return an image containing the different pixels between two images.
    If `onion_opacity` is greater than 0, all other pixels will be set
    to that opacity; otherwise, they will be fully transparent.
    """
    # https://stackoverflow.com/a/16721373/9045426
    diff = ImageChops.difference(a, b)
    diff = diff.convert("L")
    diff = diff.point(POINT_TABLE)
    new = diff.convert("RGBA")
    new.paste(b, mask=diff)
    alpha = round(onion_opacity * 255)
    final = b.copy().convert("RGBA")
    final.putalpha(alpha)
    final.paste(a, mask=diff)
    return final


def get_palette(colors=Sequence[tuple[int, int, int]]) -> Image.Image:
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


def resize_nearest(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
    """
    Resize `img` to the given `size` using nearest-neighbor interpolation.
    """
    return img.resize(size, Image.Resampling.NEAREST)


def upscale(img: Image.Image, factor: int) -> Image.Image:
    """
    Resize `img` by `factor` and save it to `path`.
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


def get_video_frames(
    path: os.PathLike, resize: Tuple[int, int] = None
) -> Iterator[Tuple[Image.Image, int, int]]:
    """
    Yield Pillow `Image`s of each frame of the video located at `path`,
    resized to `resize` (an optional 2-tuple containing the new size).
    """
    vidcap = cv2.VideoCapture(path)
    success, img = vidcap.read()
    count = 0
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
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
        yield (img_pil, count, frame_count)
        count += 1


def main(
    input_path: str = "source.mp4",
    output_type: int = OutputType.NONE,
    output_dir: str = "frames",
    diff_opacity: float = 0.25,
    output_upscale_factor: int = 8,
):
    prev_frame = Image.new("P", POKETCH_SCREEN_SIZE, color=(0, 0, 0))
    palette = get_palette(POKETCH_PALETTE)

    for frame, count, total in get_video_frames(input_path, resize=POKETCH_SCREEN_SIZE):
        print(f"Read a new frame: {count + 1}/{total}")
        frame_quantized = quantize(frame, palette)
        diff = difference(prev_frame, frame_quantized, diff_opacity)

        output_path = Path(output_dir) / f"{count:04d}.png"
        if output_type == OutputType.FRAMES:
            upscale(frame_quantized, output_upscale_factor).save(output_path)
        elif output_type == OutputType.DIFF:
            upscale(diff, output_upscale_factor).save(output_path)
        elif output_type == OutputType.BOTH:
            stacked = stack(frame_quantized, diff)
            upscale(stacked, output_upscale_factor).save(output_path)

        prev_frame = frame_quantized


if __name__ == "__main__":
    main(output_type=OutputType.BOTH)