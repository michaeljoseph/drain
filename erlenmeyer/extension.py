import logging

from flask import g
from flask_debugtoolbar import DebugToolbarExtension
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin
from flask_peewee.db import Database
from raven.contrib.flask import Sentry


def configure(app, settings):
    app.config.from_object(settings)


def setup_logging(app, settings):
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(settings.LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
    app.logger.addHandler(file_handler)


def close_database(exception):
    db = g.get('database', None)
    if db is not None:
        db.close()


def setup_database(app, settings):
    database = Database(app)
    app.teardown_appcontext(close_database)
    return database


def setup_sentry(app, settings):
    sentry = Sentry(dsn=settings.SENTRY_DSN)
    sentry.init_app(app)


# TODO: flask-social
# TODO: flask-security
# TODO: flask-bootstrap
def init_social():
    pass


def init_bootstrap():
    pass


def init_auth(app, database, user_model):
    auth = Auth(
        app,
        database,
        user_model=user_model,
    )
    app.auth = auth


def init_admin(app, auth, models):
    admin = Admin(app, auth)
    for model in models:
        admin.register(model)
    admin.setup()


class Erlenmeyer(object):
    def __init__(self, app, settings):
        """

        Usage:

            app = Flask('application_module')
            ErlenMeyer(
                Flask(application_name)
                settings,
            )

        """
        self.app = app
        self.settings = settings
        self.init_app(app, settings)

    def init_app(self, app, settings):
        configure(app, settings)
        setup_logging(app, settings)
        setup_sentry(app, settings)
        self.database = setup_database(app, settings)
        self.toolbar = DebugToolbarExtension(app) if app.debug else None
