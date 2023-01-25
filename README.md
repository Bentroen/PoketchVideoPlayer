# Pokétch Video Player

<p align="center">
     <img src="https://user-images.githubusercontent.com/29354120/214530159-06652ae1-4875-4c30-b067-0e61c98159d6.png" width="500">
</p>

Video player for the 'Dot Artist' Pokétch app from Pokémon DPPt. It works by generating [DeSmuME](http://desmume.org/) Lua scripts for manipulating the memory region corresponding to the app's screen data.

The app's screen is composed of a 24x20 pixel grid of 8x8 pixel tiles. Each tile can have four different colors, which alternate by touching each pixel.

[(Demo video)](https://youtu.be/_p1q9_shSTw)

## Usage

This script currently only works on Pokémon Platinum, US version. It may work on other versions, but it's unlikely due to different memory mappings.

### Prerequisites

-   [DeSmuME](http://desmume.org/) (tested with 0.9.13)
-   [Python 3](https://www.python.org/downloads/)
-   [Poetry](https://python-poetry.org/)
-   [OpenCV](https://opencv.org/)
-   [Pillow](https://pillow.readthedocs.io/en/stable/)

### Generating the script

1. Get a copy of the video and move it to the root folder as `source.mp4`.
1. Make sure to have [poetry](https://python-poetry.org) installed, and run:

    ```shell
    $ poetry install
    ```

1. To generate the script, run:

    ```shell
    $ python3 poketch <source>
    ```

> Tip: A number of options are available during generation. Run `python3 poketch --help` to see them.

### Running

1. Install [DeSmuME](http://desmume.org/).
1. Download Lua binaries for DeSmuME from [here](https://sourceforge.net/projects/luabinaries/files/5.1.4/Windows%20Libraries/) (make sure to match the architecture of your DeSmuME installation).
1. Move `lua51.dll` and `lua5.1.dll` to the same folder as the DeSmuME executable.
1. Open DeSmuME and load Pokémon Platinum.
1. Open the 'Dot Artist' Pokétch app.
1. Open the Lua scripting menu (Tools > Lua Scripting > New Lua Script Window...).
1. Open the generated script and click 'Run'.
1. Watch the magic happen!
