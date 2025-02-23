from logging_config import logger
import time

import requests

from configuration import Configuration

# Konstanten
OLLAMA_PORT = 11434
OLLAMA_API_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/tags"
MAX_RETRIES = 5
RETRY_DELAY = 10  # Sekunden

class OllamaManager:
    def __init__(self, config: Configuration, ssh_manager):
        self.config = config
        self.ssh_manager = ssh_manager

    def install_ollama(self):
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
            "sed -i ""\$aOLLAMA_HOST=0.0.0.0:11434"" /etc/environment"
        ]
        self.ssh_manager.execute_commands(commands)

    def start_ollama(self):
        commands = [
            "source /etc/environment"
            "printenv",
            "nohup ollama serve"
        ]
        self.ssh_manager.execute_commands(commands)

    def is_ollama_ready(self):
        url = OLLAMA_API_ENDPOINT.format(self.ssh_manager.get_hostname())
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    logger.debug("Ollama is ready.")
                    return True
            except requests.ConnectionError as e:
                logger.error(f"Failed ollama connection: {e}")
                #logger.exception(e)
            time.sleep(RETRY_DELAY)
        return False