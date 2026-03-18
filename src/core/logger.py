import sys
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def get_logger(name:str):
    logger=logging.getLogger(name)
    ch=logging.StreamHandler(sys.stdout)
    logger.addHandler(ch)
    return logger