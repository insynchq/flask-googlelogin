from functools import wraps
import httplib2

from apiclient.discovery import build
from flask import request, abort
from flask_login import *
from oauth2client.client import OAuth2WebServerFlow


USERINFO_PROFILE_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'


class GoogleLogin(object):

    def __init__(self, app=None, login_manager=None):
        if app:
            self.app = app
            self.init_app(app, login_manager)

    def init_app(self, app, login_manager=None):
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

        if login_manager:
            self.login_manager = login_manager
        else:
            self.login_manager = LoginManager()
            self.login_manager.setup_app(app)
        self.login_manager.login_view = auth_url
        self.login_manager.refresh_view = auth_url

    def oauth2callback(self, view_func):
        @wraps(view_func)
        def decorated(*args, **kwargs):
            userinfo = self.login()
            if userinfo:
                kwargs.setdefault('userinfo', userinfo)
                return view_func(*args, **kwargs)
            else:
                return self.login_manager.unauthorized()
        return decorated

    def login(self):
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

        return userinfo