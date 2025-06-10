# PyBonsai-CLI 🌴

PyBonsai is a Python script that generates procedural ASCII art trees in the comfort of your terminal.
<pre style="background-color: #2d3142; color: #d4d4d4; font-family: monospace; line-height: 1.2; font-size: 14px; padding: 1em;">
                                                        <span style="color: #b5cea8;">#</span>
                                                    <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%%&amp;#@&amp;</span>
                                    <span style="color: #b5cea8;">##</span><span style="color: #808080;">%</span>              <span style="color: #dcdcaa;">\</span><span style="color: #6a9955;">&amp;</span><span style="color: #b5cea8;">%#</span><span style="color: #6a9955;">%&amp;</span><span style="color: #b5cea8;">#</span><span style="color: #6a9955;">%%</span><span style="color: #b5cea8;">#@</span>
                       <span style="color: #b5cea8;">#</span><span style="color: #6a9955;">%</span><span style="color: #b5cea8;">@&amp;@</span><span style="color: #b5cea8;">#</span>    <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%&amp;&amp;</span><span style="color: #dcdcaa;">:</span><span style="color: #6a9955;">&amp;%%</span><span style="color: #b5cea8;">#&amp;</span>         <span style="color: #6a9955;">&amp;</span><span style="color: #b5cea8;">#@</span><span style="color: #dcdcaa;">_/</span><span style="color: #6a9955;">&amp;&amp;</span><span style="color: #b5cea8;">#@#</span> <span style="color: #6a9955;">&amp;</span>
                         <span style="color: #6a9955;">&amp;</span><span style="color: #b5cea8;">@@</span><span style="color: #6a9955;">%</span><span style="color: #b5cea8;">@&amp;</span>  <span style="color: #6a9955;">&amp;</span><span style="color: #b5cea8;">@&amp;&amp;@@</span><span style="color: #6a9955;">%&amp;</span><span style="color: #b5cea8;">@@</span><span style="color: #6a9955;">%</span>        <span style="color: #808080;">%#</span> <span style="color: #b5cea8;">@@@@#@&amp;</span>
                  <span style="color: #6a9955;">@%</span>  <span style="color: #b5cea8;">#%#%@@@%</span>  <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%#&amp;@@&amp;##@@@#</span>          <span style="color: #dcdcaa;">|</span><span style="color: #808080;">%</span> <span style="color: #6a9955;">&amp;&amp;@</span>
             <span style="color: #6a9955;">%%#&amp;%@#</span>  <span style="color: #b5cea8;">@#</span><span style="color: #dcdcaa;">~</span><span style="color: #6a9955;">%&amp;%%#%</span>   <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%%&amp;@&amp;#</span> <span style="color: #6a9955;">%%#</span>          <span style="color: #dcdcaa;">|</span>
            <span style="color: #6a9955;">%#&amp;&amp;</span>      <span style="color: #b5cea8;">@@</span><span style="color: #6a9955;">%%%#&amp;@&amp;%@</span> <span style="color: #6a9955;">%%</span><span style="color: #dcdcaa;">|</span><span style="color: #b5cea8;">%###</span><span style="color: #6a9955;">&amp;%_=\</span> <span style="color: #6a9955;">%&amp;</span>       <span style="color: #dcdcaa;">|</span>
              <span style="color: #b5cea8;">#@</span><span style="color: #dcdcaa;">|</span> <span style="color: #6a9955;">&amp;%</span> <span style="color: #6a9955;">&amp;</span><span style="color: #b5cea8;">@% @#</span> <span style="color: #6a9955;">%#</span> <span style="color: #6a9955;">&amp;</span> <span style="color: #6a9955;">&amp;%#</span><span style="color: #dcdcaa;">|</span><span style="color: #b5cea8;">@</span>  <span style="color: #b5cea8;">@@</span> <span style="color: #6a9955;">&amp;&amp;@%&amp;&amp;&amp;</span>      <span style="color: #dcdcaa;">; =__=</span>
              <span style="color: #6a9955;">&amp;@###_#@</span>  <span style="color: #b5cea8;">#</span>   <span style="color: #b5cea8;">@</span> <span style="color: #6a9955;">&amp;</span> <span style="color: #b5cea8;">@&amp;</span><span style="color: #dcdcaa;">/</span><span style="color: #b5cea8;">#</span> <span style="color: #b5cea8;">@</span>     <span style="color: #b5cea8;">#</span><span style="color: #6a9955;">%@%&amp;@%@</span>    <span style="color: #dcdcaa;">__~</span><span style="color: #b5cea8;">#@@</span> <span style="color: #6a9955;">%#&amp;@%%##&amp;&amp;</span>
          <span style="color: #6a9955;">&amp;#</span>  <span style="color: #6a9955;">%##%</span><span style="color: #dcdcaa;">_</span><span style="color: #b5cea8;">%</span><span style="color: #6a9955;">##</span><span style="color: #dcdcaa;">%;</span>        <span style="color: #6a9955;">&amp;</span> <span style="color: #dcdcaa;">~</span> <span style="color: #6a9955;">%</span>     <span style="color: #6a9955;">%@##%</span> <span style="color: #b5cea8;">@</span>  <span style="color: #b5cea8;">@</span> <span style="color: #6a9955;">&amp;@&amp;&amp;@</span>  <span style="color: #b5cea8;">#</span>  <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%#@&amp;#@</span>
        <span style="color: #6a9955;">%##&amp;%&amp;#@@</span><span style="color: #dcdcaa;">\</span>  <span style="color: #6a9955;">%##</span> <span style="color: #dcdcaa;">~\</span>        <span style="color: #dcdcaa;">|</span>        <span style="color: #6a9955;">&amp;@</span>  <span style="color: #6a9955;">&amp;</span> <span style="color: #dcdcaa;">_____</span> <span style="color: #dcdcaa;">_</span><span style="color: #dcdcaa;">|</span><span style="color: #b5cea8;">#&amp;&amp;&amp;@#@@##@</span> <span style="color: #b5cea8;">#</span>
         <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%&amp;#@@#@#</span><span style="color: #dcdcaa;">\/_#_///___;_=_=\:</span>   <span style="color: #6a9955;">%&amp;</span>     <span style="color: #dcdcaa;">/:</span>        <span style="color: #dcdcaa;">~</span> <span style="color: #6a9955;">&amp;##%#&amp;%%#&amp;&amp;</span>
        <span style="color: #b5cea8;">@</span><span style="color: #6a9955;">%&amp;@@%%@%@#&amp;&amp;%</span><span style="color: #dcdcaa;">~/_</span>          <span style="color: #dcdcaa;">\:~\</span>  <span style="color: #b5cea8;">@</span>    <span style="color: #dcdcaa;">/:</span>          <span style="color: #dcdcaa;">||</span><span style="color: #b5cea8;">#@#&amp;&amp;</span> <span style="color: #b5cea8;">@</span>
          <span style="color: #b5cea8;">@@@@#&amp;%&amp;&amp;#&amp;@#&amp;</span>             <span style="color: #dcdcaa;">==\</span><span style="color: #b5cea8;">@&amp;%@</span> <span style="color: #dcdcaa;">//</span>         <span style="color: #6a9955;">&amp;%%</span> <span style="color: #6a9955;">%</span><span style="color: #b5cea8;">@#</span> <span style="color: #6a9955;">%</span>
          <span style="color: #b5cea8;">######</span><span style="color: #6a9955;">%#%</span><span style="color: #b5cea8;">##</span><span style="color: #6a9955;">%</span><span style="color: #b5cea8;">#</span> <span style="color: #b5cea8;">@</span>              <span style="color: #6a9955;">%</span><span style="color: #dcdcaa;">\\</span><span style="color: #b5cea8;">###</span><span style="color: #6a9955;">&amp;</span>         <span style="color: #6a9955;">&amp;%&amp;@#</span>   <span style="color: #b5cea8;">#</span>
            <span style="color: #b5cea8;">@</span> <span style="color: #6a9955;">%%%%#</span>                    <span style="color: #b5cea8;">@</span> <span style="color: #dcdcaa;">\=#:</span>       <span style="color: #6a9955;">%#@#</span><span style="color: #dcdcaa;">=</span><span style="color: #b5cea8;">@@#@</span>
             <span style="color: #b5cea8;">@</span>   <span style="color: #6a9955;">%#</span>                       <span style="color: #dcdcaa;">|:|</span>       <span style="color: #6a9955;">&amp;#</span> <span style="color: #6a9955;">&amp;%&amp;%&amp;</span>
                  <span style="color: #b5cea8;">#</span>                        <span style="color: #dcdcaa;">|||</span>        <span style="color: #b5cea8;">#</span>   <span style="color: #6a9955;">%#&amp;</span>
                                           <span style="color: #dcdcaa;">;;;</span>
                                            <span style="color: #dcdcaa;">::|</span>
                              <span style="color: #d4d4d4;">\</span><span style="color: #6a9955;">.--.__.-._..</span><span style="color: #dcdcaa;">/</span><span style="color: #dcdcaa;">:</span><span style="color: #dcdcaa;">||\..</span><span style="color: #d4d4d4;">__________/</span>
                               <span style="color: #d4d4d4;">\</span>             <span style="color: #dcdcaa;">~</span>  <span style="color: #dcdcaa;">*.</span>     <span style="color: #b5cea8;">*</span>   <span style="color: #d4d4d4;">/</span>
                                <span style="color: #d4d4d4;">\_________________________</span> <span style="color: #d4d4d4;">/</span>
                                  <span style="color: #d4d4d4;">‾</span>                     <span style="color: #d4d4d4;">‾</span>
