import cv2
from pathlib import Path
from PIL import Image, ImageChops
import numpy as np


#### Code taken from: https://stackoverflow.com/a/16721373/9045426 ####
point_table = [0] + ([255] * 255)
checkerboard = Image.open("checkerboard.png")


def black_or_b(a, b):
    diff = ImageChops.difference(a, b)
    diff = diff.convert("L")
    diff = diff.point(point_table)
    new = diff.convert("RGBA")
    new.paste(b, mask=diff)

    final = checkerboard.copy()
    final.paste(new, mask=diff)

    final2 = b.copy().convert("RGBA")
    final2.putalpha(64)
    final2.paste(a, mask=diff)

    return final2


color_bands = 4
threshold = 255 / (color_bands - 1)

vidcap = cv2.VideoCapture("source.mp4")
success, img = vidcap.read()
count = 0

prev_frame = None


palette_data = [112, 176, 112, 80, 128, 80, 56, 80, 40, 16, 40, 24]
palette = Image.new("P", (16, 16))
palette.putpalette(palette_data * 64)
palette.save("palette.png")

while success:
    success, img = vidcap.read()
    resized = cv2.resize(img, (24, 20), interpolation=cv2.INTER_AREA)
    # cv2.imwrite(str(Path("output", f"{count}.jpg")), resized)
    print("Read a new frame:", count + 1)
    count += 1

    img_converted = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_converted)

    # quantized = img_pil.convert("L", palette=Image.ADAPTIVE, colors=2)")

    quantized = img_pil.quantize(colors=4, dither=Image.Dither.NONE, palette=palette)

    # converted = img_pil.convert("L")
    # quantized = converted.point(lambda x: round(x // threshold * threshold))

    quantized.resize((192, 160), Image.Resampling.NEAREST).save(
        str(Path("output", f"{count}.png"))
    )

    # Calculate diff

    if prev_frame is not None:
        diff = black_or_b(quantized, prev_frame)
        diff.resize((192, 160), Image.Resampling.NEAREST).save(
            str(Path("diff", f"{count}_diff.png"))
        )

        output_diff = Image.new("RGBA", (24, 20 * 2))
        output_diff.paste(quantized, (0, 0))
        output_diff.paste(diff, (0, 20))
        output_diff.resize((192, 160 * 2), Image.Resampling.NEAREST).save(
            str(Path("output_diff", f"{count}.png"))
        )

    prev_frame = quantized
