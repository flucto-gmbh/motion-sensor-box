from influxdb_client import InfluxDBClient, QueryApi
from msb.config import load_config
from .config import InfluxDBConf
import pandas as pd


def build_query(options: dict) -> str:
    query = (
        f'from(bucket:"{options["bucket"]}")'
        + f'|> range(start: {options["start"].isoformat("T")}, stop: {options["end"].isoformat("T")})'
        + f'|> filter(fn:(r) => r._measurement == "{options["measurement"]}")'
    )
    if options["filter"]:
        for attribute, value in options["filter"].items():
            if isinstance(value, list):
                query += f'|> filter(fn:(r) => r.{attribute} == "{value[0]}"'
                for vv in value[1:]:
                    query += f' or r.{attribute} == "{vv}"'
                query += ")"
            else:
                query += f'|> filter(fn:(r) => r.{attribute} == "{value}")'

    query += (
        f'|> aggregateWindow(every: {options["resample"]}, fn: mean)'
        + f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
    )

    return query


class Influx_Subscriber:
    def __init__(self, config: InfluxDBConf, query: str):
        self.config = config
        self.query = query
        self.df: pd.DataFrame = None

        self.client: InfluxDBClient = InfluxDBClient(
            url=self.config.url,
            token=self.config.all_access_token or self.config.read_token,
            org=self.config.org,
            timeout=60_000,
        )
        self.reader = self.client.query_api()

        self._run_query()

    def receive(self) -> dict:
        return next(self)

    def _run_query(self):
        self.df = self.reader.query_data_frame(self.query, org=self.config.org)
        self.df["epoch"] = pd.to_numeric(self.df["_time"]) / 1e9
        self.df.drop(
            columns=[
                "result",
                "table",
                "_start",
                "_stop",
                "_measurement",
                "_time",
                "topic",
            ],
            inplace=True,
        )

    def __iter__(self):
        for _, row in self.df.iterrows():
            yield row.to_dict()

    def __next__(self):
        return self.__iter__().__next__()
