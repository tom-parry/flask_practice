import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# create Blueprint named auth, with URL prefix /auth for access
bp = Blueprint('auth', __name__, url_prefix='/auth')

# associate /auth/register with register() view function
@bp.route('/register', methods=('GET', 'POST'))
# registration for new users
def register():
    # if user submitted form, request will be of type POST. Start validating.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # verify we received a username & password & the user does not already exist
        if not username:
            error = 'Username is required!'
        elif not password:
            error = 'Password is required!!'
        # fetchone() returns one row from query (same as LIMIT 1 in SQL command?)
        # to get all results, use fetchall()
        elif db.execute('SELECT id FROM usr WHERE username = ?', (username,)).fetchone() is not None:
            error = 'User {} is already registered'.format(username)
        
        # validation succeeded, insert new user into DB
        # store hash of password, not password itself
        if error is None:
            db.execute(
                'INSERT INTO usr (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            # Since query modifies data, must commit() to save changes
            db.commit()
            return redirect(url_for('auth.login'))
        
        # if validation failed, show error to user
        # flash() stores messages that can be retrieved when rendering the template
        flash(error)

    # when user initially navigates here, or when we see a validation error, render registration page
    return render_template('auth/register.html')

# associate /auth/login with login() view function
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # if request is POST, get username and password data
    # load DB, and try to find username in database
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM usr WHERE username = ?', (username,)
        ).fetchone()

        # if we could not find user, error
        if user is None:
            error = 'Incorrect Username :('
        # if password is incorrect, error
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password 0v0'

        # if no errors, save user info to session object
        if error is None:
            # session object is a dict that stores data across requests
            # stored in a browser cookie
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        # if validation failed, show error
        flash(error)

    # render page on load and on bad login
    return render_template('auth/login.html')

# run before every view function is called
@bp.before_app_request
def load_logged_in_user():
    # get user_id from the session
    user_id = session.get('user_id')

    # if no id, no user. else, get user info from DB
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM usr WHERE id = ?', (user_id,)
        ).fetchone()

# I hope you understand this by now
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# wrapper for a view: checks for a logged in user. If no user, redirect to the login page
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view