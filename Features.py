import chess
from chess import Board
import numpy as np

flipPers = [56, 57, 58, 59, 60, 61, 62, 63,
  48, 49, 50, 51, 52, 53, 54, 55,
  40, 41, 42, 43, 44, 45, 46, 47,
  32, 33, 34, 35, 36, 37, 38, 39,
  24, 25, 26, 27, 28, 29, 30, 31,
  16, 17, 18, 19, 20, 21, 22, 23,
  8, 9, 10, 11, 12, 13, 14, 15,
  0, 1, 2, 3, 4, 5, 6, 7]

def piece_to_ordinal(piece):
    return (piece.piece_type - 1) + ((not piece.color) * 6)

def main_features(board, pmap):
    features = np.zeros((12, 64), dtype=int)
    for p in pmap:
        features[piece_to_ordinal(pmap[p])][flipPers[p]] = 1
    return features.flatten()

def material(board, pmap):
    features = np.zeros((12,), dtype=int)
    for p in pmap:
        features[piece_to_ordinal(pmap[p])] += 1
    return features

def unprotected(board : Board, pmap):
    pv = [1, 3, 3, 5, 9, 0, 1, 3, 3, 5, 9, 0]
    features = np.zeros(shape=(2, 64), dtype=int)

    for s in pmap:
        piece = pmap[s]
        if not board.is_attacked_by(piece.color, s):
            features[int(piece.color)][s] = pv[piece_to_ordinal(piece)] / 9
            
    return features.flatten()

def attacked(board : Board, pmap):
    features = np.zeros((12, 64), dtype=int)

    for sq in pmap:
        pieceOrd = piece_to_ordinal(pmap[sq])
        attacks = np.array(board.attacks(sq).tolist()).astype(int)
        features[pieceOrd] += attacks
    
    return features.flatten()
                
def turn(board : Board, pmap):
    return np.array([int(board.turn)])

def castling_rights(board : Board, pmap):
    return np.array([board.has_castling_rights(chess.WHITE),
                    board.has_queenside_castling_rights(chess.WHITE),
                    board.has_castling_rights(chess.BLACK),
                    board.has_queenside_castling_rights(chess.BLACK)]).astype(int)

def extra_features(board, pmap):
    # return material(board)
    return np.concatenate((material(board, pmap), turn(board, pmap)), axis=0)

def get(fen):
    board = Board(fen)
    pmap = board.piece_map()
    return np.concatenate((main_features(board, pmap), extra_features(board, pmap)), axis=0)
    # return main_feat

if __name__ == '__main__':
    print(len(list(get("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))))
