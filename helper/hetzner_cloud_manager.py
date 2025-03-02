from helper.configuration import Configuration
from logging_config import logger

from hcloud import Client
from hcloud.images import Image
from hcloud.server_types import ServerType
import time

# Konstanten
MAX_RETRIES = 3
RETRY_DELAY = 5

class HetznerCloudManager:
    def __init__(self, config: Configuration):
        self.client = Client(token=config.get('hetzner','api_token'))

    def get_ssh_key(self, name):
        return self.client.ssh_keys.get_by_name(name)

    def get_server(self, server_id: str):
        return self.client.servers.get_by_id(server_id)

    def get_search_for_ssh_key(self, hetzner_ssh_key_name: str = None):
        if not hetzner_ssh_key_name:
            logger.error(f"SSH key name was not set")
            return None

        try:
            hetzner_ssh_key = self.get_ssh_key(hetzner_ssh_key_name)
        except Exception as ex:
            logger.error(f"Load hetzner ssh key failed: {ex}")
            return None

        if not hetzner_ssh_key:
            logger.error(f"SSH key '{hetzner_ssh_key_name}' not found.")
            return None
        return hetzner_ssh_key

    def create_server(self, server_name, server_type, image_name, server_location, hetzner_ssh_key_name):
        """
        Create a new server in Hetzner Cloud.

        :param server_name: Desired name for the new server.
        :param server_type: Type of server (e.g., 'cx11').
        :param image_name: Name of the image to use (e.g., 'ubuntu-20.04').
        :param server_location: Name of server location (e.g., 'nbg1').
        :param hetzner_ssh_key_name: SSHKey object to be added to the server.
        :return: Created Server object or None if creation failed.
        """
        try:
            # Check if a server with the same name already exists
            existing_servers = self.client.servers.get_all(name=server_name)
            if existing_servers:
                logger.error(f"Server creation failed: A server with the name '{server_name}' already exists.")
                return None

            ssh_key = self.get_search_for_ssh_key(hetzner_ssh_key_name)
            location = self.client.locations.get_by_name(server_location)

            response = self.client.servers.create(
                name=server_name,
                server_type=ServerType(name=server_type),
                image=Image(name=image_name),
                location=location,
                ssh_keys=[ssh_key],
            )
            # Verify server creation
            if response and response.server:
                server = response.server
                logger.debug(f"Server '{server.name}' with ID {server.id} has been created successfully.")
                return server
            else:
                logger.error("Server creation failed: No server information returned.")
                return None

        except Exception as ex:
            logger.error(f"Server creation failed: {ex}")
            return None

    def reboot_server(self, server):
        for attempt in range(MAX_RETRIES):
            try:
                self.client.servers.reboot(server)
                logger.debug(f"Server '{server.name}' was rebooted.")
                return True
            except Exception as e:
                logger.debug(f"Error on server delete: {e}")
                time.sleep(RETRY_DELAY)
        return False


    def delete_server(self, server):
        for attempt in range(MAX_RETRIES):
            try:
                self.client.servers.delete(server)
                logger.debug(f"Server '{server.name}' was deleted.")
                return True
            except Exception as e:
                logger.debug(f"Error on server delete: {e}")
                time.sleep(RETRY_DELAY)
        return False