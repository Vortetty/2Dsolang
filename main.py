from curses import wrapper
import curses
import _curses
import enum
import math
import textwrap
import time
import subprocess
import argparse
import traceback
import os
import random

memory = None
pos = None
currentMemCell = None
cmd = None

try:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group1 = group.add_argument_group()
    
    parser.add_argument("file", type=str, help="The file to execute")
    parser.add_argument("-c", "--cps", type=float, default=16, help="How many commands to execute per second")
    parser.add_argument("-n", "--no-kitty", help="Disable Kitty commands", action="store_true")
    
    group1.add_argument("-m", "--mem-cells", type=int, default=32, help="Memory cells to have")
    group1.add_argument("-w", "--width", type=int, default=32, help="Width of the board in cells")
    group1.add_argument("-e", "--height", type=int, default=32, help="Height of the board in cells")
    
    group.add_argument("-g", "--no-text", help="Disable debug rendering, this also makes the board size dynamic and memory to have any number of cells, and instructions will execute as fast as possible", action="store_true")
    
    args = parser.parse_args()
    
    memCellCount = args.mem_cells
    boardWidth = args.width
    boardHeight = args.height
    main = None

    if os.name != "nt":
        if not args.no_kitty:
            subprocess.run(["kitty", "@", "set-window-title", f"2Dsolang Interpreter ({os.path.basename(args.file)})"])
            subprocess.run(["kitty", "@", "resize-os-window", "--width", f"{boardWidth*2 + 66 + 2 + 5}", "--height", f"{(max(boardHeight, memCellCount) + 1) + 2}", "--self"])
    else:
        subprocess.run(f"title 2Dsolang Interpreter ({os.path.basename(args.file)}) ", shell=True)
        print("Do not maximize this window. It breaks curses and then the program looks horribly wrong.")

    if args.no_text:
        from interpreter import non_graphical
        main = non_graphical.main
    else:
        from interpreter import graphical
        main = graphical.main
    

    fp = args.file
    f = open(fp, "r")
    source = [
        [" " for x in range(boardWidth)] for y in range(boardHeight)
    ]
    

    for y,l in enumerate(f.readlines()[:boardHeight]):
        for x,c in enumerate(l.strip("\n")[:boardWidth]):
            source[y][x] = c
    f.close()

    wrapper(main, source, memCellCount, boardWidth, boardHeight, args.cps)
    
except Exception as e:
    print(traceback.format_exc())
    print(f"Current Char: {pos} \"{cmd}\"")
    print(f"Memory: {memory}")
    print(f"Current Memory Cell: {currentMemCell}")
    input("\nPress enter to continue")