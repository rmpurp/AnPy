import datetime as dt
from typing import List, Iterable, NamedTuple

from anpy import AbstractDataHandler
from anpy import Record

DAYS_IN_A_WEEK = 7


class DailyStat(NamedTuple):
    name: str
    cat_id: int
    seconds_working: float


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


def get_subject_breakdown(records: Iterable[Record]):
    record_dict = dict()
    for record in records:
        seconds = (record.end - record.start).total_seconds()
        record_dict[(record.name, record.cat_id)] = record_dict.get(
            (record.name, record.cat_id), 0) + seconds
    result = []
    for (name, id), value in record_dict.items():
        result.append(DailyStat(name, id, value))
    return result
