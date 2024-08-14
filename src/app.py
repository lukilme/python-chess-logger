from src.analyserChess import AnalyserChess
from src.repository import Repository
import pandas as pd

class Application:
    def __init__(self):
        self.analyseChess = AnalyserChess()
        self.repository = Repository()

    def analyseGame(self, path_game):
        path_game = '\\src\\data\\games\\'+path_game+'.pgn'
        print(path_game)
        gameAnalyse = self.analyseChess.analyse(path_game)
        self.repository.saveAnalysis(gameAnalyse)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        print(gameAnalyse)

    def showGame(self, id_game):
        print(id_game)
        gameAnalyse = self.repository.getAnalysis(1)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        print(gameAnalyse)