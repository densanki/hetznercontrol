from logging_config import logger

from configuration import Configuration
from email_notifier import EmailNotifier
from hetzner_cloud_manager import HetznerCloudManager
from ollama_manager import OllamaManager
from server_provisioner import ServerProvisioner
from ssh_manager import SSHManager

if __name__ == "__main__":
    logger.debug("### Starting")

    configuration = Configuration()
    hcloud_manager = HetznerCloudManager(configuration)
    notifier = EmailNotifier(configuration)
    ssh_manager = SSHManager(configuration)
    ollama_manager = OllamaManager(configuration, ssh_manager)

    provisioner = ServerProvisioner(
        configuration,
        hcloud_manager,
        notifier,
        ssh_manager,
        ollama_manager
    )
    provisioner.provision_server()

    logger.debug("### Stopping")
    logger.debug("")
    logger.debug("-------------------------------------------------------------")
