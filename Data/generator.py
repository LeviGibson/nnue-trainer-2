import chess.pgn
import chess
from stockfish import Stockfish
from math import pow
import sys
import threading
from threading import Lock
from math import floor

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


def write_game(game, stockfish):
    global linesDone
    lines = ["", "", "", "", ""]

    board = chess.Board()
    for move in game:
        board.push(move)
        if board.is_game_over(): break

        stockfish.set_fen_position(board.fen())
        multipv = stockfish.get_top_moves(1)

        diff = abs(sf_sigmoid(multipv[0]) - sf_sigmoid(multipv[-1]))
        if diff > .4999:
            # print("rejected", board.fen(), diff)
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

def write_games(games):
    stockfish = Stockfish("./Stockfish/src/stockfish")
    stockfish.set_depth(9)

    for g in games:
        write_game(g, stockfish)
    stockfish.__del__()

def run(filename):
    global pgn, outfile
    pgn = open(filename + '.pgn', 'r')
    outfile = [
        open("1.csv", 'w'),
        open("2.csv", 'w'),
        open("3.csv", 'w'),
        open("4.csv", 'w'),
        open("5.csv", 'w')
        ]

    threads = []

    while True:
        for thr in range(16):
            games = []
            for i in range(20):
                games.append(list(chess.pgn.read_game(pgn).mainline_moves()))
            # write_games(games)
            thread = threading.Thread(target=write_games, args=(games,))
            thread.start()
            threads.append(thread)

        for thr in threads:
            thr.join()
        print("ALL THREADS FINISHED")

if __name__ == '__main__':
    print(sys.argv)
    run(sys.argv[1])
