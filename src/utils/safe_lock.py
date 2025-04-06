from src.utils.logger import *

def singleton(cls):
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class safe_lock:
    
    def design_structure_checker():
        pass

    def builder_structure():
        pass



