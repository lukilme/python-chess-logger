import pathlib
import pickle
import glob
import os
import subprocess

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


class Repository:
    def __init__(self):
        self.system = "Windows"
        self.root = pathlib.Path().resolve()
        self.parent = {"path":"","type":"root","name":"root","date":"nome",'data':list()}
        self.database = self.root / "data"
    
    def saveGame(self):
        pass

    def saveAnalysis(self):
        pass

    def getGame(self):
        pass

    def getAnalysis(self):
        pass

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

    def listContent2(self, folder: str, parent = None):
        if not parent:
            parent = self.parent
        if self.system == "Windows":  # Windows
            command = "dir " + str(folder)
        else:  # Linux ou MacOS
            command = "ls -l " + str(folder)
        result = self.executeCommand(command).split("\n")
        result = result[7:len(result)-3]
        files = []
        directories = []
        for part in result:
            content = {"type":"","name":"","date":"",'data':list()}
            parts = part.split(" ")
            content['data']=parts[0]+':'+parts[2]
            content['name']=parts[len(parts)-1]
            if '<DIR>' in parts:
                content['type']='directory'
                directories.append(content)
                print(content['name'])
            else:
                content['type']='file'
                files.append(content)
        result = directories+files

       
if __name__ == '__main__':
    repo = Repository()
    print(repo.root)
    print("save file")
    data_path = repo.database / "logfile.bin"
    print(data_path)

    if not data_path.parent.exists():
        os.makedirs(data_path.parent)


    with open(data_path, "wb") as f:
        dct = {"name": "Rajeev", "age": 30, "Gender": "Male", "marks": 75}
        pickle.dump(dct, f)

    print("load file")
    with open(data_path, "rb") as f:
        d = pickle.load(f)
        print(d)
    
    repo.listContent(str(repo.database / "*"))

    repo.listContent2(repo.database)

