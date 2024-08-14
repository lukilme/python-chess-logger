import pathlib
import pickle
import glob
import os
import subprocess
import json

class Path:
    def __init__(self, path):
        self.path = path
        self.name = self._get_name(path)  # Extract name using a helper function

    def _get_name(self, path):
        return os.path.basename(path) 

class Directory(Path):
    def __init__(self, path):
        super().__init__(path) 
        self.children = list()

class File(Path):
    def __init__(self, path):
        super().__init__(path)  
        self.extension = self._get_extension(path) 

    def _get_extension(self, path):
        return os.path.splitext(path)[1]  


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
            os.makedirs(f'{self.root}\\chess-logger', exist_ok=True)
            with open(f'{self.root}\\chess-logger\\config.json', "w") as f:
                json.dump(config_data, f)
        except Exception as e:
            print(e)

    def load(self):
        try:
            with open(f'{self.root}\\chess-logger\\config.json', "r") as f:
                loaded_config = json.load(f)
                self.last_id_game = loaded_config.get('last_id_game', 0)
                self.last_id_analysis = loaded_config.get('last_id_analysis', 0)
        except Exception as e:
            print("Erro ao carregar a configuração.")
            print(e)
    
class Repository:
    def __init__(self):
        self.system = "Windows"
        self.root = pathlib.Path().resolve()
        self.config = Configuration(self.root.parent)
        self.database = str(self.root) + "\\src\\data"
    

    def saveGame(self, savedGame):
        try:
            with open(self.database+f'\\games\\game{self.config.last_id_game+1}.bin', "wb") as f:
                self.config.last_id_game+=1
                pickle.dump(savedGame, f)
        except Exception as e:
            print(e)

    def saveAnalysis(self, savedAnalysis):
        try:
            print(self.database)
            with open(self.database+f'\\analysis\\analysis{self.config.last_id_analysis+1}.bin', "wb") as f:
                self.config.last_id_analysis+=1
                pickle.dump(savedAnalysis, f)
        except Exception as e:
            print(e)

    def getGame(self, idGame):
        try:
            with open(self.database+f'\\games\\game{idGame}.bin', "rb") as f:
                d = pickle.load(f)
                return d
        except Exception as e:
            print(e)

    def getAnalysis(self, idAnalysis):
        try:
            print(self.database+f'\\analysis\\analysis{idAnalysis}.bin')
            with open(self.database+f'\\analysis\\analysis{idAnalysis}.bin', "rb") as f:
                d = pickle.load(f)
                return d
        except Exception as e:
            print(e)


    def listContent(self, folder: str) -> list[list]:
        #str(repo.database / "*")
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


if __name__ == '__main__':
    repo = Repository()
    print(repo.root)
    repo.closeRepository()
    
    #repo.listContent2(repo.database)

