from logging_config import logger
import time

from model.hetzner_cloud_server_instance import HetznerCloudServerInstance
from ollama.ollama_client import OllamaClient
from ollama.ollama_test_run import OllamaTestRun

# Konstanten
RETRY_DELAY = 20  # Sekunden
START_DELAY = 20  # Sekunden
RESTART_DELAY = 20  # Sekunden


class ServerProvisioner:
    def __init__(self, config, hcloud_manager, notifier, ssh_manager, ollama_manager):
        self.config = config
        self.hcloud_manager = hcloud_manager
        self.notifier = notifier
        self.ssh_manager = ssh_manager
        self.ollama_manager = ollama_manager

    def check_server_status(self, server):
        # Wait for server to be running
        try:
            while server.status != 'running':
                logger.debug(f"Waiting for server to start... Current status: {server.status}")
                time.sleep(RETRY_DELAY)
                server = self.hcloud_manager.get_server(server.id)

            logger.debug(f"Server '{server.name}' is running.")
            return True
        except Exception as exception:
            logger.error(f"Server status check failed: {exception}")
        return False

    def manage_server(self, server_model: HetznerCloudServerInstance):
        try:
            self.ssh_manager.set_hostname(server_model.get_ipv4())
            if not self.ssh_manager.connect():
                logger.error(
                    f"Server Provisioning Failed. SSH connection to server '{server_model.get_server_name()}' failed.")
                self.notifier.send_email(
                    subject="Server Provisioning Failed",
                    message=f"SSH connection to server '{server_model.get_server_name()}' failed."
                )
                return

            self.ollama_manager.install_ollama(server_model)

        finally:
            self.ssh_manager.close()

    def manage_ollama(self, server_model: HetznerCloudServerInstance):
        ollama_client = OllamaClient(self.config, server_model.get_ipv4())

        ollama_test_run = OllamaTestRun(self.config, ollama_client, self.notifier)
        ollama_test_run.run_test()

    def create_server(self):
        hetzner_ssh_key_name = self.config.get('hetzner', 'ssh_key_name')
        server_name = "ollama-server"
        server_type = "cax21"  # Beispiel für einen ARM-Servertyp
        image_name = "ubuntu-22.04"
        server_location = "nbg1"

        server = self.hcloud_manager.create_server(server_name, server_type, image_name, server_location,
                                                   hetzner_ssh_key_name)

        time.sleep(START_DELAY)

        return server

    def process_server(self):
        server_instance_id = self.config.get('hetzner', 'server_instance_id', fallback=None)

        logger.debug(f"Server instance_id: {server_instance_id}")

        if server_instance_id:
            logger.debug("Use existing server instance.")
            self.use_server(server_instance_id)
        else:
            logger.debug("Provisioning new server instance.")
            self.provision_server()

    def provision_server(self):

        server = self.create_server()

        if server:
            if self.check_server_status(server):
                try:
                    server = self.hcloud_manager.get_server(server.id)
                except Exception as ex:
                    logger.error(f"Get server state failed: {ex}")

                serverModel = HetznerCloudServerInstance(server)
                logger.debug(serverModel)

                self.manage_server(serverModel)

                self.hcloud_manager.reboot_server(server)
                time.sleep(RESTART_DELAY)

                if self.check_server_status(server):
                    self.manage_ollama(serverModel)

        delete = self.config.get('hetzner', 'delete', fallback=True).lower().strip()
        if delete == "true":
            if not self.hcloud_manager.delete_server(server):
                self.notifier.send_email(
                    subject="Server Deletion Failed",
                    message=f"Failed to delete server '{server.name}' after multiple attempts."
                )

    def use_server(self, server_instance_id):
        try:
            server = self.hcloud_manager.get_server(server_instance_id)

            serverModel = HetznerCloudServerInstance(server)

            logger.debug(serverModel)

            if self.check_server_status(server):
                self.manage_ollama(serverModel)
        except Exception as ex:
            logger.error(f"Get use server failed: {ex}")
