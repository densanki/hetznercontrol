from logging_config import logger
import time

import requests

from configuration import Configuration

# Konstanten
OLLAMA_PORT = 11434
OLLAMA_API_TAGS_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/tags"
OLLAMA_API_PULL_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/pull"
OLLAMA_API_CHAT_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/generate"
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
            'mkdir -p /etc/systemd/system/ollama.service.d',
            'echo -e \'[Service]\\nEnvironment="OLLAMA_HOST=0.0.0.0:11434"\' | sudo tee /etc/systemd/system/ollama.service.d/override.conf'
        ]
        self.ssh_manager.execute_commands(commands)

    #def start_ollama(self):
        # commands = [
        #     "source /etc/environment",
        #     "printenv"
        #     "ollama serve"
        # ]
        #
        # self.ssh_manager.execute_commands(commands)

    def is_ollama_ready(self):
        url = OLLAMA_API_TAGS_ENDPOINT.format(self.ssh_manager.get_hostname())
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

    def download_model(self, model_name: str):
        """
        Downloads the specified model using the Ollama API.

        Args:
            :param self:
            :param model_name: The name of the model to download.

            model_name

        Returns:
            dict: The JSON response from the API indicating the status of the download.

        """
        url = OLLAMA_API_PULL_ENDPOINT.format(self.ssh_manager.get_hostname())
        payload = {"model": model_name}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            print(response.text)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failure on downloading model: {e}")
            return None

    def send_chat_message(self, model_name, message):
        """
        Sends a chat message to the specified model and retrieves the response.

        Args:
            model_name (str): The name of the model to interact with.
            message (str): The user's message to send to the model.

        Returns:
            str: The model's response to the user's message.
        """
        url = OLLAMA_API_CHAT_ENDPOINT.format(self.ssh_manager.get_hostname())
        payload = {
            "model": model_name,
            "prompt": message,
            "stream": False  # Set to True if you prefer streaming responses
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(response.text)
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failure on request chat: {e}")
            return ""
