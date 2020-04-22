import pytest

from nile_test.toxiproxy import ToxiProxy, Proxy

HOSTNAME = "localhost:8474"
TOXIPROXY = ToxiProxy(HOSTNAME)

TOXIPROXY_UNAVAILABLE = not TOXIPROXY.exists()
TOXIPROXY_REASON = f"Could not find ToxiProxy server at '{HOSTNAME}'"


def cleanup_proxy(name):
    proxy = Proxy(TOXIPROXY, name=name)

    if proxy.exists():
        proxy.delete()
        assert not proxy.exists(), \
            f"A Proxy named '{name}' should not exist on server after delete"


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_basic_info():
    assert f"http://{HOSTNAME}" == TOXIPROXY.get_url()


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_proxy_creation():
    cleanup_proxy("proxy1")
    proxy1 = Proxy(TOXIPROXY, name="proxy1")

    proxy1_upstream = "localhost:8000"
    proxy1_listen = "127.0.0.1:8001"

    proxy1.make(
        upstream_address=proxy1_upstream,
        listen_address=proxy1_listen)

    assert proxy1.exists(), \
        "A Proxy named 'proxy1' should exist on server after creation"

    retrieved_upstream = proxy1.get_upstream()

    assert proxy1_upstream == retrieved_upstream, \
        f"Found upstream '{retrieved_upstream}', expected '{proxy1_upstream}'"

    retrieved_listen = proxy1.get_listen()

    assert retrieved_listen == proxy1_listen, \
        f"Found listen '{retrieved_listen}', expected '{proxy1_listen}'"


@pytest.mark.skipif(TOXIPROXY_UNAVAILABLE, reason=TOXIPROXY_REASON)
def test_proxy_update():
    cleanup_proxy("proxy1")
    proxy1 = Proxy(TOXIPROXY, name="proxy1")

    proxy1_upstream = "localhost:8000"
    proxy1_listen = "127.0.0.1:8001"

    proxy1.make(
        upstream_address=proxy1_upstream,
        listen_address=proxy1_listen)

    new_upstream = "localhost:8003"
    proxy1.set_upstream(new_upstream)

    retrieved_upstream = proxy1.get_upstream()
    assert new_upstream == retrieved_upstream, \
        f"Found upstream '{retrieved_upstream}', expected '{new_upstream}'"

    new_listen = "127.0.0.1:8003"
    proxy1.set_listen(new_listen)

    retrieved_listen = proxy1.get_listen()
    assert retrieved_listen == new_listen, \
        f"Found listen '{retrieved_listen}', expected '{new_listen}'"
