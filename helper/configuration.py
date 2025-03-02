import configparser
import socket

from logging_config import logger
import os

class Configuration:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.load_configuration(config_file)

    def load_configuration(self, config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        self.config.read(config_file)

    def get(self, section, option, fallback=None):
        try:
            return self.config.get(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
