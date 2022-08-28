from lib2to3.pgen2 import pgen
from lib2to3.pgen2.literals import evalString
import chess.pgn
import chess
from stockfish import Stockfish
from math import pow
import sys

pgn = None
outfile = None

stockfish = Stockfish("./Stockfish/src/stockfish")
stockfish.set_depth(9)

def sf_sigmoid(x):
    if x['Mate'] is not None:
        if x['Mate'] < 0: return 0
        return 1
    return 1/(1+pow(2.71828, (-x['Centipawn']/100)))

def sf_evaluation_to_string(x):
    if x['Mate'] is not None:
        return "#" + str(x['Mate'])
    return str(x['Centipawn'])

linesDone = 0

def write_game(game):
    global linesDone
    board = chess.Board()
    for move in game:
        board.push(move)
        if board.is_game_over(): break

        stockfish.set_fen_position(board.fen())
        multipv = stockfish.get_top_moves(5)

        diff = abs(sf_sigmoid(multipv[0]) - sf_sigmoid(multipv[-1]))
        if diff > .3:
            print("rejected", board.fen(), diff)
            continue

        evalString = sf_evaluation_to_string(multipv[0])
        outfile.write(board.fen() + "," + evalString + "\n")

        print(linesDone)
        linesDone+=1


def run(filename):
    global pgn, outfile
    pgn = open(filename + '.pgn', 'r')
    outfile = open(filename + ".csv", 'w')

    while True:
        game = list(chess.pgn.read_game(pgn).mainline_moves())
        write_game(game)

if __name__ == '__main__':
    print(sys.argv)
    run(sys.argv[1])
