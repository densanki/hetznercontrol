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

    def get_ipv4_by_hostname(hostname):
        # see `man getent` `/ hosts `
        # see `man getaddrinfo`

        return list(
            i  # raw socket structure
            [4]  # internet protocol info
            [0]  # address
            for i in
            socket.getaddrinfo(
                hostname,
                0  # port, required
            )
            if i[0] is socket.AddressFamily.AF_INET  # ipv4

            # ignore duplicate addresses with other socket types
            and i[1] is socket.SocketKind.SOCK_RAW
        )