import requests
from .Proxy import Proxy
from .Toxic import Toxic


class ToxiproxyTool:

    ip = None
    port = None
    proxy = None

    def __init__(self):
        self.proxy = None

    def create_Proxy(self, name, uip, uport, lip, lport):

        self.proxy = Proxy(name, uip, uport, lip, lport)
        json = {
            "name": self.proxy.name,
            "listen": self.proxy.listen + ':' + self.proxy.listen_port,
            "upstream": self.proxy.upstream + ':' + self.proxy.up_port,
            "enabled": self.proxy.enabled
        }
        requests.post("http://localhost:8474/proxies", json=json)
        return self.proxy
