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
import sys
import random

class DIRECTION(enum.Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
class GrowingList(list):
    def __init__(self, defaultItem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defaultItem = defaultItem
    
    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([self.defaultItem] * (index + 1 - len(self)))
        list.__setitem__(self, index, value)
    
    def __getitem__(self, index):
        if index >= len(self):
            self.extend([self.defaultItem] * (index + 1 - len(self)))
        return list.__getitem__(self, index)
    
    
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
            self.full_lines = [
                " "*width for i in range(height)
            ]
        else:
            self.full_lines = []
        self.width = width
        self.height = height
        
    def newLine(self, line):
        for x in line.split("\n"):
            l = [i.ljust(self.width, " ").strip("\n") for i in textwrap.wrap(x, self.width, subsequent_indent=" ", replace_whitespace=False, drop_whitespace=False)]
            self.full_lines.extend(l)
        
    def appendChar(self, line):
        if line == "\n":
            self.full_lines.append(" "*self.width)
        else:
            tmp = self.full_lines.pop(-1).strip(" ") if len(self.full_lines) > 0 else ""
            l = [i.ljust(self.width, " ").strip("\n") for i in textwrap.wrap(tmp+line, self.width, subsequent_indent=" ", replace_whitespace=False, drop_whitespace=False)]
            self.full_lines.extend(l)
        
    def writeToDisplay(self, stdscr: _curses.window):
        stdscr.clear()
        for y, line in enumerate(self.full_lines[-self.height:]):
            for x, char in enumerate(line):
                #print(x, y)
                try:
                    stdscr.addch(y, x, char)
                except:
                    pass
            #stdscr.addstr(line[:self.width])
            
    def writeToFile(self, filename: str):
        with open(filename, "w") as f:
            f.writelines(self.full_lines)
        
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
    curses.resize_term(37, 133)
    #stdscr.box()
    stdscr.addstr(0, 0, "╷ Program output ╷")
    stdscr.addstr(0, 67, "╷ Program log ╷")
    stdscr.refresh()
    stdscr.nodelay(False)
    outputBox = stdscr.derwin(36, 66, 1, 0)
    outputBox.box()
    outputBox.addstr(0, 0, "├────────────────┴")
    outputBox.refresh()
    outputBox.nodelay(False)
    codeHistoryBox = stdscr.derwin(36, 66, 1, 67)
    codeHistoryBox.box()
    codeHistoryBox.addstr(0, 0, "├─────────────┴")
    codeHistoryBox.refresh()
    codeHistoryBox.nodelay(False)
    
    outputContent = outputBox.derwin(34, 64, 1, 1)
    codeHistoryContent = codeHistoryBox.derwin(34, 64, 1, 1)
    
    outputContent.refresh()
    codeHistoryContent.refresh()
    
    #outputContent.getch()
    #stdscr.getstr()
    
    outputText = textManager(outputContent.getmaxyx()[1], outputContent.getmaxyx()[0])
    historyText = textManager(codeHistoryContent.getmaxyx()[1], codeHistoryContent.getmaxyx()[0])
    memory = [
        0 for i in range(memCellCount)
    ] if cps != -1 else GrowingList(0)
    
    end = False
    pos = Vec2(0, 0)
    direction = DIRECTION.RIGHT
    currentMemCell = 0
    commandsPerSecond = cps
    
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    
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
        outputBox.box()
        codeHistoryBox.box()
        
        stdscr.refresh()
        outputBox.refresh()
        outputContent.refresh()
        codeHistoryBox.refresh()
        codeHistoryContent.refresh()
    
    def reRender():
        #clearAll()
        updateOutputs()
        
    def scanForJumpForward():
        newDirection = direction
                
        while code[pos.y][pos.x] != '|':
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
            
    def parseDigitsForward(n=3, offset=0):
        newPos = Vec2(pos.x, pos.y)
        num = ""
        
        for i in range(1, n+1):
            if direction == DIRECTION.UP:
                newPos.y = (newPos.y - 1) % boardHeight
                num += code[newPos.y-offset][newPos.x]
            elif direction == DIRECTION.DOWN:
                newPos.y = (newPos.y + 1) % boardHeight
                num += code[newPos.y+offset][newPos.x]
            elif direction == DIRECTION.LEFT:
                newPos.x = (newPos.x - 1) % boardWidth
                num += code[newPos.y][newPos.x-offset]
            elif direction == DIRECTION.RIGHT:
                newPos.x = (newPos.x + 1) % boardWidth
                num += code[newPos.y][newPos.x+offset]
                
        if num.isdigit():
            return int(num)
        elif num.startswith("#"):
            return memory[currentMemCell + int(num[1:])]
    
    while not end:
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
        elif cmd == '.':
            tmp = parseDigitsForward(3)
            if (tmp == memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is not equal to " + str(tmp))
        elif cmd == ':':
            tmp = parseDigitsForward(3)
            if (tmp != memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is equal to " + str(tmp))
        elif cmd == 'g':
            tmp = parseDigitsForward(3)
            if (tmp > memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is not greater than " + str(tmp))
        elif cmd == 'l':
            tmp = parseDigitsForward(3)
            if (tmp < memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpForward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " is not less than " + str(tmp))
        elif cmd == '=':
            tmp = "Jumped from " + str(pos) + " to "
            scanForJumpBackward()
            tmp += str(pos)
            historyText.newLine(tmp)
        elif cmd == ',':
            tmp = parseDigitsForward(3)
            if (tmp == memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " != " + str(tmp))
        elif cmd == ';':
            tmp = parseDigitsForward(3)
            if (tmp != memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " == " + str(tmp))
        elif cmd == 'G':
            tmp = parseDigitsForward(3)
            if (tmp > memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " >= " + str(tmp))
        elif cmd == 'L':
            tmp = parseDigitsForward(3)
            if (tmp < memory[currentMemCell]):
                tmp = "Jumped from " + str(pos) + " to "
                scanForJumpBackward()
                tmp += str(pos)
                historyText.newLine(tmp)
            else:
                historyText.newLine("Did not jump because memory cell " + str(currentMemCell) + " <= " + str(tmp))
        elif cmd == '$':
            tmp = parseDigitsForward(3)
            x = parseDigitsForward(3, 3)
            y = parseDigitsForward(3, 6)
            beginPos = Vec2(x, y)
            historyText.newLine("Asking for " + str(tmp) + " lines of input at " + str(beginPos))
            reRender()
            written = ""
            for i in range(tmp):
                
                if direction == DIRECTION.UP:
                    code[(beginPos.y-i) % boardHeight][beginPos.x] = chr(stdscr.getch())
                    written += code[(beginPos.y-i) % boardHeight][beginPos.x]
                elif direction == DIRECTION.DOWN:
                    code[(beginPos.y+i) % boardHeight][beginPos.x] = chr(stdscr.getch())
                    written += code[(beginPos.y+i) % boardHeight][beginPos.x]
                elif direction == DIRECTION.LEFT:
                    code[beginPos.y][(beginPos.x-i) % boardWidth] = chr(stdscr.getch())
                    written += code[beginPos.y][(beginPos.x-i) % boardWidth]
                elif direction == DIRECTION.RIGHT:
                    code[beginPos.y][(beginPos.x+i) % boardWidth] = chr(stdscr.getch())
                    written += code[beginPos.y][(beginPos.x+i) % boardWidth]
                    
            historyText.newLine("Input written: " + written)
            reRender()
        elif cmd == 'i':
            historyText.newLine("Asking for character to put into " + str(memory[currentMemCell]))
            reRender()
            memory[currentMemCell] = stdscr.getch()
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
                        
                if direction == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif direction == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif direction == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif direction == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                        
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
                
                outputText.appendChar(code[pos.y][pos.x])
                        
                if direction == DIRECTION.UP:
                        pos.y = (pos.y - 1) % boardHeight
                elif direction == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % boardHeight
                elif direction == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % boardWidth
                elif direction == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % boardWidth
                    
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
        
    outputText.newLine("\nPress enter to exit")
    outputText.writeToDisplay(outputContent)
    outputContent.refresh()
    stdscr.nodelay(True)
    while stdscr.getch() != -1:
        pass
    stdscr.nodelay(False)
    stdscr.getch()