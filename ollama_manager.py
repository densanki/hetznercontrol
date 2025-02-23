from logging_config import logger
import time

import requests

from configuration import Configuration

# Konstanten
OLLAMA_PORT = 11434
OLLAMA_API_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/tags"
MAX_RETRIES = 3
RETRY_DELAY = 5  # Sekunden

class OllamaManager:
    def __init__(self, config: Configuration, ssh_manager):
        self.config = config
        self.ssh_manager = ssh_manager

    def install_ollama(self):
        commands = [
            "apt update",
            "apt upgrade",
            "apt autoremove"
            "curl -fsSL https://ollama.com/install.sh | sh",
            "ollama serve"
        ]
        self.ssh_manager.execute_commands(commands)

    def is_ollama_ready(self):
        url = OLLAMA_API_ENDPOINT.format(self.ssh_manager.hostname)
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    logger.debug("Ollama ist bereit.")
                    return True
            except requests.ConnectionError as e:
                logger.debug(f"Ollama-Verbindung fehlgeschlagen: {e}")
            time.sleep(RETRY_DELAY)
        return False