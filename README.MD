# twofiftysixsquared

all code takes place on a 2d grid of 256x256, any character that isn't defined as a command is treated as a noop unless part of a command

## Commands

| Command | Description                                                                                                                                                                      |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `>`     | set execution right                                                                                                                                                              |
| `<`     | set execution left                                                                                                                                                               |
| `^`     | set execution up                                                                                                                                                                 |
| `v`     | set execution down                                                                                                                                                               |
| `+`     | increment mem                                                                                                                                                                    |
| `-`     | decrement mem                                                                                                                                                                    |
| `*`     | move to next mem cell                                                                                                                                                            |
| `/`     | move to previous mem cell                                                                                                                                                        |
| `\|`    | mark jump point
| `_`     | jump to first jump point (scans opposite direction as execution direction from current 2d cell, don't change direction)                                                          |
| `=`     | jump to last jump point (scans opposite direction as execution direction from current 2d cell, don't change direction)                                                           |
| `.`     | jump to first jump point if selected mem is equal to the number in the next 3 cells (example: `>                                                                                 |+.001--_` would set mem cell 0 to 1, then jump to beginning if it equals 1, then increment again and not jump, decrement 2 and repeat)  
| `:`     | jump to first jump point if selected mem is not equal to the number in the next 3 cells (example: `>                                                                             |+.001--_` would set mem cell 0 to 1, then jump to beginning if it equals 1, then increment again and not jump, decrement 2 and repeat) 
| `,`     | jump to last jump point if selected mem is equal to the number in the next 3 cells                                                                                               |
| `;`     | jump to last jump point if selected mem is not equal to the number in the next 3 cells                                                                                           |
| `$`     | get n characters from user and store them starting at cell x, y in the current execution direction, structure is `$<3 digit number><3 digit number for x><3 digit number for y>` |
| `%`     | print current character in selected memory cell(ascii only)                                                                                                                      |
| `@`     | print character at given cell, structure is `@<3 digit number for x to print><3 digit number for y to print>`                                                                    |
| `#`     | replaces a number, will be substituted for the current number in the current memory cell offset by n, structure is `#<2 digit number to offset by, must be positive>`            |
| `!`     | executes current memory value as if it was a character                                                                                                                           |
| `~`     | ends the program                                                                                                                                                                 |

## Examples

| Name                | Code                     |
| ------------------- | ------------------------ |
| ascii code to ascii | ``>$003014000\|+:   %~`` |
| quine               | ``>\|@#00000+:015~``     |
| cheat quine         | `` `` (a blank file)     |
