"""
This file is here so that locust is imported as soon as possible

This aims to prevent issues related to monkey patching
when monkey patching occurds after ssl has been imported
issues can occur see:

https://github.com/gevent/gevent/issues/1016
"""


def pytest_configure():
    import locust  # noqa: F401
