# Pokétch Video Player

Video player for the 'Dot Artist' Pokétch app from Pokémon DPPt. It works by generating [DeSmuME](http://desmume.org/) Lua scripts for manipulating the memory region corresponding to the app's screen data.

The app's screen is composed of a 24x20 pixel grid of 8x8 pixel tiles. Each tile can have four different colors, which alternate by touching each pixel.

## Usage

This script currently only works on Pokémon Platinum, US version. It may work on other versions, but it's unlikely due to different memory mappings.

### Prerequisites

-   [DeSmuME](http://desmume.org/) (tested with 0.9.13)
-   [Python 3](https://www.python.org/downloads/) (tested with 3.10.4)
-   [Poetry](https://python-poetry.org/) (tested with 1.1.13)
-   [OpenCV](https://opencv.org/) (tested with 4.1.0)
-   [Pillow](https://pillow.readthedocs.io/en/stable/) (tested with 6.0.0)

### Generating the script

1. Get a copy of the video and move it to the root folder as `source.mp4`.
1. Run `python3 main.py` to generate the script.

### Running

1. Install [DeSmuME](http://desmume.org/).
1. Download Lua binaries for DeSmuME from [here](https://sourceforge.net/projects/luabinaries/files/5.1.4/Windows%20Libraries/) (make sure to match the architecture of your DeSmuME installation).
1. Move `lua51.dll` and `lua5.1.dll` to the same folder as the DeSmuME executable.
1. Open DeSmuME and load Pokémon Platinum.
1. Open the 'Dot Artist' Pokétch app.
1. Open the Lua scripting menu (Tools > Lua Scripting > New Lua Script Window...).
1. Open the generated script and click 'Run'.
1. Watch the magic happen!
