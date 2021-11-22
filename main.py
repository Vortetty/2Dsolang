from curses import wrapper
import curses
import _curses
import enum
import textwrap
import time
import subprocess

subprocess.run(["kitty",  "@", "resize-window"])

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
    commandsPerSecond = 16
    
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    
    def updateCode(jumping = False):
        for y,yi in enumerate(code):
            for x,xi in enumerate(yi):
                codeContent.addstr(y, x*2, "░░" if jumping and x==pos.x and y==pos.y else xi + " ", (curses.A_REVERSE if x==pos.x and y==pos.y and not jumping else curses.A_NORMAL))
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
        if direction == DIRECTION.UP:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.y = (pos.y - 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
        elif direction == DIRECTION.DOWN:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.y = (pos.y + 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
        elif direction == DIRECTION.LEFT:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.x = (pos.x - 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
        elif direction == DIRECTION.RIGHT:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.x = (pos.x + 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
                    
    def scanForJumpBackward():
        if direction == DIRECTION.UP:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.y = (pos.y + 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
        elif direction == DIRECTION.DOWN:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.y = (pos.y - 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
        elif direction == DIRECTION.LEFT:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.x = (pos.x + 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
        elif direction == DIRECTION.RIGHT:
            while code[pos.y][pos.x] != '|':
                start_time = time.time()
                pos.x = (pos.x - 1) % 32
                reRender(True)
                while time.time() - start_time < 1/commandsPerSecond:
                    pass
    
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
        elif cmd == '+':
            memory[currentMemCell] = (memory[currentMemCell] + 1) % 256 
        elif cmd == '-':
            memory[currentMemCell] = (memory[currentMemCell] - 1) % 256 
        elif cmd == '/':
            currentMemCell = (currentMemCell + 1) % 32
        elif cmd == '\\':
            currentMemCell = (currentMemCell - 1) % 32
        elif cmd == '_':
            scanForJumpForward()
        elif cmd == '=':
            scanForJumpBackward()
                    
            
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

fp = "basics.2dl" #input("Enter file path >>> ")
f = open(fp, "r")
source = [
    [" " for x in range(32)] for y in range(32)
]

for y,l in enumerate(f.readlines()[:32]):
    for x,c in enumerate(l.strip("\n")[:32]):
        source[y][x] = c
f.close()

wrapper(main, source)