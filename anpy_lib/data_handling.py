import collections
import datetime as dt
import sqlite3

DATABASE = 'data.db'

Session = collections.namedtuple('Session',
                                 'cat_id time_start done_or_canceled')


def create_database(path: str = DATABASE):
    db = sqlite3.Connection(path)
    create_tables(db)
    return db


def get_categories(db: sqlite3.Connection, only_active: bool = True):
    if only_active:
        cur = db.execute('SELECT cat_id, name FROM categories WHERE active')
    else:
        cur = db.execute('SELECT cat_id, name FROM categories')
    return dict(cur.fetchall())


def create_tables(db: sqlite3.Connection):
    db.execute(
        'CREATE TABLE IF NOT EXISTS categories(name UNIQUE, active DEFAULT TRUE, cat_id PRIMARY KEY AUTOINCREMENT);'
    )
    db.execute(
        'CREATE TABLE IF NOT EXISTS current(cat_id, time_start, done_or_canceled DEFAULT FALSE);'
    )
    db.execute(
        'CREATE TABLE IF NOT EXISTS records(cat_id, time_start, time_end, ignored DEFAULT FALSE);'
    )
    db.commit()


def add_category(db: sqlite3.Connection, name: str, status: bool = True):
    probe = db.execute('SELECT name FROM categories WHERE name = ? AND active',
                       [name]).fetchone()
    if probe:
        raise AlreadyExistsError('Active category with that name exists')

    db.execute(
        'INSERT OR REPLACE INTO categories(name, active) VALUES (?, ?)',
        [name, status]
    )
    db.commit()


def start(db: sqlite3.Connection, cat_id: int, datetime: dt.datetime):
    if is_active_session(db):
        raise AlreadyExistsError('Current session still running')
    db.execute('INSERT OR REPLACE INTO current VALUES (?, ?)',
               [cat_id, datetime])
    db.commit()


def mark_done_or_cancel(db: sqlite3.Connection):
    cur = db.execute(
        'SELECT ROWID FROM current ORDER BY time_start DESC LIMIT 1')
    row = cur.fetchone()[0]
    db.execute('UPDATE current SET done_or_canceled = 1 WHERE ROWID = ?',
               [row])
    db.commit()


def is_active_session(db: sqlite3.Connection):
    return not get_most_recent_session(db).done_or_canceled


def get_most_recent_session(db: sqlite3.Connection):
    """Return a tuple with the contents from the most recent session"""
    cur = db.execute(
        'SELECT cat_id, time_start, done_or_canceled FROM current ORDER BY time_start DESC LIMIT 1')
    return Session(*cur.fetchone())


def complete(db: sqlite3.Connection, datetime: dt.datetime = None):
    if datetime is None:
        datetime = dt.datetime.now()

    if is_active_session(db):
        mark_done_or_cancel(db)
        session = get_most_recent_session(db)
        db.execute('INSERT INTO records VALUES (?, ?, ?)',
                   [session.cat_id,
                    session.time_start,
                    dt.datetime.now().timestamp()])
        db.commit()
    else:
        raise RuntimeError('No running session')


def rename_category(db, name: str, active: bool = True):
    raise NotImplemented


class AlreadyExistsError(RuntimeError):
    pass
