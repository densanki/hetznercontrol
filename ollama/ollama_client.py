import json
import re

import requests
import time

from helper.configuration import Configuration
from logging_config import logger

# Consts
OLLAMA_PORT = 11434
OLLAMA_API_TAGS_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/tags"
OLLAMA_API_PULL_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/pull"
OLLAMA_API_CHAT_ENDPOINT = f"http://{{}}:{OLLAMA_PORT}/api/generate"
MAX_RETRIES = 5
RETRY_DELAY = 10  # Sekunden


class OllamaClient:
    def __init__(self, config: Configuration, hostname):
        self.config = config
        self.hostname = hostname

    def is_ollama_ready(self):
        url = OLLAMA_API_TAGS_ENDPOINT.format(self.hostname)
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    logger.debug("Ollama is ready.")
                    return True
            except requests.ConnectionError as e:
                logger.error(f"Failed ollama connection: {e}")
                # logger.exception(e)
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
        url = OLLAMA_API_PULL_ENDPOINT.format(self.hostname)
        payload = {"model": model_name}
        try:
            # Stream the response
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()  # Raises an HTTPError for bad responses

                # Process each line in the response
                for line in response.iter_lines():
                    if line:
                        # Decode the line and parse it as JSON
                        json_data = json.loads(line.decode("utf-8"))
                        logger.debug(json_data)

            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failure on downloading model: {e}")
            return False

    def sanitize_message(self, message: str) -> str:
        """
        Remove or replace unsupported Unicode characters from the message.
        """
        # Replace emojis and other non-ASCII characters with a placeholder
        return re.sub(r"[^\x00-\x7F]", "", message)  # Remove all non-ASCII characters

    def send_chat_message(self, model_name, message):
        """
        Sends a chat message to the specified model and retrieves the response.

        Args:
            model_name (str): The name of the model to interact with.
            message (str): The user's message to send to the model.

        Returns:
            str: The model's response to the user's message.
        """
        url = OLLAMA_API_CHAT_ENDPOINT.format(self.hostname)
        payload = {
            "model": model_name,
            "prompt": message,
            "stream": False
        }
        logger.debug(f"Model {model_name} request: \n{message}")
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            data_response = self.sanitize_message(data.get("response", ""))
            logger.debug(f"Model's response: \n{data_response}")
            return data_response
        except requests.exceptions.RequestException as e:
            logger.error(f"Failure on request chat: {e}")
            return ""
