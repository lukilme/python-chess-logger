from src.analysisChess import AnalyserChess
from src.repository import Repository
from src.visualAnalysis import VisualAnalysis
import pandas as pd

class Application:
    def __init__(self):
        self.analyseChess = AnalyserChess()
        self.repository = Repository()
        self.graph = VisualAnalysis()

    def analyseGame(self, path_game):
        path_game = '\\src\\data\\games\\game'+str(path_game)+'.pgn'
        print(path_game)
        metaDataGame, gameAnalyse = self.analyseChess.analyse(path_game)
        self.repository.saveAnalysis(gameAnalyse)
        self.graph.showTerminal( gameAnalyse)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
  

    def showGame(self, id_game):
        print(id_game)
        gameAnalyse = self.repository.getAnalysis(id_game)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        self.graph.showTerminal(gameAnalyse)