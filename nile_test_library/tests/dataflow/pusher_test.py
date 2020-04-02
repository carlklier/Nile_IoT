from nile_test.dataflow import _reset
from nile_test.dataflow.buffers import Buffer
from nile_test.dataflow.pushers import DeterministicPusher


def test_DPusher_init():
    in_buf = Buffer()
    out_buf = Buffer()
    dpusher = DeterministicPusher(in_buf, out_buf, 1, 0.1, 1)

    assert dpusher.source is in_buf
    assert dpusher.sink is out_buf
    assert dpusher.quantity == 1
    assert dpusher.retry_delay == 0.1
    assert dpusher.cycle_delay == 1


def test_DPusher_run():
    print("Running test_run")
    in_buf = Buffer()
    out_buf = Buffer()

    in_buf.write(["test1"])
    in_buf.write(["test2"])
    assert len(in_buf.data) == 2

    dpusher = DeterministicPusher(in_buf, out_buf, 1, 0, 0.01)
    dpusher.start()

    import time
    time.sleep(0.1)
    _reset()

    assert len(in_buf.data) == 0
