from logging_config import logger
import paramiko

from configuration import Configuration

# Konstanten
MAX_RETRIES = 3
RETRY_DELAY = 5


class SSHManager:
    def __init__(self, config: Configuration):
        self.config = config

        self.hostname = ''
        self.username = self.config.get('hetzner', 'ssh_username')
        self.key_path = self.config.get('hetzner', 'private_key_path')
        self.passphrase = self.config.get('hetzner', 'private_key_passphrase')

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def set_hostname(self, hostname):
        self.hostname = hostname

    def get_hostname(self):
        return self.hostname

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
            logger.error("Authentication failed:")
            logger.exception(auth_err)
        except paramiko.SSHException as ssh_err:
            logger.error("SSH error:")
            logger.exception(ssh_err)
        except Exception as e:
            logger.error("Unexpected error:")
            logger.exception(e)
        return False

    def execute_commands(self, commands, environment = None, pty = False):
        for command in commands:
            try:
                stdin, stdout, stderr = self.client.exec_command(command, environment=environment, get_pty=pty)
                stdout.channel.recv_exit_status()

                logger.info(f"# Executed:\n{command}")
                output = stdout.read().decode()
                logger.info(f"# Output:\n{output}")
            except Exception as e:
                logger.error(f"Failed to execute command '{command}': {e}")

    def close(self):
        self.client.close()
        logger.info(f"SSH connection to {self.hostname} closed.")
