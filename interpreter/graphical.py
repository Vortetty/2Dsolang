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
    
class textManager:
    def __init__(self, width, height, preInitialize=False):
        if preInitialize:
            self.lines = [
                " "*width for i in range(height)
            ]
        else:
            self.lines = []
        self.width = width
        self.height = height
        
    def newLine(self, line):
        for x in line.split("\n"):
            self.lines.extend(
                i.ljust(self.width, " ").strip("\n") for i in textwrap.wrap(x, self.width, subsequent_indent=" ", replace_whitespace=False)
            )
        self.lines = self.lines[-self.height:]
        
    def appendChar(self, line):
        if line == "\n":
            self.lines.append(" "*self.width)
        else:
            tmp = self.lines.pop(-1).strip(" ") if len(self.lines) > 0 else ""
            self.lines.extend(
                i.ljust(self.width, " ") for i in textwrap.wrap(tmp+line, self.width, subsequent_indent=" ", replace_whitespace=False)
            )
        self.lines = self.lines[-self.height:]
        
    def writeToDisplay(self, stdscr: _curses.window):
        stdscr.clear()
        for y, line in enumerate(self.lines):
            for x, char in enumerate(line):
                #print(x, y)
                try:
                    stdscr.addch(y, x, char)
                except:
                    pass
            #stdscr.addstr(line[:self.width])
        
def addToHistory(historyText: list, text: list):
    for t in text:
        historyText.append(t)
    del historyText[:text.len()]
        
