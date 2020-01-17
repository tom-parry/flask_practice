from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

# note: no url_prefix param
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u ON p.author_id = u.id ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

# view for creating a blog post
@bp.route('/create', methods=('GET', 'POST'))
# user must be logged in to use this view
@login_required
def create():
    # only act if request is POST
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        # if user did not enter a title, create & save an error
        if not title:
            error = 'Title is required  >:|'
        if error is not None:
            flash(error)
        # otherwise, save post to DB
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)', 
                (title, body, g.user['id'])
            )
            db.commit()
            
            # after making post, send user back to index page
            return redirect(url_for('blog.index'))

    # on first entry, wrong request type, or after error, render the create page
    return render_template('blog/create.html')

# get one post by id
def get_post(id, check_author=True):
    # get one post from DB by author id
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username FROM post p JOIN user u on p.author_id = u.id WHERE p.id = ?',
        (id,)
    ).fetchone()

    #if no posts exist, throw an error
    if post is None:
        # abort() raises special exception that returns HTTP status code, takes optional message
        abort(404, 'Post id {0} does not exist.'.format(id))
    # if we want to check if the author of the post is the same as current user, and they are not, throw an error
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    # otherwise, return the post
    return post

# url will look like: /123/update. In which case, id = 123
# Flask can capture params from urls
# params will be strings unless declared otherwise (e.g. <int:>)
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # get post of author whose id is in url
    post = get_post(id)

    # only act if request method is POST
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        # post must have title
        if not title:
            error = 'Title is required  >:|'
        if error is not None:
            flash(error)
        # if post has title, update the post in the DB with changes from the webpage
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # after saving return to index
            return redirect(url_for('blog.index'))

    # render this page initially and after any errors or incorrect request methods
    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute(
        'DELETE FROM post WHERE id = ?',
        (id,)
    )
    db.commit()
    return redirect(url_for('blog.index'))