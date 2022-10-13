import argparse

from lua_script import *
from video_processing import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", help="Path to the input video")
    parser.add_argument("output_path", help="Path to the output video")
    parser.add_argument(
        "-t",
        "--output",
        help="Set the frame output type [none, frames, diff, both] (default: none)",
        type=str,
        default="none",
        choices=["none", "frames", "diff", "both"],
    )
    parser.add_argument(
        "-d",
        "--dir",
        help="Set the directory to output frames to (default: frames)",
        type=str,
        default="frames",
    )
    parser.add_argument(
        "-u",
        "--upscale",
        help="Set the factor to upscale frames by (default: 8)",
        type=int,
        default=8,
    )
    parser.add_argument(
        "-o",
        "--opacity",
        help="Set the opacity of the diff overlay (default: 0.25)",
        type=float,
        default=0.25,
    )
    parser.add_argument(
        "-n",
        "--noise",
        help="Set the number of frames to show noise for (default: 30)",
        type=int,
        default=30,
    )
    args = parser.parse_args()

    try:
        import progressbar
    except ImportError:
        progressbar = None

    print(f"Processing video {args.input_path}")

    if progressbar:
        frame_count = get_video_frame_count(args.input_path)
        bar = progressbar.ProgressBar(max_value=frame_count)
    else:
        bar = None

    diffs = process(
        args.input_path,
        output_type=OutputType[args.output.upper()],
        output_dir=args.dir,
        diff_opacity=args.opacity,
        output_upscale_factor=args.upscale,
        progress=bar,
    )

    print("Generating script...")
    script = generate_script(diffs, noise_frames=args.noise)
    with open(args.output_path, "w") as f:
        f.write("\n".join(script))
    print(f"Saved script to {args.output_path}")
    print("Done!")


if __name__ == "__main__":
    main()
