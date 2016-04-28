import sqlite3
from flask import g

DATABASE = 'resources/sqlite/AsAppChat.db'


def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def make_dicts(cur, row):
    return dict((cur.description[idx][0], value)
                for idx, value in enumerate(row))


def query_db(query, args=(), one=False):

    def make_dicts(cursor, row):
        return dict((cur.description[idx][0], value)
                    for idx, value in enumerate(row))

    db = get_db()
    db.row_factory = make_dicts

    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()
