import pytest

from msb.network.influxdb.config import InfluxDBConf
from msb.network.influxdb.subscriber import FluxSubscriber, build_query


def test_influxdb_conf_default():
    conf = InfluxDBConf()
    assert conf.host == "localhost"
    assert conf.port == "8086"
    assert conf.bucket == "test"
    assert conf.org == "test"
    assert conf.ssl is False
    assert conf.read_token == ""
    assert conf.write_token == ""
    assert conf.all_access_token == ""
    assert conf.url == "http://localhost:8086"


def test_influxdb_conf_constructor():
    conf = InfluxDBConf(
        host="192.168.1.122",
        port="8080",
        bucket="flucto",
        org="flucto",
        ssl=True,
        read_token="readtoken",
        write_token="writetoken",
        all_access_token="allyourbasearebelongtous",
    )
    assert conf.host == "192.168.1.122"
    assert conf.port == "8080"
    assert conf.bucket == "flucto"
    assert conf.org == "flucto"
    assert conf.ssl is True
    assert conf.read_token == "readtoken"
    assert conf.write_token == "writetoken"
    assert conf.all_access_token == "allyourbasearebelongtous"
    assert conf.url == "https://192.168.1.122:8080"


def test_query_builder():
    from datetime import datetime, timezone

    options = {
        "bucket": "flucto",
        "start": datetime(2023, 7, 1, 0, 0, 0, tzinfo=timezone.utc),
        "end": datetime(2023, 7, 1, 1, 0, 0, tzinfo=timezone.utc),
        "measurement": "test",
        "filter": {},
        "resample": "1min",
    }

    query = build_query(options)

    expected = (
        "from(bucket:flucto)\n"
        + "|> range(start: 2023-07-01T00:00:00+00:00, end: 2023-07-01T01:00:00+00:00)\n"
        + '|> filter(fn:(r) => r._measurement == "test)\n'
        + "|> aggregateWindow(every: 1min, fn: mean)\n"
        + '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
    )

    assert query == expected, f"Not as expected:\n{expected}\nreceived:\n{query}"


def test_subscriber():
    from datetime import datetime, timezone
    from msb.network.influxdb.config import InfluxDBConf
    from msb.network.influxdb.subscriber import FluxSubscriber, build_query
    import json

    with open("token.txt", "r") as f:
        read_token = f.readline()

    conf = InfluxDBConf(
        read_token=read_token,
        org="flucto",
        host="192.168.1.122",
        bucket="yunlin",
    )

    options = {
        "bucket": "flucto",
        "start": datetime(2023, 7, 1, 0, 0, 0, tzinfo=timezone.utc),
        "end": datetime(2023, 7, 1, 1, 0, 0, tzinfo=timezone.utc),
        "measurement": "yunlin",
        "filter": {"_field": ["acc_x", "acc_y"]},
        "resample": "10m",
    }

    query = build_query(options)
    print(query)
    reader = FluxSubscriber(conf, query)

    for d in reader:
        print(json.dumps(d, indent=2))
