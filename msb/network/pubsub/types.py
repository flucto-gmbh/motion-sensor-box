from abc import ABC, abstractmethod


class Publisher(ABC):
    """
    Publisher interface.
    """
    @abstractmethod
    def send(self, topic: str | bytes, data: dict):
        """
        Send data via the implemented output stream.
        """
        pass


class Subscriber(ABC):
    """
    Subscriber interface
    """
    @abstractmethod
    def receive(self) -> tuple(bytes, dict):
        """
        Blocking function to receive data from the implemented input stream.

        Data is returned as a tuple of (topic, data).
        """
        pass
