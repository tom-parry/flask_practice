import os

from flask import Flask

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
        return "Hello World"
    
    return app