from abc import ABC, abstractmethod
from potable.saveable import Saveable


class TimeOutError(Exception):
    pass


class TransportLayer(ABC, Saveable):
    classes = {}

    def __init__(self):
        self.address = None

    @classmethod
    def class_path(cls):
        return 'TransportLayer'

    @classmethod
    def name(cls) -> str:
        return 'TransportLayer'

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send(self, message: bytes):
        pass

    @abstractmethod
    def recv(self) -> bytes:
        pass

    @abstractmethod
    def flush(self):
        pass


