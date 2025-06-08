# PyBonsai➕ 🌴

PyBonsai+ is a Python script that generates procedural ASCII art trees in the comfort of your terminal.

## Features 🌱

This is a fork of [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai) with some additional features.

- Simple package installation
- Better CLI experience
- Infinite mode

About other features read more in [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai).

## Installation 🔗

### Requirements:

- Python 3.9 or greater

### Recommended 

Use [pipx](https://pipx.pypa.io/stable/installation/) to install PyBonsai+ globally.

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
git clone https://github.com/Ben-Edwards44/PyBonsai.git
cd PyBonsai
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
    -w, --wait            time delay between drawing characters when not in instant mode [default 0]

    -c, --branch-chars    string of chars randomly chosen for branches [default "~;:="]
    -C, --leaf-chars      string of chars randomly chosen for leaves [default "&%#@"]

    -x, --width           maximum width of the tree [default 80]
    -y, --height          maximum height of the tree [default 25]

    -t, --type            tree type: integer between 0 and 3 inclusive [default random]
    -S, --start-len       length of the root branch [default 15]
    -L, --leaf-len        length of each leaf [default 4]
    -l, --layers          number of branch layers: more => more branches [default 8]
    -a, --angle           mean angle of branches to their parent, in degrees; more => more arched trees [default 40]

    -f, --fixed-window    do not allow window height to increase when tree grows off screen
    
    -I, --infinite        run in infinite mode, infinitely growing same tree
    -n, --new             run in infinite mode, automatically growing new trees
    -W, --wait-infinite   time delay between drawing in infinite mode [default 5]
```

The following images demonstrate the use of the different options:

| Effect               | Image                                              |
| -------------------- | -------------------------------------------------- |
| Big tree             | ![big tree](/Images/options/big.png)               |
| Different characters | ![different characters](/Images/options/chars.png) |
| Longer leaves        | ![longer leaves](/Images/options/leafy.png)        |

## Tree Types :leaves:

PyBonsai supports 4 different tree types. Unless specified with the `--type` option, the tree type will be chosen at random.

All tree types are generated recursively and are, essentially, variations on [this](https://www.youtube.com/watch?v=0jjeOYMjmDU) basic fractal tree.

| Type             | Image                                       | Description                                                                                                              |
| ---------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Classic          | ![classic](/Images/types/classic.png)       | The number of child branches is normally distributed with $\mu = 2$ and $\sigma = 0.5$.                                  |
| Fibonacci        | ![fib](/Images/types/fib.png)               | The number of branches on the $n^{th}$ layer is the $n^{th}$ fibonacci number.                                           |
| Offset fibonacci | ![offset fib](/Images/types/offset_fib.png) | Similar to above, except child branches grow in the middle of the parent as well as the end.                             |
| Random fibonacci | ![random fib](/Images/types/rand_fib.png)   | Similar to above, except child branches grow at random positions on the parent and leaves can grow in the middle layers. |
