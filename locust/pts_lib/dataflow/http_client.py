from requests import request
from collections import ChainMap
from interface import implements
from . import Sink


class HttpClient(implements(Sink)):
    """
    An HTTPClient is a Sink that sends data
    written to it to the specified server
    """

    def __init__(self, **defaults):
        """
        Creates an HTTPClient

        Arguments:
         The keyword arguments provided act as duplicates for the fields
         read from records written to this client.
         For more info see HTTPClient.write()
        """
        self.defaults = defaults

    def write(self, records):
        """
        Sends records to an HTTP server

        Each record that is not a dictionary is ignored.
        Each dictionary record is overlayed onto the defaults
        provided to the client.

        The following fields must be defined in
        either the record or the overlay.
         * method - the HTTP method to use
         * url - the URL to send to

        The following additional fields may also be provided
         * params - a dictionary of query string parameters
         * data - data to be sent in the body of the request
         * headers - a dictionary of HTTP headers
        """
        for record in records:
            self._write_one(record)

    def _write_one(self, record):
        optionals = {
            "params": {},
            "data": {},
            "headers": {}
        }
        record = ChainMap(record, self.defaults, optionals)

        if "method" not in record:
            raise ValueError("Must provide 'method'")

        if "url" not in record:
            raise ValueError("Must provide 'url'")

        request(record["method"], record["url"], params=record["params"],
                data=record["data"], headers=record["headers"])
