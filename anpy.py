#!/usr/bin/env python

import datetime as dt
from abc import ABC, abstractmethod
from typing import Optional, NamedTuple, Tuple


class Record(NamedTuple):
    name: str
    start: dt.datetime
    end: dt.datetime


class Session(NamedTuple):
    name: str
    time_start: dt.datetime
    done_or_canceled: bool


class AbstractDataHandler(ABC):
    @abstractmethod
    def new_category(self, name: str):
        """Create new category with the given name.

        The name parameter must be non-empty, else a ValueError will be raised.
        """
        pass

    @abstractmethod
    def set_category_activation(self, name: str, status: bool):
        """Set the active status of the given category to the given state."""
        pass

    @property
    @abstractmethod
    def active_categories(self) -> Tuple[str]:
        """Get the active categories as a tuple."""
        pass

    @property
    @abstractmethod
    def all_categories(self) -> Tuple[str]:
        """Get all categories, including inactive ones, as a list."""
        pass

    @abstractmethod
    def start(self, name: str, start: Optional[dt.datetime] = None):
        """Record the beginning of a working session.

        If there is no datetime object passed in, the datetime associated with
        the current instant will be used instead.
        """
        pass

    @abstractmethod
    def cancel(self):
        """Cancel the current working session that is running"""
        pass

    @abstractmethod
    def complete(self, end: dt.datetime = None):
        """Record the end of a current working session.

        If there is no datetime object passed in, the datetime associated with
        the current instant will be used instead.
        """
        pass

    @abstractmethod
    def get_records_between(self, start: dt.datetime, end: dt.datetime):
        """Get the records between the two times.

        The start time of a session is used to determine if a session is or is
        not between the two given datetimes. In other words, all records
        returned must start after beginning and must start before before end.

        :param start: the beginning datetime
        :param end: the ending datetime
        :return: an iterable of the records
        """
        pass

    @abstractmethod
    def rename_category(self, old_name: str, new_name: str):
        """Change the name of the category.

        """
        pass

    @abstractmethod
    def get_most_recent_session(self) -> Session:
        """Return a namedtuple with the contents from the most recent session"""
        pass
