import json

from helper.ssh_manager import SSHManager
from logging_config import logger
import time

import requests

from helper.configuration import Configuration
from model.hetzner_cloud_server_instance import HetznerCloudServerInstance

# Konstanten
MAX_RETRIES = 5
RETRY_DELAY = 10  # Sekunden


class OllamaManager:
    def __init__(self, config: Configuration, ssh_manager: SSHManager):
        self.config = config
        self.ssh_manager = ssh_manager

    def install_ollama(self, server_model: HetznerCloudServerInstance):
        commands = [
            "apt update",
            "apt upgrade -y",
            "apt install -y cpulimit",
            "apt install -y nohup",
            "apt autoremove",
            "apt autoclean -y",
        ]
        self.ssh_manager.execute_commands(commands)

        commands = [
            "curl -fsSL https://ollama.com/install.sh | sh",
        ]
        self.ssh_manager.execute_commands(commands)

        commands = [
            'mkdir -p /etc/systemd/system/ollama.service.d',
            'echo -e \'[Service]\\nEnvironment="OLLAMA_HOST=0.0.0.0:11434"\\nCPUQuota=' + str(
                server_model.get_cpu_max_limit()) + '%\' | sudo tee /etc/systemd/system/ollama.service.d/override.conf'
        ]
        self.ssh_manager.execute_commands(commands)

    # def start_ollama(self):
    # commands = [
    #     "source /etc/environment",
    #     "printenv"
    #     "ollama serve"
    # ]
    #
    # self.ssh_manager.execute_commands(commands)
