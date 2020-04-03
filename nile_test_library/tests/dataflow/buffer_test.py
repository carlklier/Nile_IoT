import pytest

from nile_test.dataflow.buffers import Buffer


def test_init_illegal_arg():
    with pytest.raises(ValueError):
        Buffer(yield_next='OLD')


def test_init_valid_args():
    buf = Buffer()
    assert buf.yield_next == "oldest"
    assert buf.drop_next == "oldest"
    assert len(buf.data) == 0


def test_FIFO_read():
    buf = Buffer()
    buf.data.extend(["1", "2", "3"])
    assert len(buf.data) == 3

    assert list(buf.read()) == ["1"]
    assert list(buf.read()) == ["2"]
    assert list(buf.read()) == ["3"]
    assert len(buf.data) == 0


def test_FIFO_read_multiple():
    buf = Buffer()
    buf.data.extend(["1", "2", "3"])
    assert len(buf.data) == 3

    assert list(buf.read(3)) == ["1", "2", "3"]
    assert len(buf.data) == 0


def test_LIFO_read():
    buf = Buffer(yield_next="newest")
    buf.data.extend(["1", "2", "3"])
    assert len(buf.data) == 3

    assert list(buf.read()) == ["3"]
    assert list(buf.read()) == ["2"]
    assert list(buf.read()) == ["1"]
    assert len(buf.data) == 0


def test_LIFO_read_multiple():
    buf = Buffer(yield_next="newest")
    buf.data.extend(["1", "2", "3"])
    assert len(buf.data) == 3

    assert list(buf.read(3)) == ["3", "2", "1"]
    assert len(buf.data) == 0


def test_read_empty():
    buf = Buffer()
    assert list(buf.read()) == []
    assert len(buf.data) == 0


def test_write_overflow_drop_oldest():
    buf = Buffer(drop_next="oldest", capacity=3)
    buf.write(["test1", "test2", "test3"])
    assert list(buf.data) == ["test1", "test2", "test3"]
    assert len(buf.data) == 3

    buf.write(["test4"])
    assert list(buf.data) == ["test2", "test3", "test4"]


def test_write_overflow_drop_newest():
    buf = Buffer(drop_next="newest", capacity=3)
    buf.write(["test1", "test2", "test3"])
    assert list(buf.data) == ["test1", "test2", "test3"]
    assert len(buf.data) == 3

    buf.write(["test4"])
    assert list(buf.data) == ["test1", "test2", "test4"]
