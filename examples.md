The following images demonstrate the use of the different options:

| Effect               | Image                                              |
| -------------------- | -------------------------------------------------- |
| Big tree             | ![big tree](/Images/options/big.png)               |
| Different characters | ![different characters](/Images/options/chars.png) |
| Longer leaves        | ![longer leaves](/Images/options/leafy.png)        |

## Tree Types 🍃

PyBonsai supports 4 different tree types. Unless specified with the `--type` option, the tree type will be chosen at random.

All tree types are generated recursively and are, essentially, variations on [this](https://www.youtube.com/watch?v=0jjeOYMjmDU) basic fractal tree.

| Type             | Image                                       | Description                                                                                                              |
| ---------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Classic          | ![classic](/Images/types/classic.png)       | The number of child branches is normally distributed with $\mu = 2$ and $\sigma = 0.5$.                                  |
| Fibonacci        | ![fib](/Images/types/fib.png)               | The number of branches on the $n^{th}$ layer is the $n^{th}$ fibonacci number.                                           |
| Offset fibonacci | ![offset fib](/Images/types/offset_fib.png) | Similar to above, except child branches grow in the middle of the parent as well as the end.                             |
| Random fibonacci | ![random fib](/Images/types/rand_fib.png)   | Similar to above, except child branches grow at random positions on the parent and leaves can grow in the middle layers. |

