from src.app import Application

app = Application()
while(True):
    entrada = input()
    if entrada == 'exit':
        break
    else:
        app.analyseGame('1')
    
