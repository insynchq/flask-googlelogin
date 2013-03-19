"""
Flask-GoogleLogin
"""

from base64 import (urlsafe_b64encode as b64encode,
                    urlsafe_b64decode as b64decode)
from urllib import urlencode
from urlparse import parse_qsl
from functools import wraps

from flask import request, redirect, abort, current_app
from flask_login import *
import requests


GOOGLE_OAUTH2_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_OAUTH2_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_OAUTH2_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
USERINFO_PROFILE_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'


class GoogleLogin(object):
    """Main extension class"""

    def __init__(self, app=None, login_manager=None):
        if login_manager:
            self.login_manager = login_manager
        else:
            self.login_manager = LoginManager()

        if app:
            self.app = app
            self.init_app(app)

    def init_app(self, app, add_context_processor=True, login_manager=None):
        """Initialize with app configuration. Existing
        `flaskext.login.LoginManager` instance can be passed."""

        if login_manager:
            self.login_manager = login_manager
        else:
            self.login_manager = LoginManager()

        # Check if login manager has been init
        if not hasattr(app, 'login_manager'):
            self.login_manager.init_app(app,
                add_context_processor=add_context_processor)

        # Clear flashed messages since we redirect to auth immediately
        self.login_manager.login_message = None
        self.login_manager.needs_refresh_message = None

        # Set default unauthorized callback
        self.login_manager.unauthorized_handler(self.unauthorized_callback)

    def login_url(self, params=None, **kwargs):
        """Return login url with params encoded in state"""
        if not params:
            params = {}

        app = getattr(self, 'app', current_app)

        kwargs.setdefault('access_type', 'online')
        if 'prompt' not in kwargs:
            kwargs.setdefault('approval_prompt', 'auto')

        scopes = kwargs.pop('scopes',
                            app.config.get('GOOGLE_LOGIN_SCOPES', '')
                                .split(','))
        scopes = map(lambda x: x.strip('/'), scopes)
        if USERINFO_PROFILE_SCOPE not in scopes:
            scopes.append(USERINFO_PROFILE_SCOPE)

        # NOTE: redirect_uri is stored in state for use later in getting token
        params['redirect_uri'] = kwargs.pop('redirect_uri',
            app.config.get('GOOGLE_LOGIN_REDIRECT_URI'))

        state = b64encode(urlencode(dict(sig=make_secure_token(**params),
                                         **params)))

        return GOOGLE_OAUTH2_AUTH_URL + '?' + urlencode(
            dict(response_type='code',
                 client_id=app.config['GOOGLE_LOGIN_CLIENT_ID'],
                 scope=' '.join(scopes),
                 redirect_uri=params['redirect_uri'],
                 state=state,
                 **kwargs))

    def unauthorized_callback(self):
        """Redirect to login url with next param set as request.url"""
        return redirect(self.login_url(params=dict(next=request.url)))

    def login(self, code, redirect_uri):
        """Exchanges code for tokens and returns retrieved `userinfo` and
        `token`"""

        app = getattr(self, 'app', current_app)

        token = requests.post(GOOGLE_OAUTH2_TOKEN_URL, data=dict(
            code=code,
            redirect_uri=redirect_uri,
            grant_type='authorization_code',
            client_id=app.config['GOOGLE_LOGIN_CLIENT_ID'],
            client_secret=app.config['GOOGLE_LOGIN_CLIENT_SECRET'],
            )).json
        if not token or token.get('error'):
            abort(400)

        userinfo = requests.get(GOOGLE_OAUTH2_USERINFO_URL, params=dict(
            access_token=token['access_token'],
            )).json
        if not userinfo or userinfo.get('error'):
            abort(400)

        return token, userinfo

    def oauth2callback(self, view_func):
        """Decorator for OAuth2 callback. Calls `GoogleLogin.login` then
        passes results to `view_func`."""

        @wraps(view_func)
        def decorated(*args, **kwargs):
            code = request.args.get('code')
            if not code:
                abort(400)

            # Check sig 
            params = dict(parse_qsl(b64decode(str(request.args.get('state')))))
            if params.pop('sig', None) != make_secure_token(**params):
                return self.login_manager.unauthorized()

            # Get userinfo and token
            token, userinfo = self.login(code, params.pop('redirect_uri'))

            params.update(token=token, userinfo=userinfo)

            return view_func(**params)

        return decorated

    def user_loader(self, func):
        """Shortcut to `login_manager`'s
        `flaskext.login.LoginManager.user_loader`"""
        self.login_manager.user_loader(func)
