try:
    import pyjion
    pyjion.config(level=2)
    pyjion.enable()
except: pass
import argparse
import gettext
import sys

# A list mapping color names to ansi color codes
color_codes = [
    ['{black}',   "\u001b[30m"],
    ['{red}',     "\u001b[31m"],
    ['{green}',   "\u001b[32m"],
    ['{yellow}',  "\u001b[33m"],
    ['{blue}',    "\u001b[34m"],
    ['{magenta}', "\u001b[35m"],
    ['{cyan}',    "\u001b[36m"],
    ['{white}',   "\u001b[37m"],
    
    ['{bright_black}',   "\u001b[30;1m"],
    ['{bright_red}',     "\u001b[31;1m"],
    ['{bright_green}',   "\u001b[32;1m"],
    ['{bright_yellow}',  "\u001b[33;1m"],
    ['{bright_blue}',    "\u001b[34;1m"],
    ['{bright_magenta}', "\u001b[35;1m"],
    ['{bright_cyan}',    "\u001b[36;1m"],
    ['{bright_white}',   "\u001b[37;1m"],
    
    ['{bg_black}',   "\u001b[40m"],
    ['{bg_red}',     "\u001b[41m"],
    ['{bg_green}',   "\u001b[42m"],
    ['{bg_yellow}',  "\u001b[43m"],
    ['{bg_blue}',    "\u001b[44m"],
    ['{bg_magenta}', "\u001b[45m"],
    ['{bg_cyan}',    "\u001b[46m"],
    ['{bg_white}',   "\u001b[47m"],
    
    ['{bg_bright_black}',   "\u001b[40;1m"],
    ['{bg_bright_red}',     "\u001b[41;1m"],
    ['{bg_bright_green}',   "\u001b[42;1m"],
    ['{bg_bright_yellow}',  "\u001b[43;1m"],
    ['{bg_bright_blue}',    "\u001b[44;1m"],
    ['{bg_bright_magenta}', "\u001b[45;1m"],
    ['{bg_bright_cyan}',    "\u001b[46;1m"],
    ['{bg_bright_white}',   "\u001b[47;1m"],
    
    ['{reset}',     "\u001b[0m"],
    ['{bold}',      "\u001b[1m"],
    ['{italic}',    "\u001b[3m"],
    ['{underline}', "\u001b[4m"],
    ['{blink}',     "\u001b[5m"],
    ['{invert}',    "\u001b[7m"],
    ['{hide}',      "\u001b[8m"],
    
    ['{newline}', "\n"]
]

def colorFormatter(text):
    for i in color_codes:
        text = text.replace(i[0], i[1])
        
    return text

def new_format_usage(self=None, usage=None, actions=None, groups=None, prefix=None):
    return colorFormatter(
'''Usage:
{bold}{bg_bright_black}run-crossplatform.bat
{bright_cyan}file
{white}[{bright_cyan}-h{white}]
{white}[{bright_cyan}-n{white}]
{white}[
{red}[{bright_cyan}-c {green}CPS{red}]
{red}[{bright_cyan}-m {green}MEM_CELLS{red}]
{red}[{bright_cyan}-w {green}WIDTH{red}]
{red}[{bright_cyan}-e {green}HEIGHT{red}]
{white}|
{blue}[{bright_cyan}-g{blue}]
{white}]{reset}{newline}'''.replace('\n', " ")
    )

def newHelpMessage(*args, **kwargs):
    return f'''{new_format_usage()}

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
'''

argparse.ArgumentParser.format_help = newHelpMessage
argparse.ArgumentParser.format_usage = new_format_usage

parser = argparse.ArgumentParser(add_help=False, prog='run-crossplatform.bat')
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
