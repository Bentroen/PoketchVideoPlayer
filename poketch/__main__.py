import sys
from typing import Optional

from lua_script import *
from video_processing import *


def help():
    print(f"Usage: python3 {sys.argv[0]} <input_path> <output_path> [options]")
    print("Options:")
    print("  -h, --help   : Show this help message")
    print("  -n, --noise  : Set the number of frames to show noise for (default: 30)")
    print(
        "  -o, --output : Set the frame output type [none, frames, diff, both] (default: none)"
    )
    print("  -d, --dir    : Set the directory to output frames to (default: frames)")
    print("  -u, --upscale: Set the factor to upscale frames by (default: 8)")
    print("  -o, --opacity: Set the opacity of the diff overlay (default: 0.25)")


def argparse(arg: str, default: str, short: Optional[str] = None):
    if arg in sys.argv:
        return sys.argv[sys.argv.index(arg) + 1]
    elif short and short in sys.argv:
        return sys.argv[sys.argv.index(short) + 1]
    else:
        return default


def main():
    if len(sys.argv) < 3 or "-h" in sys.argv or "--help" in sys.argv:
        help()
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    noise_frames = int(argparse(arg="-n", short="--noise", default="30"))
    output_type = OutputType[
        argparse(arg="-o", short="--output", default="none").upper()
    ]
    output_dir = argparse(arg="-d", short="--dir", default="frames")
    output_upscale_factor = int(argparse(arg="-u", short="--upscale", default="8"))
    diff_opacity = float(argparse(arg="-o", short="--opacity", default="0.25"))

    try:
        import progressbar
    except ImportError:
        progressbar = None

    print(f"Processing video {input_path}")

    if progressbar:
        frame_count = get_video_frame_count(sys.argv[1])
        bar = progressbar.ProgressBar(max_value=frame_count)
    else:
        bar = None

    diffs = process(
        input_path,
        output_type=output_type,
        output_dir=output_dir,
        diff_opacity=diff_opacity,
        output_upscale_factor=output_upscale_factor,
        progress=bar,
    )

    print("Generating script...")
    script = generate_script(diffs, noise_frames=noise_frames)
    with open(output_path, "w") as f:
        f.write("\n".join(script))
    print(f"Saved script to {output_path}")
    print("Done!")


if __name__ == "__main__":
    main()
