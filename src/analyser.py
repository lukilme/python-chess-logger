import chess
from collections import Counter
import pathlib
import io
import chess.pgn as chess_pgn
from view.loadingWindow import LoadingWindow
import pandas as pd

class AnalyserTool:
    @staticmethod
    def material_balance(board):
        """
        This function calculates the material
        difference between White and Black.
        """
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
        """
        This function evaluates how well each
        side has developed their pieces.
        """
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
        """
        This function calculates the number of legal
        moves available to the current player."""
        mobility = len(list(board.legal_moves))
        return mobility

    @staticmethod
    def calculate_control(board):
        """
        This function calculates the difference in
        the number of squares controlled by each side.
        """
        control = sum(
            len(board.attackers(chess.WHITE, square))
            - len(board.attackers(chess.BLACK, square))
            for square in chess.SQUARES
        )
        return control

    @staticmethod
    def calculate_tension(board):
        """
        This function calculates the number of squares
        that are under attack by both White and Black.
        """
        tension = sum(
            1
            for square in chess.SQUARES
            if board.is_attacked_by(chess.WHITE, square)
            and board.is_attacked_by(chess.BLACK, square)
        )
        return tension

    @staticmethod
    def calculate_king_safety(board):
        """
        calculate the number of pieces that are in
        contact with the king's sensitive squares, by distance of rist
        """
        safety = 0
        for king_square in [board.king(chess.WHITE), board.king(chess.BLACK)]:
            for piece_square in chess.SQUARES:
                piece = board.piece_at(piece_square)
                if piece:
                    distance = max(chess.square_distance(king_square, piece_square), 1)
                    # safety += piece.piece_type / distance
                    safety += piece.piece_type
        return safety

class AnalyserChess:
    def __init__(self):
        self.path = pathlib.Path().resolve()
        self.enginepath = str(self.path)+"./../engines/stockfish/"
        self.enginefile = "stockfish-windows-x86-64-sse41-popcnt"
        self.totaltime = 1 
    
    def analyse(self, path_game):
        with io.open(str(self.path) + path_game, encoding="utf-8-sig") as pgnin:
            game = chess_pgn.read_game(pgnin)
        board = chess.Board()
        gamedata = []
        node = game
        plytotal = sum(1 for _ in node.mainline())
        time = self.totaltime * 80 / plytotal 
        root = LoadingWindow("Game Analisys!")
        counter = 0
        moves_len = (len(str(game.mainline_moves()).split(".")) - 2) * 2
        with chess.engine.SimpleEngine.popen_uci(self.enginepath + self.enginefile) as engine:
            node = game
            cap = 30  
            ply = 0
            matedist = "N/A"
            while not node.is_end():
                next_node = node.variations[0]
                move = node.board().san(next_node.move)
                side = "W" if board.turn else "B"
                capprior = cap

                try:
                    result = engine.analyse(board, chess.engine.Limit(time=time))
                    score = result['score'].relative

                    if isinstance(score, chess.engine.Cp):
                        cap = score.score()
                    elif isinstance(score, chess.engine.Mate):
                        cap = score.mate() * 10000 if score.mate() is not None else 0
                        matedist = score.mate() if score.mate() is not None else "N/A"
                    
                    depth = result['depth']
                    suggested = board.san(result['pv'][0]) if 'pv' in result else "N/A"

                    if side == "B":
                        cap = -cap

                    cpdelta = cap - capprior

                    board.push(next_node.move)  

                    material = AnalyserTool.material_balance(board)
                    development = AnalyserTool.calculate_development(board)
                    mobility = AnalyserTool.calculate_mobility(board)
                    control = AnalyserTool.calculate_control(board)
                    tension = AnalyserTool.calculate_tension(board)
                    safety = AnalyserTool.calculate_king_safety(board)

                    movedata = (ply, side, move, cap, matedist, cpdelta, suggested, depth, material,
                                development, mobility, control, tension, safety)

                    gamedata.append(movedata)

                    ply += 1
                    node = next_node
                    counter += 1
                    if counter == moves_len:
                        root.close_window()
                    root.update_progress(round((counter / moves_len * 100), 2))
                    
                    root.update()
                
                except Exception as e:
                    print(f"Something wrong: {e}")
                    break
        gamedata = pd.DataFrame(gamedata, columns=['Ply', 'Side', 'Move', 'CP', 'Mate', 'CP Delta', 'Suggested', 'Depth', 'Material',
                                                    'Development', 'Mobility', 'Control', 'Tension', 'Safety'])
        gamedata['CP'] = gamedata['CP'].shift(-1)
        gamedata['CP Delta'] = gamedata['CP Delta'].shift(-1)
        return gamedata
        

