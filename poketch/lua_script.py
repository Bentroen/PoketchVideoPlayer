from typing import Dict, Sequence

import video_processing

TOP_LEFT_ADDRESS = 0x0238F9E8

SCREEN_SIZE = (24, 20)
SCREEN_SIZE_PX = (192, 160)
SCREEN_OFFSET_PX = (16, 16)

COLOR_LUT = [1, 2, 3, 0]


def get_memory_address(x: int, y: int) -> str:
    return hex(TOP_LEFT_ADDRESS + (y * SCREEN_SIZE[0]) + x)


def generate_script(diffs: Dict[int, Sequence[tuple[int, int, int]]]):
    script = []

    # Frame switching functions
    for frame, changes in diffs.items():
        script.append(f"f{frame} = function ()")
        for i, (x, y, color) in enumerate(changes):
            address = get_memory_address(x, y)
            script.append(f"  memory.writebyte({address}, {COLOR_LUT[color]})")
        script.append("end")
        script.append("")

    # Frame table
    script.append("local frames = {")
    for frame in diffs.keys():
        script.append(f"  [{frame}] = f{frame},")
    script.append("}")
    script.append("")

    # Main loop
    script.append("local l = 0")
    script.append("start = emu.framecount()")
    script.append("while true do")
    script.append("  frame = emu.framecount()")
    script.append("  current = (frame - start) / 2")
    script.append("  local func = frames[current]")
    script.append("    if (func) then")
    script.append('      print("Playing frame", current)')
    script.append("      func()")
    script.append("    end")
    script.append("  l = l + 0.5")
    script.append("  if l >= 2 then")
    script.append("    l = 0")
    script.append("  end")
    script.append("  stylus.set{x=192 + l * 8, y=168, touch=true}")
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
