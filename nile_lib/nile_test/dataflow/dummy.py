from interface import implements
from . import Sink


class AlwaysAccepts(implements(Sink)):
    """
    A simple Sink that always accepts
    """
    def write(self, records):
        return []


class AlwaysRejects(implements(Sink)):
    """
    A simple Sink that always rejects
    """
    def write(self, records):
        return []
