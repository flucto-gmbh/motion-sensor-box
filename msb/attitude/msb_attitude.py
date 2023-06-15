from msb.attitude.complementary_filter import ComplementaryFilter
from msb.zmq_base.Publisher import Publisher, get_default_publisher
from msb.zmq_base.Subscriber import Subscriber, get_default_subscriber


class AttitudeService:
    def __init__(self, subscriber: Subscriber, publisher: Publisher):
        self.subscriber = subscriber
        self.publisher = publisher
        self.filter = ComplementaryFilter()

    def run(self):
        while True:
            imu_data = self.subscriber.receive()
            rpy_data = self.filter.update(imu_data)
            self.publisher.send("rpy", rpy_data)


def main():
    subscriber = get_default_subscriber("imu")
    publisher = get_default_publisher()
    attitude = AttitudeService(subscriber, publisher)
    attitude.run()
