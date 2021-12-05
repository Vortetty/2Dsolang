import argparse

parser = argparse.ArgumentParser(description='Generate 2Dsolang from Brainfuck.')
parser.add_argument('input', type=str, help='Input file.')
parser.add_argument('-o', '--out', type=str, help='Output file.')
args = parser.parse_args()

if args.out is None:
    args.out = args.input + '.2dl'
    
infile = open(args.input, 'r')
inText = infile.read()

neededLines = 1
neededCols = 1

currentDepth = 0
maxDepth = 0

for i in inText:
    if i == '>':
        neededCols += 1
    elif i == '<':
        neededCols += 1
    elif i == '+':
        neededCols += 1
    elif i == '-':
        neededCols += 1
    elif i == '.':
        neededCols += 1
    elif i == ',':
        neededCols += 1
    elif i == '[':
        neededCols += 6
        currentDepth += 1
        maxDepth = max(currentDepth, maxDepth)
    elif i == ']':
        neededCols += 6
        currentDepth -= 1
        maxDepth = max(currentDepth, maxDepth)

neededLines = maxDepth*2+1
        
outBuffer = [
    [" " for x in range(neededCols)] for i in range(neededLines)
]

curCol = 0
curDepth = 0

for i in inText:
    if i == '>':
        outBuffer[0][curCol] = '/'
        curCol += 1
    elif i == '<':
        outBuffer[0][curCol] = '\\'
        curCol += 1
    elif i == '+':
        outBuffer[0][curCol] = '+'
        curCol += 1
    elif i == '-':
        outBuffer[0][curCol] = '-'
        curCol += 1
    elif i == '.':
        outBuffer[0][curCol] = '%'
        curCol += 1
    elif i == ',':
        outBuffer[0][curCol] = 'i'
        curCol += 1
    elif i == '[':
        curDepth += 1
        outBuffer[0][curCol] =   '|'
        outBuffer[max(curDepth*2-1, 0)][curCol] =   '{'
        outBuffer[0][curCol+1] = '.'
        outBuffer[0][curCol+2] = '0'
        outBuffer[0][curCol+3] = '0'
        outBuffer[0][curCol+4] = '0'
        outBuffer[0][curCol+5] = '}'
        outBuffer[max(curDepth*2, 0)][curCol+5] =   ']'
        curCol += 6
    elif i == ']':
        outBuffer[0][curCol] =   '|'
        outBuffer[max(curDepth*2, 0)][curCol] =   '{'
        outBuffer[0][curCol+1] = ':'
        outBuffer[0][curCol+2] = '0'
        outBuffer[0][curCol+3] = '0'
        outBuffer[0][curCol+4] = '0'
        outBuffer[0][curCol+5] = '}'
        outBuffer[max(curDepth*2-1, 0)][curCol+5] =   '['
        curDepth -= 1
        curCol += 6
        
outBuffer[0][-1] = '~'

outfile = open(args.out, 'w')
outfile.write('\n'.join("".join(i) for i in outBuffer))

outfile.close()
infile.close()
