import yaml
import logging.config
import sys
import os

# Change dir silently to load the config file.
ori_path = os.getcwd()
# os.chdir("/Pyproject/ProfGetter/")
os.chdir("D:\GitRepo\progetter\\")
print("Process on:" + str(os.getcwd()))
with open("log.yaml") as f:
    log_ = logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger("fileLogger")
os.chdir(ori_path)
logger.info("Process path: " + str(os.getcwd()))

if __name__ == '__main__':
    logger.info("In main.")
