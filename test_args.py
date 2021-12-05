import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="The file to execute")
parser.add_argument("-c", "--cps", type=float, default=16, help="How many commands to execute per second")
parser.add_argument("-n", "--no-kitty", help="Disable Kitty commands", action="store_true")
parser.add_argument("-g", "--no-text", help="Disable debug rendering, this also makes the board size dynamic and memory to have any number of cells, and instructions will execute as fast as possible", action="store_true")
parser.add_argument("-m", "--mem-cells", type=int, default=32, help="Memory cells to have")
parser.add_argument("-w", "--width", type=int, default=32, help="Width of the board in cells")
parser.add_argument("-e", "--height", type=int, default=32, help="Height of the board in cells")
args = parser.parse_args()
