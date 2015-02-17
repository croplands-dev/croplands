from gfsad.exceptions import FieldError, UserError, Unauthorized, InvalidLocation
from gfsad import limiter
from gfsad.views.json_response import JSONResponse
from itsdangerous import SignatureExpired, BadSignature
from flask import render_template, request
from sqlalchemy.exc import IntegrityError

def init_error_handlers(app):
    @app.errorhandler(FieldError)
    def handle_field_error(e):
        return JSONResponse(status_code=400, description='Missing required data',
                            error='Bad request')
    @app.errorhandler(UserError)
    def handle_user_error(e):
        return JSONResponse(**e.__dict__)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(429)
    def rate_limit_handler(e):
        return JSONResponse(status_code=429, error='Exceeded Rate Limit',
                            description='Slow Down! ' + e.description)

    @app.errorhandler(SignatureExpired)
    def signature_expired(e):
        return JSONResponse(status_code=401, description='Token is expired.')

    @app.errorhandler(BadSignature)
    def signature_expired(e):
        return JSONResponse(status_code=400, error='Bad Signature', description='Your token is not valid.')

    @app.errorhandler(Unauthorized)
    def unauthorized_handler(e):
        return JSONResponse(status_code=401, error='Unauthorized', description=e.description)

    @app.errorhandler(InvalidLocation)
    def invalid_location_handler(e):
        return JSONResponse(**e.__dict__)