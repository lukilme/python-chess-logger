import pathlib
import pickle
import glob
import os
import subprocess
import json
import logging

class Configuration:
    def __init__(self, root):
        self.root = root
        self.last_id_game = 0
        self.last_id_analysis = 0
        self.load()
    
    def save(self):
        try:
            config_data = {
                'last_id_game': self.last_id_game,
                'last_id_analysis': self.last_id_analysis
            }
            os.makedirs(f'{self.root}/python-chess-logger', exist_ok=True)
            with open(f'{self.root}/python-chess-logger/config.json', "w") as f:
                json.dump(config_data, f)
        except Exception as e:
            logging.error(e)
            print(e)

    def load(self):
        try:
            with open(f'{self.root}/python-chess-logger/config.json', "r") as f:
                loaded_config = json.load(f)
                self.last_id_game = loaded_config.get('last_id_game', 0)
                self.last_id_analysis = loaded_config.get('last_id_analysis', 0)
        except Exception as e:
            logging.error(e)
            print(e)
    
class Repository:
    def __init__(self):
        self.system = "Windows"
        self.root = pathlib.Path().resolve()
        self.config = Configuration(self.root.parent)
        self.database = str(self.root) + "/src/data"
        logging.info("Repository started!")
    

    def saveGame(self, savedGame):
        try:
            game_dir = os.path.join(self.database, 'games')
            os.makedirs(game_dir, exist_ok=True)
            
            file_path = os.path.join(game_dir, f'game{self.config.last_id_game + 1}.bin')
            logging.warning(f"Saving game to: {file_path}")

            with open(file_path, "wb") as f:
                self.config.last_id_game += 1
        
                pickle.dump(savedGame, f)
                logging.info(f"Game saved successfully!")
                self.config.last_id_game+=1
                self.config.save()
                
        except Exception as e:
            logging.error(f"Failed to save game: {e}")
            print(f"Failed to save game: {e}")

    def saveAnalysis(self, savedAnalysis):
        try:
            analysis_dir = os.path.join(self.database, 'analysis')
            os.makedirs(analysis_dir, exist_ok=True)
            file_path = os.path.join(analysis_dir, f'analysis{self.config.last_id_analysis + 1}.bin')
            logging.warning(f"Saving analysis to: {file_path}")
            
            with open(file_path, "wb") as f:
                pickle.dump(savedAnalysis, f)
                logging.info(f"Analysis saved successfully!")
                self.config.last_id_analysis+=1
                self.config.save()
        except Exception as e:
            logging.error(f"Failed to save analysis: {e}")
            print(f"Failed to save analysis: {e}")

    def getGame(self, idGame):
        try:
            with open(self.database+f'/games/game{idGame}.bin', "rb") as f:
                d = pickle.load(f)
                return d
        except Exception as e:
            print(e)

    def getAnalysis(self, idAnalysis):
        try:
            with open(self.database+f'/analysis/analysis{idAnalysis}.bin', "rb") as f:
                d = pickle.load(f)
                return d
        except Exception as e:
            print(e)


    def listContent(self, folder: str) -> list[list]:
        result = glob.glob(folder)

        for folder in result:
            print(folder.replace(str(self.database),""))


    def executeCommand(self, command):
        current_os = self.system
        if current_os == "Windows":
            command_list = ["cmd.exe", "/c", command]
        elif current_os in ["Linux", "Darwin"]:
            command_list = ["sh", "-c", command]
        else:
            return f"Unsupported operating system: {current_os}"

        try:
            resultado = subprocess.check_output(
                command_list, stderr=subprocess.STDOUT, shell=True, text=True
            )
            return resultado
        except subprocess.CalledProcessError as e:
            return f"Error executing command: {e.output}"
        
    def closeRepository(self):
        self.config.save()
