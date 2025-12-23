# PyBonsai-CLI 🌴

PyBonsai is a Python script that generates procedural ASCII art trees in the comfort of your terminal.

## Features 🌱

This is a fork of [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai) with some additional features.

- Simple package installation 📦
- Better CLI experience 💻
- Infinite mode 🔄
- Save to text files 📄
- [NEW] ✨ True bonsai 🌳
- [NEW] ✨ Preset change 🎨
- [NEW] ✨ Falling leaves animation 🍃
- [NEW] ✨ Lofi radio 📻

About other features read more on [examples.md](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/examples.md).

## Installation 🔗

### Requirements:

- Python 3.9 or greater

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

    -p, --preset          [NEW] ✨ apply a color preset: {", ".join(colors.PRESETS.keys())}
    -B, --branch-color    [NEW] ✨ custom color for branches (e.g. "red", "#553311", "100,60,30")
    -e, --leaf-color      [NEW] ✨ custom color for leaves
    -g, --soil-color      [NEW] ✨ custom color for soil

    -F, --leaves-falling  [NEW] ✨ animate leaves falling from the tree continuously
    -N, --intensity       [NEW] ✨ intensity of falling leaves [1-10, default {Options.INTENSITY}]
    -d, --fall-speed      [NEW] ✨ speed of falling animation [default {Options.FALL_SPEED}]
    -T, --tumbling-speed  [NEW] ✨ speed of leaf character change [default {Options.TUMBLING_SPEED}]
    -K, --falling-chars   [NEW] ✨ custom characters for falling leaves (e.g. "01" for matrix-style)

    -R, --lofi            [NEW] ✨ play Lo-Fi radio stream in the terminal (requires ffplay)
    -V, --volume          [NEW] ✨ volume level for radio [0-100, default {Options.VOLUME}]
    -U, --radio-url       [NEW] ✨ custom radio stream URL
```

Other options usage examples see [examples.md](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/examples.md)

## Like it?

If you like this project, please consider giving it a ⭐️ on [GitHub](https://github.com/DaEtoJostka/PyBonsai-CLI)

Also don't forget to check out [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai)
## Contributing

If you want to contribute to this project, please feel free to submit a pull request.

## License
[MIT license](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/LICENSE)
