from nile_test.dataflow import _reset
from nile_test.dataflow.buffers import Buffer
from nile_test.dataflow.pushers import DeterministicPusher, GammaPusher

FUDGE_FACTOR = 2


def test_DPusher_init():
    in_buf = Buffer()
    out_buf = Buffer()
    dpusher = DeterministicPusher(in_buf, out_buf, quantity=1,
                                  retry_delay=0.1, cycle_delay=1)

    assert dpusher.source is in_buf
    assert dpusher.sink is out_buf
    assert dpusher.quantity == 1
    assert dpusher.retry_delay == 0.1
    assert dpusher.cycle_delay == 1


def test_DPusher_run():
    in_buf = Buffer()
    out_buf = Buffer()

    in_buf.write(["test1", "test2"])
    assert len(in_buf.data) == 2

    retry_delay = 0
    cycle_delay = 0.01

    dpusher = DeterministicPusher(in_buf, out_buf, quantity=1,
                                  retry_delay=retry_delay,
                                  cycle_delay=cycle_delay)
    dpusher.start()

    import time
    time.sleep(cycle_delay * 2 * FUDGE_FACTOR)
    _reset()

    assert len(in_buf.data) == 0


def test_GPusher_init():
    in_buf = Buffer()
    out_buf = Buffer()
    gpusher = GammaPusher(in_buf, out_buf, quantity=1,
                          retry_shape=1, cycle_shape=1)

    assert gpusher.source is in_buf
    assert gpusher.sink is out_buf
    assert gpusher.quantity == 1
