"""
Flask-GoogleLogin
"""

from base64 import (urlsafe_b64encode as b64encode,
                    urlsafe_b64decode as b64decode)
from urllib import urlencode
from urlparse import parse_qsl
from functools import wraps
import httplib2

from apiclient.discovery import build
from flask import request, redirect, abort
from flask_login import *
from oauth2client.client import OAuth2WebServerFlow


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

    def init_app(self, app, login_manager=None):
        """Initialize with app configuration. Existing
        `flaskext.login.LoginManager` instance can be passed."""

        # Check if login manager has been init
        if not hasattr(app, 'login_manager'):
            self.login_manager.init_app(app)

        # Google OAuth2 web server flow
        scopes = app.config.get('GOOGLE_LOGIN_SCOPES', '').split(',')
        if USERINFO_PROFILE_SCOPE not in scopes:
            scopes.append(USERINFO_PROFILE_SCOPE)
        self.flow = OAuth2WebServerFlow(
            app.config.get('GOOGLE_LOGIN_CLIENT_ID'),
            app.config.get('GOOGLE_LOGIN_CLIENT_SECRET'),
            scopes, redirect_uri=app.config.get('GOOGLE_LOGIN_REDIRECT_URI'))

        # Step 1) Redirect to auth page
        auth_url = self.flow.step1_get_authorize_url()

        # Set views to OAuth2 authorization urls
        self.login_manager.login_view = auth_url
        self.login_manager.refresh_view = auth_url

        # Clear flashed messages since we redirect to auth immediately
        self.login_manager.login_message = None
        self.login_manager.needs_refresh_message = None

        # Set default unauthorized callback
        self.login_manager.unauthorized_handler(self.unauthorized_callback)

    def login_url(self, **params):
        """Return login url with params encoded in state"""
        url = self.login_manager.login_view
        state = dict(nonce=make_secure_token(**params), **params)
        return url + '&' + urlencode(dict(state=b64encode(urlencode(state))))

    def unauthorized_callback(self):
        """Redirect to login url with next param set as request.url"""
        return redirect(self.login_url(next=request.url))

    def login(self):
        """Exchanges code for tokens and returns `userinfo`"""
        code = request.args.get('code')
        if not code:
            abort(400)

        # Step 2) Exchange code for credentials
        credentials = self.flow.step2_exchange(code)

        # Get user info
        try:
            http = credentials.authorize(httplib2.Http())
            client = build('oauth2', 'v2', http=http)
            userinfo = client.userinfo().get().execute()
        except Exception:
            # TODO: Proper exception handling
            return

        return userinfo, credentials

    def get_params(self):
        """Get params from state"""
        return dict(parse_qsl(b64decode(str(request.args.get('state')))))

    def oauth2callback(self, view_func):
        """Decorator for OAuth2 callback. Calls `GoogleLogin.login` then
        passes results to `view_func`."""
        @wraps(view_func)
        def decorated(*args, **kwargs):
            # Check nonce
            params = self.get_params()
            if params.pop('nonce') != make_secure_token(**params):
                return self.login_manager.unauthorized()

            # Get userinfo and credentials
            userinfo, credentials = self.login()

            if userinfo:
                params.update(userinfo=userinfo, credentials=credentials)
                return view_func(**params)
            else:
                return self.login_manager.unauthorized()

        return decorated

    def user_loader(self, func):
        """Shortcut to `login_manager`'s
        `flaskext.login.LoginManager.user_loader`"""
        self.login_manager.user_loader(func)
