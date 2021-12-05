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
    parser.add_argument("-g", "--no-text", help="Disable debug rendering, this also makes the board size dynamic and memory to have any number of cells, and instructions will execute as fast as possible", action="store_true")
    parser.add_argument("-m", "--mem-cells", type=int, default=32, help="Memory cells to have")
    parser.add_argument("-w", "--width", type=int, default=32, help="Width of the board in cells")
    parser.add_argument("-e", "--height", type=int, default=32, help="Height of the board in cells")
    args = parser.parse_args()
    
    memCellCount = args.mem_cells
    boardWidth = args.width
    boardHeight = args.height

    if os.name != "nt":
        if not args.no_kitty:
            subprocess.run(["kitty", "@", "set-window-title", f"2Dsolang Interpreter ({os.path.basename(args.file)})"])
            subprocess.run(["kitty", "@", "resize-os-window", "--width", f"{boardWidth*2 + 66 + 2 + 5}", "--height", f"{(max(boardHeight, memCellCount) + 1) + 2}", "--self"])
    else:
        subprocess.run(f"title 2Dsolang Interpreter ({os.path.basename(args.file)}) ", shell=True)
        print("Do not maximize this window. It breaks curses and then the program looks horribly wrong.")

    class DIRECTION(enum.Enum):
        UP = 0
        RIGHT = 1
        DOWN = 2
        LEFT = 3
        
    class Vec2:
        x = 0
        y = 0
        
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __eq__(self, other):
                if self.x==other.x and self.y==other.y:
                    return True
                else:
                    return False
        
        def __str__(self) -> str:
            return f"({self.x}, {self.y})"
            
    def addToHistory(historyText: list, text: list):
        for t in text:
            historyText.append(t)
        del historyText[:text.len()]

    def main(stdscr: _curses.window, code):
        global memory
        global pos
        global currentMemCell
        global cmd
        
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.delay_output(0)
        
        stdscr.clear()
        curses.resize_term((max(boardHeight, memCellCount) + 1) + 2, boardWidth*2 + boardWidth*2+2 + 2 + 5)
        stdscr.box()
        stdscr.refresh()
        stdscr.nodelay(True)
        codeBox = stdscr.derwin((max(boardHeight, memCellCount) + 1) + 2, boardWidth*2+2, 0, 0)
        codeBox.box()
        codeBox.refresh()
        codeBox.nodelay(False)
        memBox = stdscr.derwin((max(boardHeight, memCellCount) + 1) + 2, 5, 0, boardWidth*2+2)
        memBox.box()
        memBox.refresh()
        memBox.nodelay(False)
        outputBox = stdscr.derwin((max(boardHeight, memCellCount) + 1) + 2 - 7, 66, 0, boardWidth*2+2+5)
        outputBox.box()
        outputBox.refresh()
        outputBox.nodelay(False)
        codeHistoryBox = stdscr.derwin(7, 66, (max(boardHeight, memCellCount) + 1) + 2 - 7, boardWidth*2+2+5)
        codeHistoryBox.box()
        codeHistoryBox.refresh()
        codeHistoryBox.nodelay(False)
        
        codeContent = codeBox.derwin((max(boardHeight, memCellCount) + 1), boardWidth*2, 1, 1)
        memContent = memBox.derwin((max(boardHeight, memCellCount) + 1), 3, 1, 1)
        outputContent = outputBox.derwin((max(boardHeight, memCellCount) + 1) - 7, 64, 1, 1)
        codeHistoryContent = codeHistoryBox.derwin(5, 64, 1, 1)
        
        subprocess.run(["/usr/bin/notify-send", "--icon=error", f"{len(list(enumerate(list(enumerate(code))[0][1])))}, {len(list(enumerate(code)))}"])
        for index in range(boardHeight*boardWidth):
            x = int(index % boardWidth)
            y = int(index / boardWidth)
            codeContent.addstr(y, x*2, code[y][x])
        
        codeContent.refresh()
        memContent.refresh()
        outputContent.refresh()
        codeHistoryContent.refresh()
        
        outputText = [
            [] for i in range(outputContent.getmaxyx()[0])
        ]
        historyText = [
            [] for i in range(codeHistoryContent.getmaxyx()[0])
        ]
        memory = [
            0 for i in range(memCellCount)
        ]
        
        for y,i in enumerate(memory):
            memContent.addstr(y, 0, str(i).rjust(3))
        
        end = False
        pos = Vec2(0, 0)
        direction = DIRECTION.RIGHT
        currentMemCell = 0
        commandsPerSecond = args.cps
        
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        
        def updateCode(jumping = False, highlights = [], cursors = []):
            for y,yi in enumerate(code):
                for x,xi in enumerate(yi):
                    codeContent.addstr(y, x*2, "░░" if jumping and ((x==pos.x and y==pos.y) or Vec2(x, y) in highlights) else ("‗‗" if Vec2(x, y) in cursors else xi + " "), (curses.A_REVERSE if ((x==pos.x and y==pos.y) or Vec2(x, y) in highlights) and not jumping else curses.A_NORMAL))
            codeContent.refresh()
            
        def updateMem():
            for y,i in enumerate(memory):
                memContent.addstr(y, 0, str(i).rjust(3), curses.A_REVERSE if y==currentMemCell else curses.A_NORMAL)
            memContent.refresh()
        
        def updateOutputs():
            outputContent.refresh()
            codeHistoryContent.refresh()
            
        def clearAll():
            #stdscr.clear()
            #codeBox.clear()
            #codeContent.clear()
            #memBox.clear()
            #memContent.clear()
            #outputBox.clear()
            #outputContent.clear()
            #codeHistoryBox.clear()
            #codeHistoryContent.clear()
            
            
            #stdscr.box()
            codeBox.box()
            memBox.box()
            outputBox.box()
            codeHistoryBox.box()
            
            stdscr.refresh()
            codeBox.refresh()
            codeContent.refresh()
            memBox.refresh()
            memContent.refresh()
            outputBox.refresh()
            outputContent.refresh()
            codeHistoryBox.refresh()
            codeHistoryContent.refresh()
        
        def reRender(jumping = False):
            #clearAll()
            updateCode(jumping)
            updateMem()
            updateOutputs()
            
        def scanForJumpForward():
            newDirection = direction
                    
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                        
                if newDirection == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif newDirection == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif newDirection == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif newDirection == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                        
                cmd = code[pos.y][pos.x]
                if cmd == '{':
                    newDirection = DIRECTION.UP
                elif cmd == '}':
                    newDirection = DIRECTION.DOWN
                elif cmd == '[':
                    newDirection = DIRECTION.LEFT
                elif cmd == ']':
                    newDirection = DIRECTION.RIGHT
                        
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
                        
            
        def scanForJumpBackward():
            newDirection = direction
            if newDirection == DIRECTION.UP:
                newDirection = DIRECTION.DOWN
            elif newDirection == DIRECTION.DOWN:
                newDirection = DIRECTION.UP
            elif newDirection == DIRECTION.LEFT:
                newDirection = DIRECTION.RIGHT
            elif newDirection == DIRECTION.RIGHT:
                newDirection = DIRECTION.LEFT
                    
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                        
                if newDirection == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif newDirection == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif newDirection == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif newDirection == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                        
                cmd = code[pos.y][pos.x]
                if cmd == '{':
                    newDirection = DIRECTION.UP
                elif cmd == '}':
                    newDirection = DIRECTION.DOWN
                elif cmd == '[':
                    newDirection = DIRECTION.LEFT
                elif cmd == ']':
                    newDirection = DIRECTION.RIGHT
                        
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
                
        def parseDigitsForward(n=3, offset=0):
            newPos = Vec2(pos.x, pos.y)
            num = ""
            extraHighlights = []
            
            for i in range(1, n+1):
                start_time = time.time()
                
                if direction == DIRECTION.UP:
                    newPos.y = (newPos.y - 1) % boardHeight
                    num += code[newPos.y-offset][newPos.x]
                    extraHighlights.append(Vec2(newPos.x, newPos.y-offset))
                    updateCode(False, extraHighlights)
                elif direction == DIRECTION.DOWN:
                    newPos.y = (newPos.y + 1) % boardHeight
                    num += code[newPos.y+offset][newPos.x]
                    extraHighlights.append(Vec2(newPos.x, newPos.y+offset))
                    updateCode(False, extraHighlights)
                elif direction == DIRECTION.LEFT:
                    newPos.x = (newPos.x - 1) % boardWidth
                    num += code[newPos.y][newPos.x-offset]
                    extraHighlights.append(Vec2(newPos.x-offset, newPos.y))
                    updateCode(False, extraHighlights)
                elif direction == DIRECTION.RIGHT:
                    newPos.x = (newPos.x + 1) % boardWidth
                    num += code[newPos.y][newPos.x+offset]
                    extraHighlights.append(Vec2(newPos.x+offset, newPos.y))
                    updateCode(False, extraHighlights)
                
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
                    
            if num.isdigit():
                return int(num)
            elif num.startswith("#"):
                return memory[currentMemCell + int(num[1:])]
        
        while not end:
            start_time = time.time()
            cmd = code[pos.y][pos.x]
                
            #
            # Commands
            #
            if cmd == '^':
                direction = DIRECTION.UP
            elif cmd == 'v':
                direction = DIRECTION.DOWN
            elif cmd == '<':
                direction = DIRECTION.LEFT
            elif cmd == '>':
                direction = DIRECTION.RIGHT
            elif cmd == '?':
                direction = random.choice([DIRECTION.UP, DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT])
            elif cmd == '+':
                memory[currentMemCell] = (memory[currentMemCell] + 1) % 256 
            elif cmd == '-':
                memory[currentMemCell] = (memory[currentMemCell] - 1) % 256 
            elif cmd == 'n':
                memory[currentMemCell] = (~(memory[currentMemCell] & (parseDigitsForward(3) % 256))) % 256
            elif cmd == 'z':
                memory[currentMemCell] = 0
            elif cmd == 's':
                memory[currentMemCell] = parseDigitsForward(3) % 256 
            elif cmd == 'p':
                tmp = parseDigitsForward(3)
                memory[tmp] = (memory[tmp] + 1) % 256 
            elif cmd == 'm':
                tmp = parseDigitsForward(3)
                memory[tmp] = (memory[tmp] - 1) % 256 
            elif cmd == 'Z':
                memory[parseDigitsForward(3)] = 0
            elif cmd == 'S':
                memory[parseDigitsForward(3)] = parseDigitsForward(3, 3) % 256 
            elif cmd == 'x':
                memory[currentMemCell] = math.floor(memory[currentMemCell]*parseDigitsForward(3))
            elif cmd == 'd':
                memory[currentMemCell] = math.floor(memory[currentMemCell]/parseDigitsForward(3))
            elif cmd == 'X':
                memory[currentMemCell] = math.floor(memory[parseDigitsForward(3)]*parseDigitsForward(3, 3))
            elif cmd == 'D':
                memory[currentMemCell] = math.floor(memory[parseDigitsForward(3)]/parseDigitsForward(3, 3))
            elif cmd == '!':
                memory[currentMemCell] = random.randint(
                    parseDigitsForward(3),
                    parseDigitsForward(3,3)
                )
            elif cmd == '/':
                currentMemCell = (currentMemCell + 1) % memCellCount
            elif cmd == '\\':
                currentMemCell = (currentMemCell - 1) % memCellCount
            elif cmd == '*':
                currentMemCell = parseDigitsForward(3) % memCellCount
            elif cmd == '_':
                scanForJumpForward()
                start_time = time.time()
            elif cmd == '.':
                if (parseDigitsForward(3) == memory[currentMemCell]):
                    scanForJumpForward()
                start_time = time.time()
            elif cmd == ':':
                if (parseDigitsForward(3) != memory[currentMemCell]):
                    scanForJumpForward()
                start_time = time.time()
            elif cmd == 'g':
                if (parseDigitsForward(3) > memory[currentMemCell]):
                    scanForJumpForward()
                start_time = time.time()
            elif cmd == 'l':
                if (parseDigitsForward(3) < memory[currentMemCell]):
                    scanForJumpForward()
                start_time = time.time()
            elif cmd == '=':
                scanForJumpBackward()
                start_time = time.time()
            elif cmd == ',':
                if (parseDigitsForward(3) == memory[currentMemCell]):
                    scanForJumpBackward()
                start_time = time.time()
            elif cmd == ';':
                if (parseDigitsForward(3) != memory[currentMemCell]):
                    scanForJumpBackward()
                start_time = time.time()
            elif cmd == 'G':
                if (parseDigitsForward(3) > memory[currentMemCell]):
                    scanForJumpBackward()
                start_time = time.time()
            elif cmd == 'L':
                if (parseDigitsForward(3) < memory[currentMemCell]):
                    scanForJumpBackward()
                start_time = time.time()
            elif cmd == '$':
                x = parseDigitsForward(3, 3)
                y = parseDigitsForward(3, 6)
                beginPos = Vec2(x, y)
                for i in range(parseDigitsForward(3)):
                    start_time = time.time()
                    
                    if direction == DIRECTION.UP:
                        updateCode(False, [ Vec2(beginPos.x, (beginPos.y - i) % boardHeight) ], [ Vec2(beginPos.x, (beginPos.y - i) % boardHeight) ])
                        code[(beginPos.y-i) % boardHeight][beginPos.x] = chr(codeContent.getch())
                    elif direction == DIRECTION.DOWN:
                        updateCode(False, [ Vec2(beginPos.x, (beginPos.y + i) % boardHeight) ], [ Vec2(beginPos.x, (beginPos.y + i) % boardHeight) ])
                        code[(beginPos.y+i) % boardHeight][beginPos.x] = chr(codeContent.getch())
                    elif direction == DIRECTION.LEFT:
                        updateCode(False, [ Vec2((beginPos.x - i) % boardWidth, beginPos.y) ], [ Vec2((beginPos.x - i) % boardWidth, beginPos.y) ])
                        code[beginPos.y][(beginPos.x-i) % boardWidth] = chr(codeContent.getch())
                    elif direction == DIRECTION.RIGHT:
                        updateCode(False, [ Vec2((beginPos.x + i) % boardWidth, beginPos.y) ], [ Vec2((beginPos.x + i) % boardWidth, beginPos.y) ])
                        code[beginPos.y][(beginPos.x+i) % boardWidth] = chr(codeContent.getch())
                    
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
                
                start_time = time.time()
            elif cmd == 'i':
                memory[currentMemCell] = codeContent.getch()
            elif cmd == '%':
                outputContent.addch(chr(memory[currentMemCell]))
            elif cmd == '&':
                outputContent.addstr(str(memory[currentMemCell]))
            elif cmd == '@':
                x = parseDigitsForward(3)
                y = parseDigitsForward(3, 3)
                outputContent.addch(code[y][x])
            elif cmd == '~':
                break
            elif cmd == '\'':
                if direction == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif direction == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif direction == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif direction == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                        
                while code[pos.y][pos.x] != '\'':
                    start_time = time.time()
                            
                    if direction == DIRECTION.UP:
                            pos.y = (pos.y - 1) % boardHeight
                    elif direction == DIRECTION.DOWN:
                            pos.y = (pos.y + 1) % boardHeight
                    elif direction == DIRECTION.LEFT:
                            pos.x = (pos.x - 1) % boardWidth
                    elif direction == DIRECTION.RIGHT:
                            pos.x = (pos.x + 1) % boardWidth
                            
                    updateCode(True)
                            
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
            elif cmd == '"':
                if direction == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif direction == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif direction == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif direction == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                        
                while code[pos.y][pos.x] != '"':
                    start_time = time.time()
                    
                    memory[currentMemCell] = ord(code[pos.y][pos.x])
                    currentMemCell = (currentMemCell + 1) % memCellCount
                            
                    if direction == DIRECTION.UP:
                            pos.y = (pos.y - 1) % boardHeight
                    elif direction == DIRECTION.DOWN:
                            pos.y = (pos.y + 1) % boardHeight
                    elif direction == DIRECTION.LEFT:
                            pos.x = (pos.x - 1) % boardWidth
                    elif direction == DIRECTION.RIGHT:
                            pos.x = (pos.x + 1) % boardWidth
                            
                    reRender(True)
                        
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
            elif cmd == 'w':
                if direction == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif direction == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif direction == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif direction == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                        
                while code[pos.y][pos.x] != 'w':
                    start_time = time.time()
                    
                    outputContent.addch(code[pos.y][pos.x])
                            
                    if direction == DIRECTION.UP:
                            pos.y = (pos.y - 1) % boardHeight
                    elif direction == DIRECTION.DOWN:
                            pos.y = (pos.y + 1) % boardHeight
                    elif direction == DIRECTION.LEFT:
                            pos.x = (pos.x - 1) % boardWidth
                    elif direction == DIRECTION.RIGHT:
                            pos.x = (pos.x + 1) % boardWidth
                        
                    reRender(True)
                        
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
                        
                
            if direction == DIRECTION.UP:
                    pos.y = (pos.y - 1) % boardHeight
            elif direction == DIRECTION.DOWN:
                    pos.y = (pos.y + 1) % boardHeight
            elif direction == DIRECTION.LEFT:
                    pos.x = (pos.x - 1) % boardWidth
            elif direction == DIRECTION.RIGHT:
                    pos.x = (pos.x + 1) % boardWidth
                
            
            reRender()
            
            while time.time() - start_time < 1/commandsPerSecond:
                pass
            
        outputContent.addstr("\nPress enter to exit")
        outputContent.refresh()
        while stdscr.getch() != -1:
            pass
        stdscr.nodelay(False)
        stdscr.getch()

    fp = args.file
    f = open(fp, "r")
    source = [
        [" " for x in range(boardWidth)] for y in range(boardHeight)
    ]
    

    for y,l in enumerate(f.readlines()[:boardHeight]):
        for x,c in enumerate(l.strip("\n")[:boardWidth]):
            source[y][x] = c
    f.close()

    wrapper(main, source)
except Exception as e:
    print(traceback.format_exc())
    print(f"Current Char: {pos} \"{cmd}\"")
    print(f"Memory: {memory}")
    print(f"Current Memory Cell: {currentMemCell}")
    input("\nPress enter to continue")