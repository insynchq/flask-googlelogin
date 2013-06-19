import json

from flask import Flask, url_for, redirect, session

from flask_login import (UserMixin, login_required, login_user, logout_user,
                         current_user)
from flask_googlelogin import GoogleLogin


users = {}


app = Flask(__name__)
app.config.update(
    SECRET_KEY='Miengous3Xie5meiyae6iu6mohsaiRae',
    GOOGLE_LOGIN_CLIENT_ID='204903060412.apps.googleusercontent.com',
    GOOGLE_LOGIN_CLIENT_SECRET='9LQdzxkGfM2BTM10dz49uWLI',
    GOOGLE_LOGIN_REDIRECT_URI='http://localhost:5000/oauth2callback')
googlelogin = GoogleLogin(app)


class User(UserMixin):
    def __init__(self, userinfo):
        self.id = userinfo['id']
        self.name = userinfo['name']
        self.picture = userinfo.get('picture')


@googlelogin.user_loader
def get_user(userid):
    return users.get(userid)


@app.route('/')
def index():
    return """
        <p><a href="%s">Login</p>
        <p><a href="%s">Login with extra params</p>
        <p><a href="%s">Login with extra scope</p>
    """ % (
        googlelogin.login_url(),
        googlelogin.login_url(params=dict(extra='large-fries')),
        googlelogin.login_url(
            scopes=['https://www.googleapis.com/auth/drive'],
            access_type='offline'),
        )


@app.route('/profile')
@login_required
def profile():
    return """
        <p>Hello, %s</p>
        <p><img src="%s" width="100" height="100"></p>
        <p>Token: %r</p>
        <p>Extra: %r</p>
        <p><a href="/logout">Logout</a></p>
        """ % (current_user.name, current_user.picture, session.get('token'),
               session.get('extra'))


@app.route('/oauth2callback')
@googlelogin.oauth2callback
def login(token, userinfo, **params):
    user = users[userinfo['id']] = User(userinfo)
    login_user(user)
    session['token'] = json.dumps(token)
    session['extra'] = params.get('extra')
    return redirect(params.get('next', url_for('.profile')))


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return """
        <p>Logged out</p>
        <p><a href="/">Return to /</a></p>
        """


app.run(debug=True)
