from logging_config import logger

from helper.configuration import Configuration
from helper.email_notifier import EmailNotifier
from helper.hetzner_cloud_manager import HetznerCloudManager
from ollama.ollama_manager import OllamaManager
from server_provisioner import ServerProvisioner
from helper.ssh_manager import SSHManager
import sys

if __name__ == "__main__":
    logger.debug("### Starting")

    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

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
    provisioner.process_server()

    logger.debug("### Stopping")
    logger.debug("")
    logger.debug("-------------------------------------------------------------")
