from logging_config import logger
import time

from model.server import Server

# Konstanten
RETRY_DELAY = 5  # Sekunden
RESTART_DELAY = 10 # Sekunden

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

    def manage_server(self, serverModel: Server):

        try:
            self.ssh_manager.set_hostname(serverModel.ipv4)
            if not self.ssh_manager.connect():
                logger.error(f"Server Provisioning Failed. SSH connection to server '{serverModel.name}' failed.")
                self.notifier.send_email(
                    subject="Server Provisioning Failed",
                    message=f"SSH connection to server '{serverModel.name}' failed."
                )
                return

            self.ollama_manager.install_ollama()

        finally:
            self.ssh_manager.close()

    def manage_ollama(self, serverModel: Server):
        try:
            if not self.ssh_manager.connect():
                logger.error(f"Server Provisioning Failed. SSH connection to server '{serverModel.name}' failed.")
                self.notifier.send_email(
                    subject="Server Provisioning Failed",
                    message=f"SSH connection to server '{serverModel.name}' failed."
                )
                return

            self.ollama_manager.start_ollama()

            if not self.ollama_manager.is_ollama_ready():
                logger.error(f"Ollama Installation Failed. Ollama on server '{serverModel.name}' is not responding.")
                self.notifier.send_email(
                    subject="Ollama Installation Failed",
                    message=f"Ollama on server '{serverModel.name}' is not responding."
                )
                return
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

        # try:
        #     server = self.hcloud_manager.get_server(60511861)
        # except Exception as ex:
        #     logger.error(f"Get server state failed: {ex}")
        #
        # logger.debug("Server Id: " + str(server.id))
        # logger.debug("Server Name: " + str(server.name))
        # logger.debug("Server Status: " + str(server.status))
        # logger.debug("Server IPv4: " + str(server.public_net.ipv4.ip))
        # logger.debug("Server IPv6: " + str(server.public_net.ipv6.ip))
        #
        # serverModel = Server(server.id, server.name, server.status, server.public_net.ipv4.ip,
        #                      server.public_net.ipv6.ip)
        #
        # self.manage_server(serverModel)
        #
        # self.hcloud_manager.reboot_server(server)
        # time.sleep(RESTART_DELAY)
        #
        # if self.check_server_status(server):
        #     self.manage_ollama(serverModel)
        #
        # return

        server = self.create_server()

        if server:
            if self.check_server_status(server):
                try:
                    server = self.hcloud_manager.get_server(server.id)
                except Exception as ex:
                    logger.error(f"Get server state failed: {ex}")

                serverModel = Server(server.id, server.name, server.status, server.public_net.ipv4.ip,
                                     server.public_net.ipv6.ip)

                self.manage_server(serverModel)

                self.hcloud_manager.reboot_server(server)
                time.sleep(RESTART_DELAY)

                if self.check_server_status(server):
                    self.manage_ollama(serverModel)

        # if not self.hcloud_manager.delete_server(server):
        #    self.notifier.send_email(
        #        subject="Server Deletion Failed",
        #        message=f"Failed to delete server '{server.name}' after multiple attempts."
        #    )