import argparse

def newHelpMessage(*args, **kwargs):
    return """Usage: \u001b[4m\u001b[1m\u001b[40;1mrun-crossplatform.bat \u001b[36mfile\u001b[0m\u001b[40;1m [\u001b[36m-h\u001b[0m\u001b[40;1m] [\u001b[36m-n\u001b[0m\u001b[40;1m] [ \u001b[31;1m[\u001b[36m-c\u001b[32m CPS\u001b[31;1m] [\u001b[36m-m\u001b[32m MEM_CELLS\u001b[31;1m] [\u001b[36m-w\u001b[32m WIDTH\u001b[31;1m] [\u001b[36m-e\u001b[32m HEIGHT\u001b[31;1m]\u001b[40;1 | \u001b[34;1m[\u001b[36m-g\u001b[34;1m] \u001b[0m\u001b[40;1m]\u001b[0m

Positional Arguments:
  \u001b[32mfile\u001b[0m              
      \u001b[31;1mThe file to execute\u001b[0m

Optional Arguments:
  \u001b[36m-h\u001b[0m, \u001b[36m--help\u001b[0m        
      \u001b[31;1mShow this help message and exit.\u001b[0m
  \u001b[36m-n\u001b[0m, \u001b[36m--no-kitty\u001b[0m    
      \u001b[31;1mDisable Kitty commands\u001b[0m
  
  Group 1 (incompatible with group 2):
    \u001b[36m-c \u001b[32mCPS\u001b[0m, \u001b[36m--cps \u001b[32mCPS\u001b[0m
        \u001b[31;1mHow many commands to execute per second\u001b[0m
    \u001b[36m-m \u001b[32mMEM_CELLS\u001b[0m, \u001b[36m--mem-cells \u001b[32mMEM_CELLS\u001b[0m
        \u001b[31;1mMemory cells to have\u001b[0m
    \u001b[36m-w \u001b[32mWIDTH\u001b[0m, \u001b[36m--width \u001b[32mWIDTH\u001b[0m
        \u001b[31;1mWidth of the board in cells\u001b[0m
    \u001b[36m-e \u001b[32mHEIGHT\u001b[0m, \u001b[36m--height \u001b[32mHEIGHT\u001b[0m
        \u001b[31;1mHeight of the board in cells\u001b[0m
                          
  Group 2 (incompatible with group 1):
    \u001b[36m-g\u001b[0m, \u001b[36m--no-text\u001b[0m
        \u001b[31;1mDisable debug rendering, this also makes the board size dynamic and memory to have any number of cells, and instructions will execute as fast as possible.\u001b[0m

"""

argparse.ArgumentParser.format_help = newHelpMessage

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', '--help', default=argparse.SUPPRESS, help='Show this help message and exit.', action='help')

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

if args.help:
    parser.print_help()
    exit(0)
