from io import TextIOWrapper
from ast import expr_context
import time
from os import path
from datetime import datetime, timezone, timedelta
import sys, signal
from typing import Text

DT_INTERVAL = 600  # seconds for each file


def exit_handler(signal, frame):
    print(" byeeeee")
    sys.exit(0)


def calc_interval_from_timestamp(t: float, dt_interval: int = DT_INTERVAL):

    interval_minutes = dt_interval / 60

    # convert unix epoch to datetime object
    timestamp = datetime.fromtimestamp(t, timezone.utc)

    # create a new datetime object without the seconds
    timestamp_minutes = datetime(
        timestamp.year,
        timestamp.month,
        timestamp.day,
        timestamp.hour,
        timestamp.minute,
        tzinfo=timezone.utc,
    )

    # calculate the remaining minutes until the next interval is due
    remaining_minutes = interval_minutes - (timestamp_minutes.minute % interval_minutes)

    # calculate the timestamp of the next interval
    next_interval = timestamp_minutes + timedelta(minutes=remaining_minutes)

    # convert the timestamp of the next interval to unix epoch
    return int(next_interval.timestamp())


def get_next_interval(current_interval: int, dt_interval: int = DT_INTERVAL):
    return current_interval + dt_interval


def get_interval_file_handle(
    interval: int,
    log_file_prefix: str,
    log_dir: str,
    timestring: str = "%Y%m%dT%H%M%S%z",
    verbose=False,
) -> TextIOWrapper:
    # create human readable datetime
    interval_iso = datetime.fromtimestamp(interval, timezone.utc).strftime(timestring)
    filepath = path.join(log_dir, f"{log_file_prefix.lower()}_{interval_iso}.log")

    try:
        file_handle = open(filepath, "w")
    except Exception as e:
        print(f"failed to open file handle {filepath}: {e}")
        sys.exit(-1)

    if verbose:
        print(f"new file handle: {filepath}")

    return file_handle


def update_interval_file_handle(
    current_interval: int,
    current_file_handle: TextIOWrapper,
    log_file_prefix: str,
    log_dir: str,
    dt_interval: int = DT_INTERVAL,
    verbose: bool = False,
) -> tuple:

    # get the next interval
    next_interval = get_next_interval(
        current_interval=current_interval, dt_interval=dt_interval
    )

    # create and open a new file handle
    next_file_handle = get_interval_file_handle(
        interval=next_interval,
        log_file_prefix=log_file_prefix,
        log_dir=log_dir,
        verbose=verbose,
    )

    # close current file handle
    try:
        current_file_handle.close()
    except Exception as e:
        print(f"failed to close file handle: {e}")
        sys.exit(-1)

    return (next_interval, next_file_handle)


def main():
    signal.signal(signal.SIGINT, exit_handler)

    current_interval_epoch = calc_interval_from_timestamp(time.time())
    current_interval_string = datetime.fromtimestamp(
        current_interval_epoch, timezone.utc
    )

    print(f"current interval: {current_interval_epoch} ({current_interval_string})")
    file_handle = get_interval_file_handle(current_interval_epoch, "test", ".")
    print(f"logfile: {file_handle}")
    file_handle.write("blabla")

    next_interval_epoch, file_handle = update_interval_file_handle(
        current_interval=current_interval_epoch,
        current_file_handle=file_handle,
        log_file_prefix="test",
        log_dir=".",
    )
    next_interval_string = datetime.fromtimestamp(next_interval_epoch, timezone.utc)
    print(f"next interval: {next_interval_epoch} ({next_interval_string})")
    file_handle.writelines("blubblubb")
    print(f"logfile: {file_handle}")
    file_handle.close()


if __name__ == "__main__":
    main()
