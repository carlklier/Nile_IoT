import sys
import pytest
import requests

from nile_test import integration
from nile_test.integration import _is_slave, _is_master
from nile_test.integration.databuffer import DataBuffer
from nile_test.integration.testmanager import TestManager


def test_launch_slave(mocker, monkeypatch):
    mock_tm = mocker.patch.object(TestManager, '__init__')
    mock_db = mocker.patch.object(DataBuffer, '__init__')
    mock_tm.return_value = None
    mock_db.return_value = None
    monkeypatch.setattr(sys, "argv", ["--slave"])

    integration.launch("hostname")

    mock_tm.assert_not_called()
    mock_db.assert_called_with("hostname")


def test_launch_master(mocker, monkeypatch):
    mock_tm = mocker.patch.object(TestManager, '__init__')
    mock_db = mocker.patch.object(DataBuffer, '__init__')
    mock_tm.return_value = None
    mock_db.return_value = None
    monkeypatch.setattr(sys, "argv", ["--master"])

    integration.launch("hostname")
    mock_tm.assert_called_with("hostname")
    mock_db.assert_not_called()

def test_is_slave(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["--slave"])
    assert _is_slave()
    assert not _is_master()


def test_is_master(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["--master"])
    assert not _is_slave()
    assert _is_master()

def test_TestManager_init(mocker):
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    tm = TestManager("localhost", slave_count=0)

    assert tm.hostname == "localhost"
    assert tm.slave_count == 1
    assert tm.start_time is not None
    assert tm.config_file == './locustfile.py'
    assert start_test_patch.called()

@patch('nile_test.integration.testmanager.requests.post')
def test_TestManager_start_test(mock_post):
  tm = TestManager("localhost")
  mock_post.return_value.status_code = 200
  assert tm.start_test() == None
  mock_post.return_value.status_code == 400
  with pytest.raises(RuntimeError):
    tm.start_test()

@patch('nile_test.integration.testmanager.requests.post')
def test_TestManager_finalize_test(mock_post):
  tm = TestManager("localhost")
  mock_post.return_value.status_code = 200
  assert tm.finalize_test() == None
  mock_post.return_value.status_code == 400
  with pytest.raises(RuntimeError):
    tm.finalize_test()

def test_DataBuffer_init():
    data_buffer1 = DataBuffer("localhost")
    assert data_buffer1.hostname == "localhost"
    assert data_buffer1.buffer_limit == 20
    assert data_buffer1.data_endpoint == "http://localhost/api/v1/requests"
    assert len(data_buffer1.buffer) == 0
    # not sure how to test the event hooks adding methods

    data_buffer2 = DataBuffer("localhost", buffer_limit=30)
    assert data_buffer2.buffer_limit == 30


def test__on_request_data(mocker):
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    data_buffer = DataBuffer("localhost")

    for i in range(20):
        data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)

    assert len(data_buffer.buffer) == 20
    data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
    assert len(data_buffer.buffer) == 0


def test_on_quitting(mocker):
    mock_post = mocker.patch.object(requests, 'post')
    mock_post.return_value.status_code = 200
    data_buffer = DataBuffer("localhost")
    data_buffer._on_request_data("GET", "/", 0.1, 10, True, None)
    data_buffer.on_quitting()

    assert len(data_buffer.buffer) == 0
