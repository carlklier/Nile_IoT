import requests

class ToxiProxy:
    def __init__(self, hostname):
        self.hostname = hostname

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

    def exists(self):
        # TODO: Verify using api that a proxy with this name exists
        url = "http://" + self.toxiproxy.hostname + "/proxies/" + self.name
        response = requests.get(url)
        if not response.ok:
            return False
        return True

    def make(self, upstream_address, listen_address):
        if self.exists():
            raise RuntimeError("Proxy already exists")
        # Use the api to create a Proxy with these parameters
        json = {
            "name": self.name,
            "listen": listen_address,
            "upstream": upstream_address,
            "enabled": True
        }
        url = "http://" + self.toxiproxy.hostname + "/proxies"
        print(url)
        requests.post(url, json=json)

    def set_upstream(self, upstream_address):
        # TODO: Use the api to set the upstream
        json = {
            "upstream": upstream_address
        }
        url = "http://" + self.toxiproxy.hostname + "/proxies/" + self.name
        response = requests.post(url, json)
        print(response)
        print(1)

    def get_upstream(self):
        # TODO: Use the api to get the upstream address
        return

    def set_listen(self, listen_address):
        # TODO: Use the api to set the listener
        pass

    def get_listen(self):
        # TODO: Use the api to get the listen address
        return

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
    
    def exists(self):
        # TODO: Verify using api that a toxic with this name exists on the proxy
        url = "http://" + self.proxy.toxiproxy.hostname + "/proxies/" + self.proxy.name + "/toxics/" + self.name
        print(url)
        response = requests.get(url)
        if not response.ok:
            return False
        return True

    def make(self, t_type, stream, toxicity, attributes):
        if self.exists():
            raise RuntimeError("Proxy already exists")
        # TODO Use the api to create a Toxic with these parameters
        json = {"name": self.name,
                "type": t_type,
                "stream": stream,
                "toxicity": toxicity,
                "attributes": attributes
                }
        url = "http://" + self.proxy.toxiproxy.hostname + "/proxies/" + self.proxy.name + "/toxics"
        print(url)
        requests.post(url, json=json)


    # TODO: Create Getters that retrieve info using the API
    # TODO: Create Setters that update the info using the API


toxiproxy = ToxiProxy("localhost:8474")
print("Proxy exists")
proxy = toxiproxy.create_proxy("proxy1", "localhost:8000", "localhost:8001")
proxy.set_upstream("localhost:8003")

attributes = {
    "latency": 2000,
    "jitter": 0
}

#toxic = proxy.create_toxic("toxic1", "latency", "downstream", 1, attributes)
