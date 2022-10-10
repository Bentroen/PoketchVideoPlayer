from typing import Dict, Sequence

import video_processing

TOP_LEFT_ADDRESS = 0x0238F9E8

SCREEN_SIZE = (24, 20)
SCREEN_SIZE_PX = (192, 160)


def get_memory_address(x: int, y: int) -> str:
    return hex(TOP_LEFT_ADDRESS + (y * SCREEN_SIZE[1]) + x)


def generate_script(diffs: Dict[int, Sequence[tuple[int, int, int]]]):
    script = []

    script.append("start = emu.framecount()")
    script.append("while true do")
    script.append("  frame = emu.framecount()")
    script.append("  current = frame - start")

    for frame, changes in diffs.items():
        script.append(f"  if current == {frame} then")
        for x, y, color in changes:
            address = get_memory_address(x, y)
            script.append(f"    memory.writebyte({address}, {color})")
        script.append("  end")

    script.append("  emu.frameadvance()")
    script.append("end")

    return script


if __name__ == "__main__":
    import progressbar

    diffs = video_processing.process(
        input_path="source.mp4",
        progress=progressbar.ProgressBar(max_value=progressbar.UnknownLength),
    )
    script = generate_script(diffs)
    with open("script.lua", "w") as f:
        f.write("\n".join(script))
