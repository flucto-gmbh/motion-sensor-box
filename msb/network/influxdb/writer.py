from influxdb_client import InfluxDBClient, WriteOptions
from msb.config import load_config
from config import InfluxDBConf


class Influx_Writer:
    def __init__(self, config: InfluxDBConf):
        self.config = config
        # self.write_options = SYNCHRONOUS
        self.write_options = WriteOptions(
            batch_size=500,
            flush_interval=10_000,
            jitter_interval=2_000,
            retry_interval=5_000,
            max_retries=5,
            max_retry_delay=30_000,
            exponential_base=2,
        )
        self.client = InfluxDBClient(
            url=self.config.url, token=self.config.token, org=self.config.org
        )
        self.writer = self.client.write_api(
            write_options=self.write_options,
        )

    def __del__(self):
        self.writer.close()
        self.client.close()

    def write_line(self, line):
        self.writer.write(bucket=self.config.bucket, record=line)

    def write_from_generator(self, generator):
        for line in generator:
            self.writer.write(bucket=self.config.bucket, record=line)

    def write_from_line_generator(self, generator):
        with InfluxDBClient(
            url=self.config.url, token=self.config.token, org=self.config.org
        ) as client:
            with client.write_api(
                write_options=self.write_options,
            ) as write_api:
                for line in generator:
                    write_api.write(bucket=self.config.bucket, record=line)


def get_parsed_flux_writer():
    config = load_config(InfluxDBConf(), "flux", read_commandline=False)
    return Influx_Writer(config)
