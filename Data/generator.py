import chess.pgn
import chess
from stockfish import Stockfish
from math import pow
import sys
import threading
from threading import Lock

pgn = None
outfile = None

lines = []
outfileMutex = Lock()

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


def write_game(game, stockfish):
    global linesDone
    lines = ""

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
        lines += (board.fen() + "," + evalString + "\n")

        print(linesDone)
        linesDone+=1

        outfileMutex.acquire()
        outfile.write(lines)
        outfileMutex.release()

def write_games(games):
    stockfish = Stockfish("./Stockfish/src/stockfish")
    stockfish.set_depth(9)

    for g in games:
        write_game(g, stockfish)

def run(filename):
    global pgn, outfile
    pgn = open(filename + '.pgn', 'r')
    outfile = open(filename + ".csv", 'w')

    threads = []

    while True:
        for thr in range(12):
            games = []
            for i in range(100):
                games.append(list(chess.pgn.read_game(pgn).mainline_moves()))
            # write_games(games)
            thread = threading.Thread(target=write_games, args=(games,))
            thread.start()
            threads.append(thread)

        for thr in threads:
            thr.join()


if __name__ == '__main__':
    print(sys.argv)
    run(sys.argv[1])
