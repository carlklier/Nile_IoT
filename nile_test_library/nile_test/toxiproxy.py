import requests
import json


class ToxiProxy:
    def __init__(self, hostname):
        self.hostname = hostname

    def get_url(self):
        url = "http://{}".format(self.hostname)
        return url

    def exists(self):
        """
        Checks whether the specified ToxiProxy server exists and is reachable
        """
        url = self.get_url() + "/proxies"
        return requests.get(url).ok

    def create_proxy(self, name, upstream_address, listen_address):
        proxy = Proxy(self, name)
        if proxy.exists():
            proxy.set_upstream(upstream_address)
            proxy.set_listen(listen_address)
        else:
            proxy.make(upstream_address, listen_address)

        return proxy

    def get_proxy(self, name):
        proxy = Proxy(self, name)

        if proxy.exists():
            return proxy
        else:
            return None


class Proxy:
    def __init__(self, toxiproxy, name):
        self.toxiproxy = toxiproxy
        self.name = name

    def get_url(self):
        url = "{}/proxies/{}".format(self.toxiproxy.get_url(), self.name)
        return url

    def exists(self):
        return requests.get(self.get_url()).ok

    def make(self, upstream_address, listen_address):
        if self.exists():
            raise RuntimeError("Proxy already exists")

        json = {
            "name": self.name,
            "listen": listen_address,
            "upstream": upstream_address,
            "enabled": True
        }
        print(self.toxiproxy.get_url() + '/proxies')
        requests.post(self.toxiproxy.get_url() + '/proxies', json=json)

    def set_upstream(self, upstream_address):
        # TODO: Use the api to set the upstream
        json = {
          "upstream": upstream_address
        }
        url = self.get_url()
        response = requests.post(url, json=json)

    def get_upstream(self):
        # TODO: Use the api to get the upstream address
        url = self.get_url()
        response = requests.get(url).text
        up = json.loads(response).get("upstream")
        return up

    def set_listen(self, listen_address):
        json = {
            "listen": listen_address
        }
        url = self.get_url()
        response = requests.post(url, json=json)

    def get_listen(self):
        url = self.get_url()
        response = requests.get(url).text
        listen = json.loads(response).get("listen")
        return listen

    def create_toxic(self, name, t_type, stream, toxicity, attributes):
        toxic = Toxic(self, name)

        if toxic.exists():
            toxic.set_type(t_type)
            toxic.set_stream(stream)
            toxic.set_toxicity(toxicity)
            toxic.set_attributes(attributes)
        else:
            toxic.make(t_type, stream, toxicity, attributes)

        return toxic

    def get_toxic(self, name):
        toxic = Toxic(self, name)

        if toxic.exists():
            return toxic
        else:
            return None


class Toxic:
    def __init__(self, proxy, name):
        self.proxy = proxy
        self.name = name

    def get_url(self):
        url = "{}/toxics/{}".format(self.proxy.get_url(), self.name)
        return url

    def exists(self):
        return requests.get(self.get_url()).ok

    def make(self, t_type, stream, toxicity, attributes):
        if self.exists():
            raise RuntimeError("Proxy already exists")

        json = {"name": self.name,
                "type": t_type,
                "stream": stream,
                "toxicity": toxicity,
                "attributes": attributes}

        url = "{}/toxics".format(self.proxy.get_url())
        requests.post(url, json=json)

    def set_stream(self, stream):
        json = {
            "stream": stream
        }
        url = self.get_url()
        print(url)
        response = requests.post(url, json=json).text
        return response

    def get_stream(self):
        url = self.get_url()
        response = requests.get(url).text
        stream = json.loads(response).get("stream")
        return stream

    # TODO: Create Getters that retrieve info using the API
    # TODO: Create Setters that update the info using the API


toxiproxy = ToxiProxy("localhost:8474")
print(toxiproxy.exists())

proxy = toxiproxy.create_proxy("proxy1", "localhost:8000", "localhost:8001")
# proxy.set_upstream("localhost:8003")
print(proxy.get_upstream())


attributes = {
    "latency": 2000,
    "jitter": 0
}

toxic = proxy.create_toxic("toxic1", "latency", "downstream", 1, attributes)

print(toxic.get_stream())
print(toxic.set_stream("upstream"))
print(toxic.get_stream())
