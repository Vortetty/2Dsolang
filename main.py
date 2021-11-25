from curses import wrapper
import curses
import _curses
import enum
import textwrap
import time
import subprocess
import argparse
import traceback
import os
import random
from pyaudio import PyAudio # sudo apt-get install python{,3}-pyaudio
import math

def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bit
                    channels=1, # mono
                    rate=sample_rate,
                    output=True)
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7f + 0x80) for t in range(n_samples))
    for buf in zip(*[samples]*sample_rate): # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cps", type=float, default=16, help="How many commands to execute per second")
    parser.add_argument("-n", "--no-kitty", type=bool, default=False, help="Disable Kitty commands")
    parser.add_argument("file", type=str, help="The file to execute")
    args = parser.parse_args()

    if not args.no_kitty:
        subprocess.run(["kitty", "@", "set-window-title", f"2Dsolang Interpreter ({os.path.basename(args.file)})"])

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
            
    def addToHistory(historyText: list, text: list):
        for t in text:
            historyText.append(t)
        del historyText[:text.len()]

    def main(stdscr: _curses.window, code):
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.delay_output(0)
        
        if not curses.has_colors() and curses.can_change_color():
            print("Your terminal does not support color")
            exit()
        
        stdscr.clear()
        curses.resize_term(34, 32*2 + 66 + 2 + 5)
        stdscr.box()
        stdscr.refresh()
        stdscr.nodelay(True)
        codeBox = stdscr.derwin(34, 66, 0, 0)
        codeBox.box()
        codeBox.refresh()
        #codeBox.nodelay(True)
        memBox = stdscr.derwin(34, 5, 0, 66)
        memBox.box()
        memBox.refresh()
        #memBox.nodelay(True)
        outputBox = stdscr.derwin(29, 66, 0, 71)
        outputBox.box()
        outputBox.refresh()
        #outputBox.nodelay(True)
        codeHistoryBox = stdscr.derwin(5, 66, 29, 71)
        codeHistoryBox.box()
        codeHistoryBox.refresh()
        #codeHistoryBox.nodelay(True)
        
        codeContent = codeBox.derwin(32, 65, 1, 1)
        memContent = memBox.derwin(33, 3, 1, 1)
        outputContent = outputBox.derwin(26, 64, 1, 1)
        codeHistoryContent = codeHistoryBox.derwin(3, 64, 1, 1)
        
        for y,yi in enumerate(code):
            for x,xi in enumerate(yi):
                codeContent.addstr(y, x*2, xi + " ")
        
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
            0 for i in range(32)
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
                        pos.y = (pos.y - 1) % 32
                elif newDirection == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % 32
                elif newDirection == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % 32
                elif newDirection == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % 32
                        
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
                        pos.y = (pos.y - 1) % 32
                elif newDirection == DIRECTION.DOWN:
                        pos.y = (pos.y + 1) % 32
                elif newDirection == DIRECTION.LEFT:
                        pos.x = (pos.x - 1) % 32
                elif newDirection == DIRECTION.RIGHT:
                        pos.x = (pos.x + 1) % 32
                        
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
                    newPos.y = (newPos.y - 1) % 32
                    num += code[newPos.y-offset][newPos.x]
                    extraHighlights.append(Vec2(newPos.x, newPos.y-offset))
                    updateCode(False, extraHighlights)
                elif direction == DIRECTION.DOWN:
                    newPos.y = (newPos.y + 1) % 32
                    num += code[newPos.y+offset][newPos.x]
                    extraHighlights.append(Vec2(newPos.x, newPos.y+offset))
                    updateCode(False, extraHighlights)
                elif direction == DIRECTION.LEFT:
                    newPos.x = (newPos.x - 1) % 32
                    num += code[newPos.y][newPos.x-offset]
                    extraHighlights.append(Vec2(newPos.x-offset, newPos.y))
                    updateCode(False, extraHighlights)
                elif direction == DIRECTION.RIGHT:
                    newPos.x = (newPos.x + 1) % 32
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
            elif cmd == 's':
                memory[currentMemCell] = parseDigitsForward(3) % 256 
            elif cmd == 'z':
                memory[currentMemCell] = 0
            elif cmd == 'p':
                tmp = parseDigitsForward(3)
                memory[tmp] = (memory[tmp] + 1) % 256 
            elif cmd == 'm':
                tmp = parseDigitsForward(3)
                memory[tmp] = (memory[tmp] - 1) % 256 
            elif cmd == '!':
                memory[currentMemCell] = random.randint(
                    parseDigitsForward(3),
                    parseDigitsForward(3,3)
                )
            elif cmd == '/':
                currentMemCell = (currentMemCell + 1) % 32
            elif cmd == '\\':
                currentMemCell = (currentMemCell - 1) % 32
            elif cmd == '*':
                currentMemCell = parseDigitsForward(3) % 32
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
            elif cmd == '$':
                x = parseDigitsForward(3, 3)
                y = parseDigitsForward(3, 6)
                beginPos = Vec2(x, y)
                for i in range(parseDigitsForward(3)):
                    start_time = time.time()
                    
                    if direction == DIRECTION.UP:
                        updateCode(False, [ Vec2(beginPos.x, (beginPos.y - i) % 32) ], [ Vec2(beginPos.x, (beginPos.y - i) % 32) ])
                        code[(beginPos.y-i) % 32][beginPos.x] = chr(codeContent.getch())
                    elif direction == DIRECTION.DOWN:
                        updateCode(False, [ Vec2(beginPos.x, (beginPos.y + i) % 32) ], [ Vec2(beginPos.x, (beginPos.y + i) % 32) ])
                        code[(beginPos.y+i) % 32][beginPos.x] = chr(codeContent.getch())
                    elif direction == DIRECTION.LEFT:
                        updateCode(False, [ Vec2((beginPos.x - i) % 32, beginPos.y) ], [ Vec2((beginPos.x - i) % 32, beginPos.y) ])
                        code[beginPos.y][(beginPos.x-i) % 32] = chr(codeContent.getch())
                    elif direction == DIRECTION.RIGHT:
                        updateCode(False, [ Vec2((beginPos.x + i) % 32, beginPos.y) ], [ Vec2((beginPos.x + i) % 32, beginPos.y) ])
                        code[beginPos.y][(beginPos.x+i) % 32] = chr(codeContent.getch())
                    
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
                
                start_time = time.time()
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
                while code[pos.y][pos.x] != '\'':
                    start_time = time.time()
                            
                    if direction == DIRECTION.UP:
                            pos.y = (pos.y - 1) % 32
                    elif direction == DIRECTION.DOWN:
                            pos.y = (pos.y + 1) % 32
                    elif direction == DIRECTION.LEFT:
                            pos.x = (pos.x - 1) % 32
                    elif direction == DIRECTION.RIGHT:
                            pos.x = (pos.x + 1) % 32
                            
                    updateCode(True)
                            
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
            elif cmd == '"':
                while code[pos.y][pos.x] != '"':
                    start_time = time.time()
                            
                    if direction == DIRECTION.UP:
                            pos.y = (pos.y - 1) % 32
                    elif direction == DIRECTION.DOWN:
                            pos.y = (pos.y + 1) % 32
                    elif direction == DIRECTION.LEFT:
                            pos.x = (pos.x - 1) % 32
                    elif direction == DIRECTION.RIGHT:
                            pos.x = (pos.x + 1) % 32
                            
                    if code[pos.y][pos.x] != '"':
                        memory[currentMemCell] = ord(code[pos.y][pos.x])
                        currentMemCell = (currentMemCell + 1) % 32
                        
                    reRender(True)
                        
                    while time.time() - start_time < 1/commandsPerSecond:
                        pass
                        
                
            if direction == DIRECTION.UP:
                pos.y = (pos.y - 1) % 32
            elif direction == DIRECTION.DOWN:
                pos.y = (pos.y + 1) % 32
            elif direction == DIRECTION.LEFT:
                pos.x = (pos.x - 1) % 32
            elif direction == DIRECTION.RIGHT:
                pos.x = (pos.x + 1) % 32
                
            
            reRender()
            
            while time.time() - start_time < 1/commandsPerSecond:
                pass
            
        stdscr.getch()

    fp = args.file
    f = open(fp, "r")
    source = [
        [" " for x in range(32)] for y in range(32)
    ]

    for y,l in enumerate(f.readlines()[:32]):
        for x,c in enumerate(l.strip("\n")[:32]):
            source[y][x] = c
    f.close()

    wrapper(main, source)
except Exception as e:
    print(traceback.format_exc())
    input("Press enter to continue")