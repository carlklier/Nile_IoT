from nile_test.dataflow.buffers import CircularReadBuffer


def test_CRB_init():
    data = ["test1", "test2", "test3"]
    buf = CircularReadBuffer(buffer_data=list(data))
    assert buf.buffer_data == list(data)
    assert buf.cursor == 0


def test_CRB_read():
    buf = CircularReadBuffer(buffer_data=[])
    values1 = list(buf.read())
    assert values1 == []

    buf = CircularReadBuffer(buffer_data=["test1", "test2", "test3"])
    values2 = list(buf.read())
    assert buf.cursor == 1
    assert values2 == ["test1"]

    list(buf.read())
    list(buf.read())
    assert buf.cursor == 0
