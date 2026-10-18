# PyBonsai-CLI

PyBonsai is a Python script that generates procedural ASCII art trees in the comfort of your terminal.

## Features 🌱

This is a fork of [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai) with some additional features.

- Simple package installation 📦
- Better CLI experience 💻
- Infinite mode 🔄
- Save to text files 📄
-  True bonsai 🌳
-  Preset change 🎨
-  Falling leaves animation 🍃
-  Lofi radio 📻 [UPDATED] ✨

About other features read more on [examples.md](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/examples.md).

## Installation 🔗

### Requirements:

- Python 3.9 or greater
- For YouTube radio: Python 3.10+, FFmpeg (`ffplay`), and Deno 2.3+ or Node.js 22+

### Recommended 

Use [pipx](https://pipx.pypa.io/stable/installation/) to install PyBonsai globally.

```
pipx install pybonsai
```

or using [uv](https://docs.astral.sh/uv/) to install in temporary, isolated environment:

```
uvx pybonsai
```

### Alternative

Also can be installed using [pip](https://pip.pypa.io/):

```
pip install pybonsai
```

or build from source:

```
git clone https://github.com/DaEtoJostka/PyBonsai-CLI.git
cd PyBonsai-CLI
pip install .
```

Verify the installation by running:

```
pybonsai --version
```


## Usage 🔧

Run `pybonsai --help` for usage:

```
OPTIONS:
    -h, --help            display help
        --version         display version

    -s, --seed            seed for the random number generator

    -i, --instant         instant mode: display finished tree immediately
    -w, --wait            time delay between drawing characters when not in instant mode [default {Options.WAIT_TIME}]

    -c, --branch-chars    string of chars randomly chosen for branches [default "{Options.BRANCH_CHARS}"]
    -C, --leaf-chars      string of chars randomly chosen for leaves [default "{Options.LEAF_CHARS}"]

    -x, --width           maximum width of the tree [default {Options.WINDOW_WIDTH}]
    -y, --height          maximum height of the tree [default {Options.WINDOW_HEIGHT}]

    -t, --type            tree type [0-3]: "classic":0, "fibonacci":1, "offset fibonacci":2, "random fibonacci":3 [default random]
    -b, --bonsai          enable bonsai preset settings (invokes specific defaults for small tree)
    -S, --start-len       length of the root branch [default {Options.INITIAL_LEN}]
    -L, --leaf-len        length of each leaf [default {Options.LEAF_LEN}]
    -l, --layers          number of branch layers: more => more branches [default {Options.NUM_LAYERS}]
    -a, --angle           mean angle of branches to their parent, in degrees; more => more arched trees [default {Options.ANGLE_MEAN}]

    -o, --save PATH       save the tree to a text file. If only a filename is provided, it will be saved in a user's Downloads directory.
    -f, --fixed-window    do not allow window height to increase when tree grows off screen
    
    -I, --infinite        run in infinite mode, infinitely growing same tree
    -n, --new             run in infinite mode, automatically growing new trees
    -W, --wait-infinite   time delay between drawing in infinite mode [default {Options.INFINITE_WAIT_TIME}]

    -p, --preset           apply a color preset: {", ".join(colors.PRESETS.keys())}
    -B, --branch-color     custom color for branches (e.g. "red", "#553311", "100,60,30")
    -e, --leaf-color       custom color for leaves
    -g, --soil-color       custom color for soil

    -F, --leaves-falling   animate leaves falling from the tree continuously
    -N, --intensity        intensity of falling leaves [1-10, default {Options.INTENSITY}]
    -d, --fall-speed       speed of falling animation [default {Options.FALL_SPEED}]
    -T, --tumbling-speed   speed of leaf character change [default {Options.TUMBLING_SPEED}]
    -K, --falling-chars    custom characters for falling leaves (e.g. "01" for matrix-style)

    -R, --lofi [PRESET]    play a terminal radio preset; presets: lofi (default), classical (alias: 0), medieval (alias: 1), synthwave (alias: 2), sad (alias: 3), jazz (alias: 4)
    -V, --volume           volume level for radio [0-100, default {Options.VOLUME}]
    -U, --radio-url        custom radio stream URL
```

Other options usage examples see [examples.md](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/examples.md)

### Radio

Radio needs FFmpeg's `ffplay` on your PATH. YouTube presets also need Python 3.10+
and Deno 2.3+ or Node.js 22+ on PATH. Both runtimes are detected automatically.
The Python dependencies include current `yt-dlp` and its JavaScript components
(`yt-dlp[default]`), plus Streamlink for other supported sites. Direct audio URLs
do not require a JavaScript runtime.

From a source checkout, update the environment before testing:

```sh
uv sync
uv run python -m pybonsai -R 2
```

On macOS, missing system dependencies can be installed with `brew install ffmpeg deno`.
If a supported Node.js is already installed, you only need FFmpeg.

```sh
pybonsai -R       # lo-fi
pybonsai -R 2     # synthwave
pybonsai -R 3     # sad lo-fi
pybonsai -U 'https://example.com/live.mp3'  # your own stream
```

Playback reconnects automatically after a stream ends or a network request fails.
Decoded audio frames are monitored as well: if no frames arrive for 15 seconds,
the player is restarted even when its process and network connection are still
running. Initial audio startup is limited to 45 seconds. The monitor tracks frames,
so quiet music or silence within a working broadcast does not trigger a restart.
YouTube's temporary media URL is resolved again on each restart. Repeated failures
use increasing delays, up to 30 seconds. Press Ctrl+C to stop both the animation
and radio, including pending retries. If playback could not recover, the last
error is printed when the animation stops.

YouTube broadcasts can move to new video URLs. If a station stays unavailable,
check its broadcast page and use `--radio-url` with its current URL. Keep `yt-dlp`
updated in the same environment as PyBonsai; for a source checkout using uv, run
`uv sync --upgrade-package yt-dlp`. Old YouTube clients can return a playable URL
whose segments start failing with HTTP 403 shortly afterwards, so a successful
startup alone is not enough to validate an old `yt-dlp` version. See the
[yt-dlp JavaScript setup guide](https://github.com/yt-dlp/yt-dlp/wiki/EJS) for runtime
and component requirements.

To build a wheel, run `uv build --wheel`; the package is written to `dist/`.
Run the tests with `uv run python -m unittest discover -s tests -v`. The local
playback recovery test requires both `ffmpeg` and `ffplay` and uses a dummy audio
device, without internet access or speaker output.

## Like it?

If you like this project, please consider giving it a ⭐️ on [GitHub](https://github.com/DaEtoJostka/PyBonsai-CLI)

Also don't forget to check out [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai)
## Contributing

If you want to contribute to this project, please feel free to submit a pull request.

## License
[MIT license](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/LICENSE)
