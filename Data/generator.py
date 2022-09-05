import chess.pgn
import chess
from stockfish import Stockfish
from math import pow
import sys
import threading
from threading import Lock
from math import floor
import random

pgn = None
outfile = None

outfileMutex = Lock()

def sf_sigmoid(x):
    if x['Mate'] is not None:
        if x['Mate'] < 0: return 0
        return 1
    return 1/(1+pow(2.71828, (-x['Centipawn']/410)))

def sf_evaluation_to_string(x):
    if x['Mate'] is not None:
        return "#" + str(x['Mate'])
    return str(x['Centipawn'])

linesDone = 0

def get_random_opening(stockfish : Stockfish):
    board = chess.Board()
    for i in range(6):
        legalMoves = list(board.legal_moves)
        board.push(legalMoves[random.randint(0, len(legalMoves)-1)])
    
    fen = board.fen()
    stockfish.set_fen_position(fen)
    evaluation = stockfish.get_evaluation()
    diff = abs(evaluation['value'])

    if diff < 150 and evaluation['type'] == 'cp':
        return fen

    return get_random_opening(stockfish)

def write_game(stockfish : Stockfish):
    global linesDone

    startpos = get_random_opening(stockfish)

    lines = ["", "", "", "", ""]

    board = chess.Board(startpos)
    while not board.is_game_over():
        multipv = stockfish.get_top_moves(5)

        diff = abs(sf_sigmoid(multipv[0]) - sf_sigmoid(multipv[-1]))

        board.push_uci(multipv[0]["Move"])
        stockfish.make_moves_from_current_position([multipv[0]["Move"]])

        if diff > .4999:
            continue

        evalString = sf_evaluation_to_string(multipv[0])
        lines[floor(diff*10)] += (board.fen() + "," + evalString + "\n")

        if linesDone % 500 == 0:
            print(linesDone)
        linesDone+=1

    outfileMutex.acquire()
    for i in range(len(lines)):
        outfile[i].write(lines[i])
    outfileMutex.release()

def write_games():
    stockfish = Stockfish("./Stockfish/src/stockfish")
    stockfish.set_depth(9)

    for g in range(20):
        write_game(stockfish)
    stockfish.__del__()

def run():
    global pgn, outfile
    outfile = [
        open("1.csv", 'a'),
        open("2.csv", 'a'),
        open("3.csv", 'a'),
        open("4.csv", 'a'),
        open("5.csv", 'a')
        ]

    threads = []

    while True:
        for thr in range(16):
            thread = threading.Thread(target=write_games)
            thread.start()
            threads.append(thread)

        for thr in threads:
            thr.join()
        print("ALL THREADS FINISHED")

if __name__ == '__main__':
    run()