</pre>

## Features 🌱

This is a fork of [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai) with some additional features.

- Simple package installation 📦
- Better CLI experience 💻
- Infinite mode 🔄
- Save to text files 📄

About other features read more on [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai).

## Installation 🔗

### Requirements:

- Python 3.9 or greater

### Recommended 

Use [pipx](https://pipx.pypa.io/stable/installation/) to install PyBonsai globally.

```
pipx install pybonsai
```
![demo](Images/demo.gif)

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

    -o, --save PATH       save the tree to a text file. If only a filename is provided, it will be saved in a user's Downloads directory.
    -f, --fixed-window    do not allow window height to increase when tree grows off screen
    
    -I, --infinite        run in infinite mode, infinitely growing same tree
    -n, --new             run in infinite mode, automatically growing new trees
    -W, --wait-infinite   time delay between drawing in infinite mode [default 5]
```

Other options usage examples see [examples.md](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/examples.md)

## Like it?

If you like this project, please consider giving it a ⭐️ on [GitHub](https://github.com/DaEtoJostka/PyBonsai-CLI)

Also don't forget to check out [PyBonsai](https://github.com/Ben-Edwards44/PyBonsai)
## Contributing

If you want to contribute to this project, please feel free to submit a pull request.

## License
[MIT license](https://github.com/DaEtoJostka/PyBonsai-CLI/blob/main/LICENSE)
