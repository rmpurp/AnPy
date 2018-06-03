import datetime as dt
from typing import List, Iterable, Dict

from anpy import AbstractDataHandler
from anpy import Record

DAYS_IN_A_WEEK = 7


def get_records_on_day(handler: AbstractDataHandler,
                       day_start: dt.datetime) -> Iterable[Record]:
    day_end = day_start + dt.timedelta(days=1)
    return handler.get_records_between(day_start, day_end)


def get_records_on_week(handler: AbstractDataHandler,
                        day_start: dt.datetime) -> List[Iterable[Record]]:
    one_day = dt.timedelta(days=1)
    records = []
    for i in range(DAYS_IN_A_WEEK):
        records.append(get_records_on_day(handler, day_start))
        day_start += one_day
    return records


def get_total_subject_breakdown(list_of_records: List[Iterable[Record]]) \
        -> List[Dict[str, float]]:
    dicts = [get_per_category_durations(r) for r in list_of_records]
    return dicts


def get_per_category_durations(records: Iterable[Record]) -> Dict[str, float]:
    record_dict = dict()
    for record in records:
        seconds = (record.end - record.start).total_seconds()
        record_dict[record.name] = record_dict.get(
            record.name, 0) + seconds
    return record_dict
