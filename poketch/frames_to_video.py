import glob

import cv2
import numpy as np
from PIL import Image

frameSize = (192, 320)

out = cv2.VideoWriter(
    "output_video.avi", cv2.VideoWriter_fourcc(*"DIVX"), 30, frameSize
)

for filename in glob.glob("frames/*.png"):
    print(filename)
    img = Image.open(filename)
    img = img.resize(frameSize, Image.NEAREST)
    bg = Image.new("RGB", frameSize, (240, 240, 240))
    bg.paste(img, (0, 0), img)
    frame = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
    # frame = cv2.imread(filename)
    out.write(frame)

out.release()
