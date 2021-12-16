#
# Generates 2Dsolang from C.
# requires https://github.com/shinh/elvm
#

ELVM_DIR = "linux-x64-elvm"

try:
    import pyjion
    pyjion.config(level=2)
    pyjion.enable()
except: pass
import os
import argparse

parser = argparse.ArgumentParser(description='Generate 2Dsolang from C')
parser.add_argument('input', help='Input C file',)
parser.add_argument('-o', '--output', help='Output C file', required=True)
args = parser.parse_args()

print("\n" + ELVM_DIR + "/8cc -S " + args.input + " -o " + args.output + ".s" + " -I" + ELVM_DIR + "/libc -I" + ELVM_DIR + "/libc/sys")
os.system(ELVM_DIR + "/8cc -S " + args.input + " -o " + args.output + ".s" + " -I" + ELVM_DIR + "/libc -I" + ELVM_DIR + "/libc/sys")

print("\n" + ELVM_DIR + "/elc -bf " + args.output + ".s")
os.system("\n" + ELVM_DIR + "/elc -bf " + args.output + ".s >> " + args.output + ".bf")

print("\npython3 gen_from_bf.py " + args.output + ".bf -o " + args.output)
os.system("python3 gen_from_bf.py " + args.output + ".bf -o " + args.output)
