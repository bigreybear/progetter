import yaml
import logging.config

with open("log.yaml") as f:
    logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger("fileLogger")

if __name__ == '__main__':
    logger.info("In main.")
