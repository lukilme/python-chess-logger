import logging
import datetime
import os

def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',  
        datefmt='%H:%M:%S',  
        handlers=[
            logging.FileHandler(f"./logger/{date}.log", mode='w'),
        ]
    )
        
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', 
            datefmt='%H:%M:%S'
    ))
    logging.getLogger().addHandler(console_handler)