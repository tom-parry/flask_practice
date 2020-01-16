import os

from flask import Flask, redirect, url_for

# application factory function
def create_app(test_config=None):
    # create & configure Flask app

    # __name__ is name of current module, app needs to know where it's located.
    # instance_relative_config=True tells app taht config files are relative to instance folder
    app = Flask(__name__, instance_relative_config=True)
    
    # set default configs
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # if test_config is present, use it. Else load from config.py
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # make sure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # simple entry point
    @app.route('/')
    def hello():
        return redirect(url_for('auth.login'))

    # initialize app
    from . import db
    db.init_app(app)

    # register authentication Blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    
    # make sure url_for('index') and url_for('blog.index') will be equivalent
    app.add_url_rule('/', endpoint='index')
    
    return app