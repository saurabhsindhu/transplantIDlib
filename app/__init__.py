"""
An application inspired by KerkoApp.
"""

from flask import current_app, Flask, g, redirect, request, render_template
from flask_babel import get_locale

from kerko import blueprint as kerko_blueprint

from . import logging
from .assets import assets
from .config import CONFIGS
from .extensions import babel, babel_domain, bootstrap


def create_app(config_name):
    """
    Application factory.

    Explained here: http://flask.pocoo.org/docs/patterns/appfactories/

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(CONFIGS[config_name]())
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    assets.init_app(app)
    babel.init_app(app)
    logging.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    # Setting `url_prefix` is required to distinguish the blueprint's static
    # folder route URL from the app's.
    app.register_blueprint(kerko_blueprint, url_prefix='/')


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500.
        error_code = getattr(error, 'code', 500)
        babel_domain.as_default()
        context = {
            'locale': get_locale(),
        }
        return render_template(f'app/{error_code}.html.jinja2', **context), error_code

    for errcode in [400, 403, 404, 500, 503]:
        app.errorhandler(errcode)(render_error)
