import json

from hcloud.servers import BoundServer


class HetznerCloudServerInstance:
    def __init__(self, server: BoundServer):
        self.server = server

    def get_ipv4(self):
        return self.server.public_net.ipv4.ip

    def get_server_name(self):
        return self.server.name

    def get_cpu_max_limit(self):
        """
        Calculate the maximum CPU limit for each server entry.
        The limit is 80% of the total vCPUs.
        """
        return int(self.server.server_type.cores * 100 * 0.80)

    def __str__(self):
        # Create a dictionary with only the required fields
        server_data = {
            "id": self.server.id,
            "name": self.server.name,
            "status": self.server.status,
            "cpu": self.server.server_type.cores,
            "ram": str(self.server.server_type.memory * 1024) + ' GB',
            "disk": str(self.server.server_type.disk) + ' GB',
            "maxcpulimit": self.get_cpu_max_limit(),
            "ipv4": self.server.public_net.ipv4.ip,
            "ipv6": self.server.public_net.ipv6.ip
        }
        # Convert the dictionary to a nicely formatted JSON string
        return '\n' + json.dumps(server_data, indent=4)