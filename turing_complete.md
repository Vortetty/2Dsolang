# Proof of Turing-Completeness

All Brainfuck programs are turing complete, and all brainfuck programs can be converted to 2Dsolang as shown below

| Brainfuck | 2Dsolang                                             |
| :-------: | :--------------------------------------------------: |
| `>`       | `/`                                                  |
| `<`       | `\\`                                                 |
| `+`       | `+`                                                  |
| `-`       | `-`                                                  |
| `.`       | `%`                                                  |
| `,`       | `i`                                                  |
| `[`       | `|.000}` then redirect jump path to after ending     |
| `]`       | `:000}|` then redirect jump path to before beginning |

## Examples

### Hello World

Brainfuck:

```brainfuck
--[>--->->->++>-<<<<<-------]>--.>---------.>--..+++.>----.>+++++++++.<<.+++.------.<-.>>+.
```

2Dsolang:

```
v
-
-
>|.000} v
 {   [  > /---/-/-/++/-v
          v-------\\\\\<
v         <            
>:000{| v
v       <
>/--%/---------%/--%%+++%/----v
v                             <
>%/+++++++++%\\%+++%------%\-%v
v                             <
>//+%~
```