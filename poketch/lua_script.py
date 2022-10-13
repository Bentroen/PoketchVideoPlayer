from typing import Dict, Sequence

TOP_LEFT_ADDRESS = 0x0238F9E8

SCREEN_SIZE = (24, 20)
SCREEN_SIZE_PX = (192, 160)
SCREEN_OFFSET_PX = (16, 16)

NOISE_FRAMES = 30


def get_memory_address(x: int, y: int) -> str:
    return hex(TOP_LEFT_ADDRESS + (y * SCREEN_SIZE[0]) + x)


def wrap(value: int, min: int, max: int) -> int:
    if value < min:
        return max
    elif value > max:
        return min
    return value


def generate_script(diffs: Dict[int, Sequence[tuple[int, int, int]]]):
    script = []

    # Random noise function
    script.append("function noise()")
    script.append(f"  for y = 0, {SCREEN_SIZE[1] - 1} do")
    script.append(f"    for x = 0, {SCREEN_SIZE[0] - 1} do")
    script.append(
        f"      memory.writebyte({TOP_LEFT_ADDRESS} + y * {SCREEN_SIZE[0]} + x, math.random(1, 3))"
    )
    script.append("    end")
    script.append("  end")
    script.append("br1 = math.random(1, 2)")
    script.append("br2 = math.random(1, 2)")
    script.append("end")

    # Frame switching functions
    for frame, changes in diffs.items():
        script.append(f"f{frame} = function ()")
        for x, y, color in changes:
            color += 1  # Color memory values range from 1-4, not 0-3
            address = get_memory_address(x, y)
            script.append(f"  memory.writebyte({address}, {color})")
            # Store color of the two last pixels, minus one, for touch correction
            if y == SCREEN_SIZE[1] - 1:
                if x == SCREEN_SIZE[0] - 1:
                    script.append(f"  br1 = {wrap(color - 1, 1, 4)}")
                elif x == SCREEN_SIZE[0] - 2:
                    script.append(f"  br2 = {wrap(color - 1, 1, 4)}")
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
    script.append("br1 = 0")
    script.append("br2 = 0")
    script.append("start = emu.framecount()")
    script.append("while true do")
    script.append("  frame = emu.framecount()")
    script.append("  current = (frame - start) / 2")
    script.append(f"  if current <= {NOISE_FRAMES} then")
    script.append("    noise()")
    script.append("  else")
    script.append(f"    local func = frames[current - {NOISE_FRAMES + 1}]")
    script.append("      if (func) then")
    script.append('        print("Playing frame", current)')
    script.append("        func()")
    script.append("      end")
    script.append("  end")
    script.append("  l = l + 4")
    script.append("  if l >= 16 then l = 0 end")
    # Touch screen to trigger redraw (we set the pixels one step behind what
    # they should be in, so that the touch leaves them in the correct state)
    bottom_right_address1 = get_memory_address(SCREEN_SIZE[0] - 1, SCREEN_SIZE[1] - 1)
    bottom_right_address2 = get_memory_address(SCREEN_SIZE[0] - 2, SCREEN_SIZE[1] - 1)
    script.append("  if l >= 8 then")
    script.append(f"    memory.writebyte({bottom_right_address1}, br1)")
    script.append("  else")
    script.append(f"    memory.writebyte({bottom_right_address2}, br2)")
    script.append("  end")
    script.append("  stylus.set{x=192 + l, y=168, touch=true}")
    script.append("  emu.frameadvance()")
    script.append("end")

    return script


if __name__ == "__main__":
    import json

    with open("diffs.json") as f:
        diffs = json.load(f)

    script = generate_script(diffs)

    with open("script.lua", "w") as f:
        f.write("\n".join(script))
