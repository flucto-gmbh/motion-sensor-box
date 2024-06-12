import pytest
import numpy as np


class MockData:
    def __init__(self, start):
        pass


def linear_data(times, values):
    for t, y in zip(times, values):
        yield (t, y)


class MockSubscriber:
    def __init__(self, data_func):
        self.data_func = data_func
        self.topic = b"mock"

    def receive(self):
        return (self.topic, next(self.data_func))


class TimestampInterpolator:
    def __init__(self, subscriber, dt):
        self.sub = subscriber
        self.dt = dt
        self.last_x = None
        self.next_x = None
        self.last_t = None
        self.next_t = None
        self.t = 0
        self.topic = b"interp"

    def _update(self):
        topic, data = self.sub.receive()
        timestep, value = data
        self.last_x = self.next_x
        self.next_x = value
        self.last_t = self.next_t
        self.next_t = timestep
        if self.last_x is None:
            self.t = self.next_t
            self._update()

    def _interpolate(self):
        # linear interpolation
        # x(t) = x_0 + Dx/Dt * dt
        # Dx = x_1 - x_0
        # Dt = t_1 - t_0
        t = self.t + self.dt
        self.t = t
        delta_t = self.next_t - self.last_t
        delta_x = self.next_x - self.last_x
        dt = self.t - self.last_t
        dx = delta_x / delta_t * dt
        x = self.last_x + dx
        return (t, x)

    def _needs_update(self):
        # Do we have data?
        if self.last_t is None:
            return True
        if self.t > self.next_t:
            return True
        return False

    def receive(self):
        # See if we need new incoming data
        if self._needs_update():
            self._update()
        t, v = self._interpolate()
        return (self.topic, (t, v))


def test_mock_subscriber():
    input_timestamps = np.linspace(4, 5, 10)
    input_values = np.linspace(0, 100, 10)
    data_generator = linear_data(input_timestamps, input_values)
    mock_sub = MockSubscriber(data_generator)

    for t in range(10):
        assert mock_sub.receive()[1] == (input_timestamps[t], input_values[t])


def test_interpolates_to_timestamp():
    input_timestamps = np.linspace(10, 20, 11)
    input_values = np.linspace(0, 100, 11)
    expected_values = np.linspace(0, 100, 101)
    data_generator = linear_data(input_timestamps, input_values)
    mock_sub = MockSubscriber(data_generator)

    interpolator = TimestampInterpolator(mock_sub, 0.1)

    for t in range(100):
        topic, data = interpolator.receive()
        val = data[1]
        assert round(val) == round(expected_values[t + 1])


def test_downsample():
    input_timestamps = np.linspace(10, 20, 101)
    output_timestamps = np.linspace(10, 20, 11)
    input_values = np.linspace(0, 100, 101)
    expected_values = np.linspace(0, 100, 11)

    data_generator = linear_data(input_timestamps, input_values)
    mock_sub = MockSubscriber(data_generator)

    interpolator = TimestampInterpolator(mock_sub, 0.1)

    for t in range(100):
        topic, data = interpolator.receive()
        val = data[1]
        assert round(val) == round(expected_values[t + 1])
@pytest.fixture
def setup_mock_input():
    pass


if __name__ == "__main__":
    test_interpolates_to_timestamp()
