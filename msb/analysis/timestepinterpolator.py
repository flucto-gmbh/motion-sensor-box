import pandas as pd
from msb.network.pubsub.types import Subscriber


class PandasInterpolator:
    """
    An Iterator class that interpolates data points to a fixed rate.
    """

    def __init__(self, sub: Subscriber, freq_ms: float, sample_size: int = 100):
        self.sub = sub
        self.incoming: pd.DataFrame = None
        self.outgoing: pd.DataFrame = None
        self.resampling_frequency = freq_ms
        self.sample_size = sample_size

    def resample_loop(self) -> dict:
        """
        Generator loop that yields dicts at a fixed rate
        """
        while True:
            self._listen_to_sub()
            self._convert_timestamp()

            # Reindex incoming timestamps
            self.outgoing = self.incoming.resample(
                f"{self.resampling_frequency}ms",
                offset="0s",
            ).mean()

            # After resampling, convert from DateTimeIndex to Epoch as a field
            # Index will not be returned in yield statement
            self.outgoing["epoch"] = pd.to_numeric(self.outgoing.index) / 10**9

            for _, row in self.outgoing.iterrows():
                yield row.to_dict()

    def _listen_to_sub(self):
        # Listen to incoming data
        for t in range(self.sample_size):
            topic, data = self.sub.receive()
            if self.incoming is None:
                self.incoming = pd.DataFrame(columns=data.keys())

            # list ordering?
            self.incoming.loc[t] = list(data.values())

    def _convert_timestamp(self):
        # Convert incoming data epoch to datetime index
        index = pd.to_datetime(self.incoming["epoch"], unit="s", utc=True)
        self.incoming.index = index
