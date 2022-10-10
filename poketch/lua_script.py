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
            if i == len(changes) - 1:
                # Touch the last pixel to trigger a redraw
                tx, ty = (SCREEN_OFFSET_PX[0] + (x * 8), SCREEN_OFFSET_PX[1] + (y * 8))
                tcolor = color - 1
                if tcolor < 0:
                    tcolor = 3
                script.append(f"  memory.writebyte({address}, {tcolor})")
                script.append(
                    f"  stylus.write{{touch=false}} emu.frameadvance() emu.frameadvance()"
                )
                script.append(
                    f"  stylus.write{{{tx}, {ty}, touch=true}} emu.frameadvance() emu.frameadvance()"
                )
                script.append(f'  print("Touching {tx}, {ty}")')
        script.append("end")
        script.append("")

    # Frame table
    script.append("local frames = {")
    for frame in diffs.keys():
        script.append(f"  [{frame}] = f{frame},")
    script.append("}")
    script.append("")

    # Main loop
    script.append("start = emu.framecount()")
    script.append("while true do")
    script.append("  frame = emu.framecount()")
    script.append("  current = frame - start")
    script.append("  local func = frames[current]")
    script.append("    if (func) then")
    script.append('      print("Playing frame", current)')
    script.append("      func()")
    script.append("    end")
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
