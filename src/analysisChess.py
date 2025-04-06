import chess
from chess import engine
import pathlib
import io
import chess.engine
import chess.pgn as chess_pgn
from src.view.loadingWindow import LoadingWindow
import pandas as pd
from src.analysisParameters import analysisParameters

class MetaDataGame:
    def __init__(self, event, site, date, round, black, white, result):
        self.event = event
        self.site = site
        self.date = date
        self.round = round
        self.black = black
        self.white = white
        self.result = result

class AnalyserChess:
    def __init__(self):
        self.path = pathlib.Path().resolve()
        self.enginepath = str(self.path)+"/engine/stockfish/"
        self.actual_engine = "stockfish-ubuntu-x86-64"
        self.totaltime = 1 
    
    def analyse(self, path_game):
        with io.open(str(self.path) + path_game, encoding="utf-8-sig") as pgnin:
            game = chess_pgn.read_game(pgnin)
        board = chess.Board()
        gamedata = []
        node = game
        plytotal = sum(1 for _ in node.mainline())
        time = self.totaltime * 12 / plytotal 
        root = LoadingWindow("Game Analisys!")
        counter = 0
        moves_len = (len(str(game.mainline_moves()).split(".")) - 2) * 2

        with chess.engine.SimpleEngine.popen_uci(self.enginepath + self.actual_engine) as engine:
            engine : chess.engine.SimpleEngine = engine
           
            node = game
            cap = 30  
            ply = 0
            matedist = "N/A"
            metaDataGame = MetaDataGame(
                game.headers["Event"],
                game.headers["Site"],
                game.headers["Date"],
                game.headers["Round"],
                game.headers["White"],
                game.headers["Black"],
                game.headers["Result"]
            )
            while not node.is_end():
                next_node = node.variations[0]
                move = node.board().san(next_node.move)
                side = "W" if board.turn else "B"
                capprior = cap

                try:
                    result = engine.analyse(board, chess.engine.Limit(time=time))
                    print(result)
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

              
                    top_moves = engine.analyse(board, chess.engine.Limit(time=time), multipv=3)
                    print("="*60)
                    print(len(top_moves))
                    print(top_moves)
                    print("="*60)
                    board.push(next_node.move)  

                    material = analysisParameters.material_balance(board)
                    development = analysisParameters.calculate_development(board)
                    mobility = analysisParameters.calculate_mobility(board)
                    control = analysisParameters.calculate_control(board)
                    tension = analysisParameters.calculate_tension(board)
                    safety = analysisParameters.calculate_king_safety(board)

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
                    raise(e)
        
        gamedata = pd.DataFrame(gamedata, columns=['Ply', 'Side', 'Move', 'CP', 'Mate', 'CP Delta', 'Suggested', 'Depth', 'Material',
                                                    'Development', 'Mobility', 'Control', 'Tension', 'Safety'])
        gamedata['CP'] = gamedata['CP'].shift(-1)
        gamedata['CP Delta'] = gamedata['CP Delta'].shift(-1)
        pgnin.close()
        return metaDataGame, gamedata
        