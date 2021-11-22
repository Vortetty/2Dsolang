import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--commands-per-second", type=float, default=16, help="How many commands to execute per second")
parser.add_argument("file", type=str, help="The file to execute")
args = parser.parse_args()
