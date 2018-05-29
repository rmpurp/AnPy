import datetime as dt
import sqlite3
from typing import Optional

from anpy import AbstractDataHandler
from anpy import Record
from anpy import Session


class SQLDataHandler(AbstractDataHandler):

    def __init__(self, db: sqlite3.Connection):
        self.db: sqlite3.Connection = db
        self._create_tables()
        db.commit()

    def new_category(self, name: str):
        """Create new category with the given name and get the associated id.

        The name parameter must be non-empty, else a ValueError will be raised.
        """

        name = name.strip()
        if not name:
            raise ValueError
        probe = self.db.execute(
            'SELECT name FROM categories WHERE name = ? AND active',
            [name]).fetchone()
        if probe:
            raise RuntimeError('Active category with that name exists')

        self.db.execute(
            'INSERT OR REPLACE INTO categories(name) VALUES (?)',
            [name]
        )
        self.db.commit()

    def set_category_activation(self, cat_id: int, status: bool):
        """Set the active status of the given category to the given state."""
        if self.does_category_exist(cat_id):
            self.db.execute('UPDATE categories SET active = ? where cat_id = ?',
                            [status, cat_id])
        else:
            raise ValueError('Does not exist')

    def get_categories(self, active_only: bool = True) -> dict:

        if active_only:
            cur = self.db.execute(
                'SELECT name, cat_id FROM categories WHERE active')
        else:
            cur = self.db.execute('SELECT name, cat_id FROM categories')
        return dict(cur.fetchall())

    def start(self, cat_id: int, start: Optional[dt.datetime] = None):
        """Record the beginning of a working session.

        If there is no datetime object passed in, the datetime associated with
        the current instant will be used instead.
        """
        if start is None:
            start = dt.datetime.now()

        if self.is_active_session():
            raise RuntimeError('Current session still running')
        self.db.execute('INSERT OR REPLACE INTO beginnings(cat_id, time_start) '
                        + 'VALUES (?, ?)', [cat_id, start.timestamp()])
        self.db.commit()

    def cancel(self):
        """Cancel the current working session that is running"""
        assert self.is_active_session(), 'No active session'
        self._mark_done_or_cancel()

    def complete(self, end: dt.datetime = None):
        """Record the end of a current working session.

        If there is no datetime object passed in, the datetime associated with
        the current instant will be used instead.
        """
        if end is None:
            end = dt.datetime.now()

        if self.is_active_session():
            self._mark_done_or_cancel()
            session = self.get_most_recent_session()
            self.db.execute('INSERT INTO records(cat_id, time_start, time_end) '
                            + 'VALUES (?, ?, ?)',
                            [session.cat_id,
                             session.time_start.timestamp(),
                             end.timestamp()])
            self.db.commit()
        else:
            raise RuntimeError('No running session')
        pass

    def rename_category(self, cat_id: int, new_name: str):
        if self.does_category_exist(cat_id):
            self.db.execute('UPDATE categories SET name = ? WHERE cat_id = ?',
                            [new_name, cat_id])
        else:
            raise ValueError('Given category ID does not exist')

    def _create_tables(self):
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS categories(name UNIQUE, active DEFAULT 1, cat_id INTEGER PRIMARY KEY AUTOINCREMENT);'
        )
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS beginnings(cat_id, time_start, done_or_canceled DEFAULT 0);'
        )
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS records(cat_id, time_start, time_end, ignored DEFAULT 0);'
        )
        self.db.commit()

    def _mark_done_or_cancel(self):
        cur = self.db.execute(
            'SELECT ROWID FROM beginnings ORDER BY time_start DESC LIMIT 1')
        row = cur.fetchone()[0]
        self.db.execute(
            'UPDATE beginnings SET done_or_canceled = 1 WHERE ROWID = ?',
            [row])
        self.db.commit()

    def is_active_session(self):
        recent_session = self.get_most_recent_session()
        if recent_session:
            return not recent_session.done_or_canceled
        return False

    def does_category_exist(self, cat_id: int):
        cur = self.db.execute('SELECT name FROM categories WHERE cat_id = ?',
                              [cat_id])
        return bool(cur.fetchone())

    def get_most_recent_session(self):
        cur = self.db.execute(
            'SELECT cat.name, cat.cat_id, b.time_start, b.done_or_canceled '
            + 'FROM categories AS cat, beginnings as b WHERE cat.cat_id = b.cat_id ORDER BY time_start DESC LIMIT 1'
        )
        result = cur.fetchone()
        if result:
            return Session(result[0],
                           result[1],
                           dt.datetime.fromtimestamp(result[2]),
                           result[3])
        else:
            return None

    def get_records_between(self, start: dt.datetime, end: dt.datetime):
        assert start < end, 'Invalid times'
        records = self.db.execute(
            'SELECT c.name, c.cat_id, r.time_start, r.time_end '
            + 'FROM categories as c, records as r '
            + 'WHERE c.cat_id = r.cat_id AND r.time_start >= ? '
            + 'AND r.time_start < ? ORDER BY r.time_start', [start.timestamp(),
                                                             end.timestamp()]
        ).fetchall()
        return [Record(tup[0],
                       tup[1],
                       dt.datetime.fromtimestamp(tup[2]),
                       dt.datetime.fromtimestamp(tup[3]))
                for tup in records]
