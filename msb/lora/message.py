import pickle
import sys

from abc import ABC, abstractmethod
from enum import Enum, auto

import numpy as np


class Topic(Enum):
    UNDEFINED = auto()
    IMU = auto()
    ATTITUDE = auto()
    ATTITUDE_AND_GPS = auto()


# https://docs.python-guide.org/scenarios/serialization/


class DeserializeError(ValueError):
    """Raised if a message could not be parsed."""

    pass


class Message(ABC):

    topic = Topic.UNDEFINED
    _sender_dtype = np.ushort

    def __init__(self, content, sender: int, topic: Topic = Topic.UNDEFINED):
        self.content = self._check_content(content)
        self.sender = sender
        self.topic = topic

    @classmethod
    @abstractmethod
    def _check_content(cls, content):
        pass

    @abstractmethod
    def _serialize(self):
        pass

    @classmethod
    @abstractmethod
    def _deserialize(cls, bytes_: bytes):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}({self.content}, {self.sender}, {str(self.topic)})"

    def __str__(self):
        return f"{self.topic}, from {self.sender}: {self.content}"

    def serialize(self):
        return (
            bytes([self.topic.value])
            + np.array(self.sender, dtype=self._sender_dtype).tobytes()
            + self._serialize()
        )

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        topic = Topic(bytes_[0])
        n_bytes_sender = np.dtype(cls._sender_dtype).itemsize
        sender = np.frombuffer(bytes_[1 : 1 + n_bytes_sender], dtype=cls._sender_dtype)[
            0
        ]
        try:
            data = cls._deserialize(bytes_[1 + n_bytes_sender :])
        except Exception as e:
            raise DeserializeError() from e
        return cls(data, sender, topic)


class TextMessage(Message):
    def __repr__(self):
        return f'{self.__class__.__name__}("{self.content}", {self.sender}, {str(self.topic)})'

    def _serialize(self):
        return self.content.encode("utf-8")

    @classmethod
    def _check_content(cls, content):
        if type(content) != str:
            raise TypeError(
                f"{cls.__name__} expects a str content but got {type(content)}."
            )
        return content

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        return bytes_.decode("utf-8")


class PickleMessage(Message):
    def _serialize(self):
        return pickle.dumps(self.content)

    @classmethod
    def _check_content(cls, content):
        return content

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        return pickle.loads(bytes_)


class NumpyMessage(Message):

    array_dtype = np.float32

    @classmethod
    def _check_content(cls, content):
        if type(content) != np.ndarray:
            raise TypeError(
                f"{cls.__name__} expects a numpy array content but got {type(content)}."
            )
        if content.shape != (len(content),):
            raise ValueError("array must be flat.")
        if content.dtype != cls.array_dtype:
            raise ValueError(f"array must be of type {cls.array_dtype}.")
        return content

    def _serialize(self):
        return self.content.tobytes()

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        return np.frombuffer(bytes_, dtype=cls.array_dtype)


class TimeAttGPSMessage(Message):

    timestamp_dtype = np.float64
    attitude_dtype = np.float32
    gps_dtype = np.float32

    @classmethod
    def _check_content(cls, content):
        if type(content) != dict:
            raise TypeError(
                f"{cls.__name__} expects a dict content but got {type(content)}."
            )
        if len(content) != 3:
            raise ValueError(
                f"{cls.__name__} expects a len 3 dict as content but got len {len(content)}."
            )
        if content.keys() != {"timestamp", "attitude", "gps"}:
            raise ValueError(
                f"{cls.__name__} expects content with keys: 'timestamp', 'attitude', 'gps' but got  {content.keys()}."
            )
        timestamp = content["timestamp"]
        if (
            len(timestamp) != 1
            or type(timestamp) != np.ndarray
            or timestamp.dtype != cls.timestamp_dtype
        ):
            raise ValueError(
                f"timestamp has to be a numpy array of length 1 and with dtype {cls.timestamp_dtype}, but was: {timestamp}"
            )
        attitude = content["attitude"]
        if (
            len(attitude) != 4
            or type(attitude) != np.ndarray
            or attitude.dtype != cls.attitude_dtype
        ):
            raise ValueError(
                f"attitude has to be a numpy array of length 4 and with dtype {cls.attitude_dtype}, but was: {attitude}"
            )
        gps = content["gps"]
        if len(gps) != 3 or type(gps) != np.ndarray or gps.dtype != cls.gps_dtype:
            raise ValueError(
                f"gps has to be a numpy array of length 3 and with dtype {cls.gps_dtype}, but was: {gps}"
            )
        return content

    @property
    def timestamp(self):
        return self.content["timestamp"]

    @property
    def attitude(self):
        return self.content["attitude"]

    @property
    def gps(self):
        """order: lat, lon, alt"""
        return self.content["gps"]

    def _serialize(self):
        return self.timestamp.tobytes() + self.attitude.tobytes() + self.gps.tobytes()

    @classmethod
    def _deserialize(cls, bytes_: bytes):
        n_timestamp_bytes = np.dtype(cls.timestamp_dtype).itemsize * 1
        n_attitude_bytes = np.dtype(cls.attitude_dtype).itemsize * 4
        n_gps_bytes = np.dtype(cls.gps_dtype).itemsize * 3
        assert len(bytes_) == n_timestamp_bytes + n_attitude_bytes + n_gps_bytes

        return {
            "timestamp": np.frombuffer(
                bytes_[:n_timestamp_bytes], dtype=cls.timestamp_dtype
            ),
            "attitude": np.frombuffer(
                bytes_[n_timestamp_bytes : n_timestamp_bytes + n_attitude_bytes],
                dtype=cls.attitude_dtype,
            ),
            "gps": np.frombuffer(
                bytes_[n_timestamp_bytes + n_attitude_bytes :], dtype=cls.gps_dtype
            ),
        }