def main(stdscr: _curses.window, code, memCellCount, boardWidth, boardHeight, cps):
    global memory
    global pos
    global currentMemCell
    global cmd
    
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.delay_output(0)
    
    stdscr.clear()
    curses.resize_term((max(boardHeight, memCellCount)) + 2, boardWidth*2 + boardWidth*2+2 + 2 + 5)
    stdscr.box()
    stdscr.refresh()
    stdscr.nodelay(True)
    codeBox = stdscr.derwin((max(boardHeight, memCellCount)) + 2, boardWidth*2+2, 0, 0)
    codeBox.box()
    codeBox.refresh()
    codeBox.nodelay(False)
    memBox = stdscr.derwin((max(boardHeight, memCellCount)) + 2, 5, 0, boardWidth*2+2)
    memBox.box()
    memBox.refresh()
    memBox.nodelay(False)
    outputBox = stdscr.derwin((max(boardHeight, memCellCount)) + 2 - 9, 66, 0, boardWidth*2+2+5)
    outputBox.box()
    outputBox.refresh()
    outputBox.nodelay(False)
    codeHistoryBox = stdscr.derwin(9, 66, (max(boardHeight, memCellCount)) + 2 - 9, boardWidth*2+2+5)
    codeHistoryBox.box()
    codeHistoryBox.refresh()
    codeHistoryBox.nodelay(False)
    
    codeContent = codeBox.derwin((max(boardHeight, memCellCount) + 1), boardWidth*2, 1, 1)
    memContent = memBox.derwin((max(boardHeight, memCellCount) + 1), 3, 1, 1)
    outputContent = outputBox.derwin((max(boardHeight, memCellCount)) - 9, 64, 1, 1)
    codeHistoryContent = codeHistoryBox.derwin(7, 64, 1, 1)
    
    for index in range(boardHeight*boardWidth):
        x = int(index % boardWidth)
        y = int(index / boardWidth)
        codeContent.addstr(y, x*2, code[y][x])
    
    codeContent.refresh()
    memContent.refresh()
    outputContent.refresh()
    codeHistoryContent.refresh()
    
    outputText = textManager(outputContent.getmaxyx()[1], outputContent.getmaxyx()[0])
    historyText = textManager(codeHistoryContent.getmaxyx()[1], codeHistoryContent.getmaxyx()[0])
    memory = [
        0 for i in range(memCellCount)
    ]
    
    for y,i in enumerate(memory):
        memContent.addstr(y, 0, str(i).rjust(3))
    
    end = False
    pos = Vec2(0, 0)
    direction = DIRECTION.RIGHT
    currentMemCell = 0
    commandsPerSecond = cps
    
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
        outputText.writeToDisplay(outputContent)
        outputContent.refresh()
        
        historyText.writeToDisplay(codeHistoryContent)
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
            historyText.newLine("Changed direction to Up")
        elif cmd == 'v':
            direction = DIRECTION.DOWN
            historyText.newLine("Changed direction to Down")
        elif cmd == '<':
            direction = DIRECTION.LEFT
            historyText.newLine("Changed direction to Left")
        elif cmd == '>':
            direction = DIRECTION.RIGHT
            historyText.newLine("Changed direction to Right")
        elif cmd == '?':
            direction = random.choice([DIRECTION.UP, DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT])
            historyText.newLine("Randomly changed direction to " + direction.name.capitalize())
        elif cmd == '+':
            memory[currentMemCell] = (memory[currentMemCell] + 1) % 256 
            historyText.newLine("Incremented memory cell " + str(currentMemCell) + " to " + str(memory[currentMemCell]))
        elif cmd == '-':
            memory[currentMemCell] = (memory[currentMemCell] - 1) % 256 
            historyText.newLine("Decremented memory cell " + str(currentMemCell) + " to " + str(memory[currentMemCell]))
        elif cmd == 'n':
            tmp = (parseDigitsForward(3) % 256)
            memory[currentMemCell] = (~(memory[currentMemCell] & tmp)) % 256
            historyText.newLine("NANDed memory cell " + str(currentMemCell) + " with " + str(tmp) + " to " + str(memory[currentMemCell]))
        elif cmd == 'z':
            memory[currentMemCell] = 0
            historyText.newLine("Zeroed memory cell " + str(currentMemCell))
        elif cmd == 's':
            memory[currentMemCell] = parseDigitsForward(3) % 256 
            historyText.newLine("Set memory cell " + str(currentMemCell) + " to " + str(memory[currentMemCell]))
        elif cmd == 'p':
            tmp = parseDigitsForward(3)
            memory[tmp] = (memory[tmp] + 1) % 256 
            historyText.newLine("Incremented memory cell " + str(tmp) + " to " + str(memory[tmp]))
        elif cmd == 'm':
            tmp = parseDigitsForward(3)
            memory[tmp] = (memory[tmp] - 1) % 256 
            historyText.newLine("Decremented memory cell " + str(tmp) + " to " + str(memory[tmp]))
        elif cmd == 'Z':
            tmp = parseDigitsForward(3)
            memory[tmp] = 0
            historyText.newLine("Zeroed memory cell " + str(tmp))
        elif cmd == 'S':
            tmp = parseDigitsForward(3)
            memory[tmp] = parseDigitsForward(3, 3) % 256 
            historyText.newLine("Set memory cell " + str(tmp) + " to " + str(memory[tmp]))
        elif cmd == 'x':
            tmp = parseDigitsForward(3)
            memory[currentMemCell] = math.floor(memory[currentMemCell]*tmp)
            historyText.newLine("Multiplied memory cell " + str(currentMemCell) + " by " + str(tmp) + " to " + str(memory[currentMemCell]))
        elif cmd == 'd':
            tmp = parseDigitsForward(3)
            memory[currentMemCell] = math.floor(memory[currentMemCell]/tmp)
            historyText.newLine("Divided memory cell " + str(currentMemCell) + " by " + str(tmp) + " to " + str(memory[currentMemCell]))
        elif cmd == 'X':
            tmp = parseDigitsForward(3)
            tmp1 = parseDigitsForward(3, 3)
            memory[currentMemCell] = math.floor(memory[tmp]*tmp1)
            historyText.newLine("Multiplied memory cell " + str(tmp) + " by " + str(tmp1) + " to " + str(memory[currentMemCell]))
        elif cmd == 'D':
            tmp = parseDigitsForward(3)
            tmp1 = parseDigitsForward(3, 3)
            memory[currentMemCell] = math.floor(memory[tmp]/tmp1)
            historyText.newLine("Divided memory cell " + str(tmp) + " by " + str(tmp1) + " to " + str(memory[currentMemCell]))
        elif cmd == '!':
            tmp = parseDigitsForward(3)
            tmp1 = parseDigitsForward(3, 3)
            memory[currentMemCell] = random.randint(
                parseDigitsForward(3),
                parseDigitsForward(3,3)
            )
            historyText.newLine("Randomly set memory cell " + str(currentMemCell) + " to " + str(memory[currentMemCell]) + " with random number " + str(tmp) + "-" + str(tmp1))
        elif cmd == '/':
            currentMemCell = (currentMemCell + 1) % memCellCount
            historyText.newLine("Moved to memory cell " + str(currentMemCell))
        elif cmd == '\\':
            currentMemCell = (currentMemCell - 1) % memCellCount
            historyText.newLine("Moved to memory cell " + str(currentMemCell))
        elif cmd == '*':
            currentMemCell = parseDigitsForward(3) % memCellCount
            historyText.newLine("Moved to memory cell " + str(currentMemCell))
        elif cmd == '_':
            tmp = "Jumped from " + str(pos) + " to "
            scanForJumpForward()
            tmp += str(pos)
            historyText.newLine(tmp)
            start_time = time.time()
        elif cmd == '.':
            tmp = parseDigitsForward(3)
            if (tmp == memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is not equal to " + str(tmp))
            start_time = time.time()
        elif cmd == ':':
            tmp = parseDigitsForward(3)
            if (tmp != memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is equal to " + str(tmp))
            start_time = time.time()
        elif cmd == 'g':
            tmp = parseDigitsForward(3)
            if (tmp > memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is not greater than " + str(tmp))
            start_time = time.time()
        elif cmd == 'l':
            tmp = parseDigitsForward(3)
            if (tmp < memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is not less than " + str(tmp))
            start_time = time.time()
        elif cmd == '=':
            tmp = "Jumped from " + str(pos) + " to "
            scanForJumpBackward()
            tmp += str(pos)
            historyText.newLine(tmp)
            start_time = time.time()
        elif cmd == ',':
            tmp = parseDigitsForward(3)
            if (tmp == memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " != " + str(tmp))
            start_time = time.time()
        elif cmd == ';':
            tmp = parseDigitsForward(3)
            if (tmp != memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " == " + str(tmp))
            start_time = time.time()
        elif cmd == 'G':
            tmp = parseDigitsForward(3)
            if (tmp > memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " >= " + str(tmp))
            start_time = time.time()
        elif cmd == 'L':
            tmp = parseDigitsForward(3)
            if (tmp < memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " <= " + str(tmp))
            start_time = time.time()
        elif cmd == '$':
            tmp = parseDigitsForward(3)
            x = parseDigitsForward(3, 3)
            y = parseDigitsForward(3, 6)
            beginPos = Vec2(x, y)
            historyText.newLine("Asking for " + str(tmp) + " lines of input at " + str(beginPos))
            written = ""
            for i in range(tmp):
                start_time = time.time()
                
                if direction == DIRECTION.UP:
                    updateCode(False, [ Vec2(beginPos.x, (beginPos.y - i) % boardHeight) ], [ Vec2(beginPos.x, (beginPos.y - i) % boardHeight) ])
                    code[(beginPos.y-i) % boardHeight][beginPos.x] = chr(codeContent.getch())
                    written += code[(beginPos.y-i) % boardHeight][beginPos.x]
                elif direction == DIRECTION.DOWN:
                    updateCode(False, [ Vec2(beginPos.x, (beginPos.y + i) % boardHeight) ], [ Vec2(beginPos.x, (beginPos.y + i) % boardHeight) ])
                    code[(beginPos.y+i) % boardHeight][beginPos.x] = chr(codeContent.getch())
                    written += code[(beginPos.y+i) % boardHeight][beginPos.x]
                elif direction == DIRECTION.LEFT:
                    updateCode(False, [ Vec2((beginPos.x - i) % boardWidth, beginPos.y) ], [ Vec2((beginPos.x - i) % boardWidth, beginPos.y) ])
                    code[beginPos.y][(beginPos.x-i) % boardWidth] = chr(codeContent.getch())
                    written += code[beginPos.y][(beginPos.x-i) % boardWidth]
                elif direction == DIRECTION.RIGHT:
                    updateCode(False, [ Vec2((beginPos.x + i) % boardWidth, beginPos.y) ], [ Vec2((beginPos.x + i) % boardWidth, beginPos.y) ])
                    code[beginPos.y][(beginPos.x+i) % boardWidth] = chr(codeContent.getch())
                    written += code[beginPos.y][(beginPos.x+i) % boardWidth]
                
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
            historyText.newLine("Input written: " + written)
            start_time = time.time()
        elif cmd == 'i':
            memory[currentMemCell] = codeContent.getch()
            historyText.newLine("Set memory cell " + str(currentMemCell) + " to " + str(memory[currentMemCell]) + " from user input")
        elif cmd == '%':
            outputText.appendChar(chr(memory[currentMemCell]))
            historyText.newLine("Output \"" + chr(memory[currentMemCell]) + "\" to console")
        elif cmd == '&':
            outputText.appendChar(str(memory[currentMemCell]))
            historyText.newLine("Output \"" + str(memory[currentMemCell]) + "\" to console")
        elif cmd == '@':
            x = parseDigitsForward(3)
            y = parseDigitsForward(3, 3)
            outputText.appendChar(code[y][x])
            historyText.newLine("Output \"" + code[y][x] + "\" to console from position " + str(Vec2(x, y)))
        elif cmd == '~':
            historyText.newLine("Exiting")
            break
        elif cmd == '\'':
            historyText.newLine("Entered skip mode")
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
            historyText.newLine("Exited skip mode")
        elif cmd == '"':
            historyText.newLine("Entered write to memory mode")
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
            historyText.newLine("Exited write to memory mode")
        elif cmd == 'w':
            historyText.newLine("Entered write to console mode")
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
                
                outputText.appendChar(code[pos.y][pos.x])
                        
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
            historyText.newLine("Exited write to console mode")
                    
            
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
        
    outputText.newLine("\nPress enter to exit")
    outputText.writeToDisplay(outputContent)
    outputContent.refresh()
    while stdscr.getch() != -1:
        pass
    stdscr.nodelay(False)
    stdscr.getch()