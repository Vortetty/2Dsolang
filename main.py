try:
    import pyjion
    pyjion.config(level=2, pgc=False)
    pyjion.enable()
except: pass
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
    
    parser.add_argument("file", type=str, help="The file to execute")
    parser.add_argument("-c", "--cps", type=float, default=16, help="How many commands to execute per second")
    parser.add_argument("-n", "--no-kitty", help="Disable Kitty commands", action="store_true")
    parser.add_argument("-l", "--log", action="store_true", help="Enable logging to file")
    parser.add_argument("-b", "--log-basename", action="store_true", help="Basename for log files, there will be a prefix added to say what is being logged")
    
    parser.add_argument("-m", "--mem-cells", type=int, default=32, help="Memory cells to have")
    parser.add_argument("-w", "--width", type=int, default=32, help="Width of the board in cells")
    parser.add_argument("-e", "--height", type=int, default=32, help="Height of the board in cells")
    
    parser.add_argument("-g", "--no-text", help="Disable debug rendering, this also makes the board size dynamic and memory to have any number of cells, and instructions will execute as fast as possible", action="store_true")
    
    args = parser.parse_args()
    
    memCellCount = args.mem_cells
    boardWidth = args.width
    boardHeight = args.height
    main = None
    
    if args.no_text:
        winSizeX = 133 + 5
        winSizeY = 35
    else:
        winSizeX = boardWidth*2 + boardWidth*2+2 + 2 + 5 + 5
        winSizeY = (max(boardHeight, memCellCount)) + 2 + 1

    if os.name == "nt":
        subprocess.run(f"title 2Dsolang Interpreter ({os.path.basename(args.file)}) ", shell=True)
    elif not args.no_kitty:
        subprocess.run(["kitty", "@", "set-window-title", f"2Dsolang Interpreter ({os.path.basename(args.file)})"])
        subprocess.run(["kitty", "@", "resize-os-window", "--width", f"{winSizeX}", "--height", f"{winSizeY}", "--self"])

    if args.no_text:
        from interpreter import non_graphical
        main = non_graphical.main
    else:
        from interpreter import graphical
        main = graphical.main
    

    fp = args.file
    f = open(fp, "r")
    lines = f.readlines()
    
    if args.no_text:
        boardHeight = len(lines)
        boardWidth = max(len(line.strip("\n")) for line in lines)
        
    #print(f"{boardWidth}x{boardHeight}")
    #input()
    
    source = [
        [" " for x in range(boardWidth)] for y in range(boardHeight)
    ]
    

    for y,l in enumerate(lines[:boardHeight]):
        for x,c in enumerate(l.strip("\n")[:boardWidth]):
            source[y][x] = c
    f.close()
    
    #print("`".join("".join(i) for i in source))
    #input()

    wrapper(main, source, memCellCount, boardWidth, boardHeight, winSizeX, winSizeY+1, args.cps)
    
except Exception as e:
    print(traceback.format_exc())
    print(f"Current Char: {pos} \"{cmd}\"")
    print(f"Memory: {memory}")
    print(f"Current Memory Cell: {currentMemCell}")
    input("\nPress enter to continue")