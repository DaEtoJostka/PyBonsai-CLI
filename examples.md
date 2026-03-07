# PyBonsai Examples 🌳

Get the most out of PyBonsai by combining different flags! Here are some cool presets and combinations to try:


### 🌸 The Sakura Zen (Most Popular)
The perfect combo for relaxation. A pink cherry blossom tree with falling leaves and Lo-Fi beats.

```bash
pybonsai -p sakura -F -R
```
<img src="Images/exampls/sakura.gif" style="max-width:100%;">
### 🍁 Autumn Breeze
A classic orange-leafed tree growing infinitely.
```bash
pybonsai -p autumn -I -N 3
```
<img src="Images/exampls/autumn.gif" style="max-width:100%;">
### 🌬️ Stormy Weather
Add wind to make the leaves blow aggressively to the side.
```bash
pybonsai -p autumn -F -M -0.3 -N 10
```
<img src="Images/exampls/wind.gif" style="max-width:100%;">
### ❄️ Winter Night
An icy white/blue tree that grows instantly, with slow-falling "snow".
```bash
pybonsai -p icy -F -d 0.1 -T 0.2 -i
```
<img src="Images/exampls/snow.gif" style="max-width:100%;">
### 🕶️ Digital Forest (Matrix Edition)
A hacker-style green tree with falling "code" bits.
```bash
pybonsai -p matrix -c "01" -C "01" -F -N 8 -K "01"
```
<img src="Images/exampls/matrix.gif" style="max-width:100%;">
### 🪴 The Desk Bonsai
Small, compact, and perfect for keeping in the corner of your terminal.
```bash
pybonsai -b -i
```
<img src="Images/exampls/bonsai.png" style="max-width:100%;">
### 🎨 Custom Masterpiece
Define your own colors using hex or RGB, and use a specific seed to recreate the same tree.
```bash
pybonsai -B "#8B4513" -e "255,100,0" -g "#335522" -s 1337
```
<img src="Images/exampls/colored.png" style="max-width:100%;">
### 🌪️ Chaotic Growth
Infinite mode that automatically starts a new tree as soon as the previous one finishes.
```bash
pybonsai -n -t 3 -W 1
```
<img src="Images/exampls/chaotic.gif" style="max-width:100%;">
### 🌲 Massive Growth
Create a huge tree that fills your screen by increasing layers and root length.

```bash
pybonsai -x 150 -y 44 -S 24 -l 10
```
<img src="Images/exampls/large.png" style="max-width:100%;">
### 🔣 Textual Textures
Customize the characters used for branches and leaves for a unique ASCII look.

```bash
pybonsai -c "#~" -C "%%" -i
```
<img src="Images/exampls/custom.png" style="max-width:100%;">
### 🌿 Weeping Willow Style
Drastically increase leaf length to give the tree a lush, weeping appearance.

```bash
pybonsai -L 10 -i
```
<img src="Images/exampls/willow.png" style="max-width:100%;">
---
## Tree Types 🍃

PyBonsai supports 4 different tree types. Unless specified with the `--type` option, the tree type will be chosen at random.

All tree types are generated recursively and are, essentially, variations on [this](https://www.youtube.com/watch?v=0jjeOYMjmDU) basic fractal tree.

| Type             | Image                                       | Description                                                                                                              |
| ---------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Classic          | <img src="Images/exampls/t0.png" style="max-width:100%;">       | The number of child branches is normally distributed with $\mu = 2$ and $\sigma = 0.5$.                                  |
| Fibonacci        | <img src="Images/exampls/t1.png" style="max-width:100%;">               | The number of branches on the $n^{th}$ layer is the $n^{th}$ fibonacci number.                                           |
| Offset fibonacci | <img src="Images/exampls/t2.png" style="max-width:100%;"> | Similar to above, except child branches grow in the middle of the parent as well as the end.                             |
| Random fibonacci | <img src="Images/exampls/t3.png" style="max-width:100%;">   | Similar to above, except child branches grow at random positions on the parent and leaves can grow in the middle layers. |

## Tips & Tricks 💡
- **Lo-Fi Radio**: Press `Ctrl+C` once to stop the tree/animation, and it will also stop the radio.
- **Save your work**: Use `-o my_tree.txt` to save the ASCII art to a file.
- **Window Size**: If the tree is too big for your terminal, use `-x` and `-y` to constrain it, or `-b` for the bonsai preset.
- **Instant Mode**: Use `-i` if you don't want to wait for the drawing animation.

