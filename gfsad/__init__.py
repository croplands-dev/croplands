from flask import Flask, request, g, redirect
from flask.ext.cache import Cache
from flask.ext.compress import Compress
from flask.ext.restless import APIManager
from flask_jwt import JWT
from flask_mail import Mail
from gfsad.exceptions import FieldError
from flask.ext.celery import Celery
from flask_limiter import Limiter, HEADERS
from gfsad.misc import PostMarkHandler
import logging
from urlparse import urlparse, urlunparse


# APIManager.APINAME_FORMAT = 'api.{0}'
# APIManager.BLUEPRINTNAME_FORMAT = '{0}'


class JSONLimiter(Limiter):
    def inject_headers(self, response):
        current_limit = getattr(g, 'view_rate_limit', None)
        if self.enabled and self.headers_enabled and current_limit:
            window_stats = self.limiter.get_window_stats(*current_limit)
            response.headers.add(
                self.header_mapping[HEADERS.LIMIT],
                str(current_limit[0].amount)
            )
            response.headers.add(
                self.header_mapping[HEADERS.REMAINING],
                str(window_stats[1])
            )
            response.headers.add(
                self.header_mapping[HEADERS.RESET],
                str(window_stats[0])
            )
        return response


cache = Cache(config={'CACHE_TYPE': 'simple'})
compress = Compress()
limiter = JSONLimiter(headers_enabled=True, global_limits=["1000 per minute"])
api = APIManager()
jwt = JWT()
celery = Celery()
mail = Mail()

from gfsad.models import db, User


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = request.headers.get(
        'Access-Control-Request-Headers', '')
    response.headers['Access-Control-Allow-Methods'] = request.headers.get(
        'Access-Control-Request-Methods', '')

    # Do nothing for post, patch, delete etc..
    try:
        method = [e for e in request.url_rule.methods][-1]
    except AttributeError:
        # print "add_cors_headers: Attribute Error - " + str(response)
        return response

    if method in ['PUT', 'PATCH', 'DELETE', 'POST', 'OPTIONS']:
        return response

    # set cache max age
    if '/api' in request.url_rule.rule:
        response.headers['Cache-Control'] = 'max-age=120'

    elif '/gee/time_series' in request.url_rule.rule:
        response.headers['Cache-Control'] = 'max-age=4000000'
    elif '/gee/maps' in request.url_rule.rule:
        response.headers['Cache-Control'] = 'max-age=80000'
    else:
        response.headers['Cache-Control'] = 'max-age=0'

    return response


def create_app(config='Testing'):
    app = Flask(__name__)

    # Configure the flask app
    app.config.from_object("gfsad.config." + config)

    # initialize all of the extensions
    jwt.init_app(app)
    celery.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    compress.init_app(app)
    mail.init_app(app)
    api.init_app(app, flask_sqlalchemy_db=db)

    # import and register all of the blueprints
    from gfsad.views.public import public
    from gfsad.views.auth import auth
    from gfsad.views.gee import gee
    from gfsad.views.aws import aws

    app.register_blueprint(public)
    app.register_blueprint(gee)
    app.register_blueprint(aws)
    app.register_blueprint(auth)

    from gfsad.views.api import init_api

    init_api(app)

    # import and init error handlers
    from gfsad.views.errors import init_error_handlers

    init_error_handlers(app)

    # cors headers and cache
    app.after_request(add_cors_headers)

    from gfsad.utils.log import log

    app.after_request(log)

    from gfsad.auth import load_user

    @limiter.request_filter
    def registered():
        """
        Removes limit if user is registered and using a token.
        :return:
        """
        return load_user() != "anonymous"

    if 'POSTMARK_API_KEY' in app.config:
        email_handler = PostMarkHandler(api_key=app.config['POSTMARK_API_KEY'])
        email_handler.setLevel(logging.ERROR)
        app.logger.addHandler(email_handler)

    import tasks.high_res_imagery
    import tasks.classifications

    @app.before_request
    def redirect_non_www():
        """Redirect non-www requests to www."""
        url_parts = urlparse(request.url)
        if url_parts.netloc == 'croplands.org':
            url_parts_list = list(url_parts)
            url_parts_list[1] = 'www.croplands.org'
            return redirect(urlunparse(url_parts_list), code=301)

    return app


if __name__ == "__main__":
    app = create_app()
