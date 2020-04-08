import requests
import json


class ToxiProxy:
    def __init__(self, hostname):
        self.hostname = hostname

    def get_url(self):
        url = f"http://{self.hostname}"
        return url

    def exists(self):
        """
        Checks whether the specified ToxiProxy server exists and is reachable
        """
        url = f"{self.get_url()}/proxies"
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
        url = f"{self.toxiproxy.get_url()}/proxies/{self.name}"
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
        requests.post(self.toxiproxy.get_url() + '/proxies', json=json)

    def delete(self):
        url = self.get_url()
        response = requests.delete(url)
        return response

    def set_upstream(self, upstream_address):
        # TODO: Use the api to set the upstream
        json = {
          "upstream": upstream_address
        }
        url = self.get_url()
        requests.post(url, json=json)

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
        requests.post(url, json=json)

    def get_listen(self):
        url = self.get_url()
        response = requests.get(url).text
        listen = json.loads(response).get("listen")
        return listen

    def create_toxic(self, name, t_type, stream, toxicity, attributes):
        toxic = Toxic(self, name)

        if toxic.exists():
            toxic.delete()

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
        response = requests.post(url, json=json).text
        return response

    def delete(self):
        # DELETE /proxies/{proxy}/toxics/{toxic}
        url = self.get_url()
        response = requests.delete(url)
        return response

    def get_stream(self):
        url = self.get_url()
        response = requests.get(url).text
        stream = json.loads(response).get("stream")
        return stream

    def set_toxicity(self, toxicity):
        json = {
            "toxicity": toxicity
        }
        url = self.get_url()
        response = requests.post(url, json=json).text
        return response

    def get_toxicity(self):
        url = self.get_url()
        response = requests.get(url).text
        toxicity = json.loads(response).get("toxicity")
        return toxicity

    def set_attributes(self, attributes):
        json = {
            "attributes": attributes
        }
        url = self.get_url()
        response = requests.post(url, json=json).text
        return response

    def get_attributes(self):
        url = self.get_url()
        response = requests.get(url).text
        attributes = json.loads(response).get("attributes")
        return attributes
