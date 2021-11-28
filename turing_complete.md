# Proof of Turing-Completeness

Brainfuck is turing complete, and all brainfuck programs can be converted to 2Dsolang as shown below

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

### Cat

Brainfuck:

```brainfuck
,[.,]
```

2Dsolang:

```
i |.000} %i |:000}
  {              [
       ]    { 
```

## Conclusion

All features of Brainfuck have been shown to be implementable in 2Dsolang, and therefore, as best i can tell, is turing complete.
