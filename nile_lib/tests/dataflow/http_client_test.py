import pytest
import threading
from locust import events
from nile_test.dataflow.http_client import HTTPClient
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import time


@pytest.fixture()
def echo_server():
    server = HTTPServer(('localhost', 8000), EchoRequestHandler)
    server_thread = threading.Thread(target=run_server, args=(server,))
    server_thread.start()
    yield server
    server.shutdown()
    server.server_close()
    server_thread.join()


def run_server(server):
    server.serve_forever()


class EchoRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"{time.ctime()}: GET Received")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(self.path, "utf-8"))

    def do_POST(self):
        print(f"{time.ctime()}: POST Received")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())

    def do_DELETE(self):
        print(f"{time.ctime()}: DELETE Received")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(self.path, "utf-8"))


def test_init():
    sink = HTTPClient(method="post", url="http://localhost:8000")
    assert sink.defaults == {"method": "post", "url": "http://localhost:8000"}


def test_write(echo_server):
    sink = HTTPClient(url="http://localhost:8000")

    delete_found = False
    post_found = False
    get_found = False

    def catch_delete(request_type, **kwargs):
        print(f"D {request_type}")
        nonlocal delete_found
        if request_type == "DELETE":
            delete_found = True

    def catch_post(request_type, **kwargs):
        print(f"P {request_type}")
        nonlocal post_found
        if request_type == "POST":
            post_found = True

    def catch_get(request_type, **kwargs):
        print(f"G {request_type}")
        nonlocal get_found
        if request_type == "GET":
            get_found = True

    events.request_success += catch_delete
    events.request_success += catch_post
    events.request_success += catch_get

    assert not delete_found and not post_found and not get_found

    sink.write([{"method": "DELETE"}])
    assert delete_found and not post_found and not get_found

    sink.write([{"method": "POST", "data": "2"}])
    assert delete_found and post_found and not get_found

    sink.write([{"method": "GET"}])
    assert delete_found and post_found and get_found
