from influxdb_client import InfluxDBClient, QueryApi
from msb.config import load_config
from .config import InfluxDBConf
import pandas as pd


def build_query(options):
    query = (
        f'from(bucket:"{options["bucket"]}")'
        + f'|> range(start: {options["start"].isoformat("T")}, stop: {options["end"].isoformat("T")})'
        # + f'|> range(start: {"2023-06-18T20:30:00Z"}, stop: {"2023-06-18T22:30:00Z"})'
        + f'|> filter(fn:(r) => r._measurement == "{options["measurement"]}")'
    )
    if options["filter"]:
        for attribute, value in options["filter"].items():
            if isinstance(value, list):
                query = query + f'|> filter(fn:(r) => r.{attribute} == "{value[0]}"'
                for vv in value[1:]:
                    query = query + f' or r.{attribute} == "{vv}"'
                query = query + ")"
            else:
                query = query + f'|> filter(fn:(r) => r.{attribute} == "{value}")'

    query = (
        query
        + f'|> aggregateWindow(every: {options["resample"]}, fn: mean)'
        + f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
    )

    return query


class FluxSubscriber:
    def __init__(self, config: InfluxDBConf, query: str):
        self.config = config
        self.buffer: pd.DataFrame = None
        # self.write_options = SYNCHRONOUS
        token = self.config.all_access_token or self.config.read_token
        print(f"Retrieving from {self.config.url}")
        self.client: InfluxDBClient = InfluxDBClient(
            url=self.config.url, token=token, org=self.config.org, timeout=60_000
        )
        self.reader = self.client.query_api()
        self.query = query
        self.run_query()
        self.iter_pos = 0

    def simple_query(self):
        return self.reader.query(self.query, org=self.config.org)

    def run_query(self):
        self.df = self.reader.query_data_frame(self.query, org=self.config.org)
        self.df["epoch"] = pd.to_numeric(self.df["_time"]) / 1e9
        self.df.drop(
            columns=["result", "table", "_start", "_stop", "_measurement", "_time", "topic"],
            inplace=True,
        )

    def receive(self) -> dict:
        # df: pd.DataFrame = self.reader.query_data_frame(self.query, org=self.config.org)

        return_dict =  self.df.iloc[self.iter_pos].to_dict()
        self.iter_pos += 1
        return return_dict


    def __iter__(self):
        for _, row in self.df.iterrows():
            yield row.to_dict()

    def __next__(self):


    # def __del__(self):

    #     self.reader.close()
    #     self.client.close()
