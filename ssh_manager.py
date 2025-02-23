from logging_config import logger
import time

import paramiko

from configuration import Configuration

# Konstanten
MAX_RETRIES = 3
RETRY_DELAY = 5

class SSHManager:
    def __init__(self, config: Configuration):
        self.hostname = ''
        self.username = config.get('hetzner', 'ssh_username')
        self.key_path = config.get('hetzner', 'private_key_path')
        self.passphrase = config.get('hetzner', 'private_key_passphrase')
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            if self.key_path:
                # Load the private key with the provided passphrase
                private_key = paramiko.RSAKey.from_private_key_file(self.key_path, password=self.passphrase)
                self.client.connect(
                    self.hostname,
                    username=self.username,
                    pkey=private_key
                )
            else:
                # Attempt password-based authentication if no key path is provided
                self.client.connect(
                    self.hostname,
                    username=self.username,
                    password=self.passphrase  # Using passphrase as password
                )
            logger.info(f"SSH connection to {self.hostname} established.")
            return True
        except paramiko.AuthenticationException as auth_err:
            logger.error(f"Authentication failed: {auth_err}")
        except paramiko.SSHException as ssh_err:
            logger.error(f"SSH error: {ssh_err}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return False

    def execute_commands(self, commands):
        for command in commands:
            try:
                stdin, stdout, stderr = self.client.exec_command(command)
                stdout.channel.recv_exit_status()
                logger.info(f"Executed: {command}")
            except Exception as e:
                logger.error(f"Failed to execute command '{command}': {e}")

    def close(self):
        self.client.close()
        logger.info(f"SSH connection to {self.hostname} closed.")