from collections import deque

OLDEST = 'oldest'
NEWEST = 'newest'

_options = (OLDEST, NEWEST)

class Buffer:
    def __init__(self, yield_next=OLDEST, drop_next=OLDEST, capacity=None):
        if yield_next not in _options or drop_next not in _options:
            raise ValueError(f"yield_next and drop_next must be either '{OLDEST}' or '{NEWEST}'")

        self.yield_next = yield_next
        self.drop_next = drop_next
        self.capacity = capacity

        self.data = deque()

    def _push(self, record):
        """The newest data is appended to the right of the buffer"""
        self.data.append(record)

    def _pop_oldest(self):
        """The oldest data is available from the left of the buffer"""
        return self.data.popleft()
    
    def _pop_newest(self):
        """The newest data is available form the right of the buffer"""
        return self.data.pop()

    def read(self):
        if len(self.data) == 0:
            return (False, None)

        if self.yield_next == OLDEST:
            return (True, self._pop_oldest())
        else:
            return (True, self._pop_newest())
    

    def write(self, record):
        if self.capacity:
            self._ensure_capacity()
        
        self._push(record)

    def _ensure_capacity(self):
        while len(self.data) >= self.capacity:
            if self.drop_next == OLDEST:
                self.data.popleft()
            else:
                self.data.pop()

class CircularReadBuffer:
    def __init__(self, buffer_data):
        self.buffer_data = buffer_data
        self.cursor = 0
    
    def read(self):
        if len(self.buffer_data) == 0:
            return (False, None)
        
        result = self.buffer_data[self.cursor]

        self.cursor += 1
        self.cursor %= len(self.buffer_data)

        return (True, result)
    
    def write(self, record):
        raise RuntimeError("It is illegal to write to a read-only buffer")
