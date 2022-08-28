#This file reads chessData.csv

from math import pow

#takes evaluation as a string (+243, #-2) and turns it into a squished evaluation with the sigmoid function
def sf_sigmoid(x) -> float:
    if x[0] == '#':
        if x[1] == ['-']:
            return 0
        else:
            return 1

    try:
        x = float(x) / 100
    except:
        print("EXEPTION", x)
        return .5
    x = 1/(1+pow(2.71828, -x))
    return x

#takes like from csv file (with \n at the end)
#returns list [FEN, SQUISHED_EVALUATION]
def process_line(line) -> list:
    line = line[:-1].split(",")
    line[1] = sf_sigmoid(line[1])

    return line
