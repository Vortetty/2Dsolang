# Proof of Turing-Completeness

All Brainfuck programs are turing complete, and all brainfuck programs can be converted to 2Dsolang as shown below

| Brainfuck | 2Dsolang |
| :-------: | :------: |
| `>`       | `/`      |
| `<`       | `\\`     |
| `+`       | `+`      |
| `-`       | `-`      |
| `.`       | `%`      |
| `,`       | `i`      |
| `[`       | `<jump to after closing if 0>`      |
| `]`       | `<jump to before opening if non-0>`      |
