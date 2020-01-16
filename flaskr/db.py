import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    # g is a special object, unique for each request. Used to store data that multiple functions might need. 
    # Reused if get_db() is called more than once in the same request
    if 'db' not in g:
        # sqlite3.connect() establishes a connection to the file pointed at by the DATABASE config key
        g.db = sqlite3.connect(
            # current_app is a special object that points to the Flask app handling the request
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row tells connection to return rows that behave like dicts
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    # check if connection was created
    db = g.pop('db', None)

    # if db exists, close it
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
