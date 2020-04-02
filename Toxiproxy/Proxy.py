from .Toxic import Toxic
import requests


class Proxy:
    name = None
    listen = None
    listen_port = None
    upstream = None
    up_port = None
    enabled = True
    toxic = None

    def __init__(self, n, l, lp, up, upp):
        self.name = n
        self.listen = l
        self.listen_port = lp
        self.upstream = up
        self.up_port = upp
        self.enabled = True
        self.toxic = None

    def create_toxic(self, name, ty, stream, toxicity):
        self.toxic = Toxic(name, ty, stream, toxicity)
        attributes = {
            self.toxic.type: 2000,
            "jitter": 0
        }

        json = {"name": self.toxic.name,
                "type": self.toxic.type,
                "stream": self.toxic.stream,
                "toxicity": self.toxic.toxicity,
                "attributes": attributes
                }

        requests.post("http://localhost:8474/proxies/testProxy/toxics", json=json)
        return self.toxic

    def set_name(self, n):
        self.name = n

    def set_listen(self, l):
        self.listen = l

    def set_listen_port(self, lp):
        self.listen_port = lp

    def set_upstream(self, up):
        self.upstream = up

    def set_upstream(self, upp):
        self.up_port = upp

    def set_enabled(self, en):
        self.enabled = en
