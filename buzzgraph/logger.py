import os
import json
import logging.config

class Logger(object):
    def __init__(self, name):
        logger = logging.getLogger(name)
        self._logger = logger

    def get(self):
        return self._logger

def setup_logging(
    default_path='resources/logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):

    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        print("Loading logging config:", path)
        logging.config.dictConfig(config)
    else:
        print("Using Default logging config")
        logging.basicConfig(level=default_level)

setup_logging()
