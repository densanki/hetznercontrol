from logging_config import logger
import time

# Konstanten
RETRY_DELAY = 5  # Sekunden

class ServerProvisioner:
    def __init__(self, config, hcloud_manager, notifier, ssh_manager, ollama_manager):
        self.config = config
        self.hcloud_manager = hcloud_manager
        self.notifier = notifier
        self.ssh_manager = ssh_manager
        self.ollama_manager = ollama_manager

    def check_server_status(self, server):
        server_run: bool = False
        # Wait for server to be running
        try:
            while server.status != 'running':
                logger.debug(f"Waiting for server to start... Current status: {server.status}")
                time.sleep(RETRY_DELAY)
                server = self.hcloud_manager.get_server(server.id)

            logger.debug(f"Server '{server.name}' is running.")
            server_run = True
        except Exception as exception:
            logger.error(f"Server status check failed: {exception}")
        return server_run

    def manage_server(self, server):
        try:
            if not self.ssh_manager.connect():
                self.notifier.send_email(
                    subject="Server Provisioning Failed",
                    message=f"SSH connection to server '{server.name}' failed."
                )
                return

            self.ssh_manager.set_host(server.public_net.ipv4.ip)
            self.ollama_manager.install_ollama()

            if not self.ollama_manager.is_ollama_ready():
                self.notifier.send_email(
                    subject="Ollama Installation Failed",
                    message=f"Ollama on server '{server.name}' is not responding."
                )
                return

            # Perform tasks with Ollama here

        finally:
            self.ssh_manager.close()

    def create_server(self):
        hetzner_ssh_key_name = self.config.get('hetzner','ssh_key_name')
        server_name = "ollama-server"
        server_type = "cax21"  # Beispiel für einen ARM-Servertyp
        image_name = "ubuntu-22.04"
        server_location = "nbg1"

        return self.hcloud_manager.create_server(server_name, server_type, image_name, server_location, hetzner_ssh_key_name)

    def provision_server(self):

        server = self.create_server()

        if server:
            server_status = self.check_server_status(server)

            if server_status:
                try:
                    server = self.hcloud_manager.get_server(server.id)
                except Exception as ex:
                    logger.error(f"Get server state failed: {ex}")

                self.manage_server(server)

        if not self.hcloud_manager.delete_server(server):
            self.notifier.send_email(
                subject="Server Deletion Failed",
                message=f"Failed to delete server '{server.name}' after multiple attempts."
            )