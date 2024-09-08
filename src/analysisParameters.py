import chess
from collections import Counter

class analysisParameters:
    @staticmethod
    def material_balance(board):
        piece_values = {"p": 100, "n": 300, "b": 300, "r": 500, "q": 900, "k": 20000}
        pieces = Counter(board.piece_map().values())
        white_material = sum(
            piece_values[p.symbol().lower()] for p in pieces if p.color == chess.WHITE
        )
        black_material = sum(
            piece_values[p.symbol().lower()] for p in pieces if p.color == chess.BLACK
        )
        return white_material - black_material

    @staticmethod
    def calculate_development(board):
        initial_squares = {
            chess.A1,
            chess.B1,
            chess.C1,
            chess.D1,
            chess.E1,
            chess.F1,
            chess.G1,
            chess.H1,
            chess.A8,
            chess.B8,
            chess.C8,
            chess.D8,
            chess.E8,
            chess.F8,
            chess.G8,
            chess.H8,
        }
        development = 0
        for square in initial_squares:
            piece = board.piece_at(square)
            if piece:
                if (piece.color == chess.WHITE and square < chess.A2) or (
                    piece.color == chess.BLACK and square > chess.H7
                ):
                    development -= 1
                else:
                    development += 1
        return development

    @staticmethod
    def calculate_mobility(board):
        mobility = len(list(board.legal_moves))
        return mobility

    @staticmethod
    def calculate_control(board):
        control = sum(
            len(board.attackers(chess.WHITE, square))
            - len(board.attackers(chess.BLACK, square))
            for square in chess.SQUARES
        )
        return control

    @staticmethod
    def calculate_tension(board):
        tension = sum(
            1
            for square in chess.SQUARES
            if board.is_attacked_by(chess.WHITE, square)
            and board.is_attacked_by(chess.BLACK, square)
        )
        return tension

    @staticmethod
    def calculate_king_safety(board):
        safety = 0
        for king_square in [board.king(chess.WHITE), board.king(chess.BLACK)]:
            for piece_square in chess.SQUARES:
                piece = board.piece_at(piece_square)
                if piece:
                    distance = max(chess.square_distance(king_square, piece_square), 1)
                    safety += piece.piece_type / distance
                    #safety += piece.piece_type
        return safety