import collections
import datetime as dt
import sqlite3
from typing import Optional

from anpy import AbstractDataHandler

DATABASE = 'data.db'

Session = collections.namedtuple('Session',
                                 'cat_id time_start done_or_canceled')


class SQLDataHandler(AbstractDataHandler):

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self._create_tables(self.db)
        db.commit()

    def new_category(self, name: str):
        """Create new category with the given name and get the associated id."""
        probe = self.db.execute(
            'SELECT name FROM categories WHERE name = ? AND active',
            [name]).fetchone()
        if probe:
            raise AlreadyExistsError('Active category with that name exists')

        self.db.execute(
            'INSERT OR REPLACE INTO categories(name) VALUES (?)',
            [name]
        )
        self.db.commit()
        pass

    def set_category_activation(self, cat_id: int, status: bool):
        """Set the active status of the given category to the given state."""
        pass

    def get_categories(self, active_only: bool = True):
        """Get the categories as a dict from id to name.

        If keyword argument active_only is true (default behavior), then only
        the categories that are marked active are returned. Otherwise all of
        them, including inactive ones, are returned.
        """
        if active_only:
            cur = self.db.execute(
                'SELECT cat_id, name FROM categories WHERE active')
        else:
            cur = self.db.execute('SELECT cat_id, name FROM categories')
        return dict(cur.fetchall())

    def start(self, cat_id: int, datetime: Optional[dt.datetime] = None):
        """Record the beginning of a working session.

        If there is no datetime object passed in, the datetime associated with
        the current instant will be used instead.
        """
        if self.is_active_session():
            raise AlreadyExistsError('Current session still running')
        self.db.execute('INSERT OR REPLACE INTO current VALUES (?, ?)',
                        [cat_id, datetime])
        self.db.commit()

    def cancel(self):
        """Cancel the current working session that is running"""
        raise NotImplemented

    def complete(self, datetime: dt.datetime = None):
        """Record the end of a current working session.

        If there is no datetime object passed in, the datetime associated with
        the current instant will be used instead.
        """
        if datetime is None:
            datetime = dt.datetime.now()

        if self.is_active_session():
            self.mark_done_or_cancel()
            session = self.get_most_recent_session()
            self.db.execute('INSERT INTO records VALUES (?, ?, ?)',
                            [session.cat_id,
                             session.time_start,
                             dt.datetime.now().timestamp()])
            self.db.commit()
        else:
            raise RuntimeError('No running session')
        pass

    def rename_category(self, cat_id: int, name: str):
        """Change the name of the category associated with the given id"""
        raise NotImplemented

    def _create_tables(self):
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS categories(name UNIQUE, active DEFAULT TRUE, cat_id PRIMARY KEY AUTOINCREMENT);'
        )
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS current(cat_id, time_start, done_or_canceled DEFAULT FALSE);'
        )
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS records(cat_id, time_start, time_end, ignored DEFAULT FALSE);'
        )
        self.db.commit()

    def _mark_done_or_cancel(self):
        cur = self.db.execute(
            'SELECT ROWID FROM current ORDER BY time_start DESC LIMIT 1')
        row = cur.fetchone()[0]
        self.db.execute(
            'UPDATE current SET done_or_canceled = 1 WHERE ROWID = ?',
            [row])
        self.db.commit()

    def is_active_session(self):
        return not self.get_most_recent_session().done_or_canceled

    def get_most_recent_session(self):
        """Return a tuple with the contents from the most recent session"""
        cur = self.db.execute(
            'SELECT cat_id, time_start, done_or_canceled FROM current ORDER BY time_start DESC LIMIT 1'
        )
        return Session(*cur.fetchone())


class AlreadyExistsError(RuntimeError):
    pass
