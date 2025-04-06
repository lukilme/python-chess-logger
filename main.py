import logging
from src.app import Application
import src.utils.logger as lg
import os


app = Application()
entrada = ''
while(True):
    entrada = input('input: ')
    if(entrada!='0'):
        app.analyse_game(entrada)
    else:
        break


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))

logging.getLogger().addHandler(console_handler)

