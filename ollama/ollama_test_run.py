from helper.email_notifier import EmailNotifier
from logging_config import logger

from helper.configuration import Configuration
from ollama.ollama_client import OllamaClient


class OllamaTestRun:
    def __init__(self, config: Configuration, ollama_client: OllamaClient, notifier: EmailNotifier):
        self.config = config
        self.ollama_client = ollama_client
        self.notifier = notifier

    def run_test(self):
        if not self.ollama_client.is_ollama_ready():
            logger.error(f"Ollama Installation Failed. Ollama on server is not responding.")
            self.notifier.send_email(
                subject="Ollama Installation Failed",
                message=f"Ollama on server is not responding."
            )
            return

        # Load Model
        model_name = "deepseek-r1:1.5b"
        result = self.ollama_client.download_model(model_name)
        if result:
            logger.debug(f"Model '{model_name}' download initiated successfully.")
        else:
            logger.error(f"Failed to initiate download for model '{model_name}'.")

        # Start Chat
        user_message = "Hello, how are you?"
        reply = self.ollama_client.send_chat_message(model_name, user_message)

        user_message = "Please tell me a story about LLM fight humans in 300 words."
        reply = self.ollama_client.send_chat_message(model_name, user_message)

        user_message = "Thanks for the test. Bye Bye"
        reply = self.ollama_client.send_chat_message(model_name, user_message)
