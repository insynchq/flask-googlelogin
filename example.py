from flask import Flask, url_for, redirect

from flask_googlelogin import (GoogleLogin, UserMixin, login_required,
                               login_user, logout_user, current_user)


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
        <p><a href="%s">Login with next</p>
    """ % (googlelogin.login_url(),
           googlelogin.login_url(next=url_for('.profile')))

@app.route('/profile')
@login_required
def profile():
    return """
        <p>Hello, %s</p>
        <p><img src="%s" width="100" height="100"></p>
        <p><a href="/logout">Logout</a></p>
        """ % (current_user.name, current_user.picture)


@app.route('/oauth2callback')
@googlelogin.oauth2callback
def login(userinfo, credentials, next=None):
    user = users[userinfo['id']] = User(userinfo)
    login_user(user)
    return redirect(next or url_for('.profile'))


@app.route('/logout')
def logout():
    logout_user()
    return """
        <p>Logged out</p>
        <p><a href="/">Return to /</a></p>
        """


app.run(debug=True)
