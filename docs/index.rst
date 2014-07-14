=================
Flask-GoogleLogin
=================
.. currentmodule:: flask_googlelogin

Flask-GoogleLogin extends Flask-Login to use Google OAuth2's authorization.

.. contents::
   :local:
   :backlinks: none

Usage
=====
Get started by creating a `GoogleLogin` instance::

    from flask_googlelogin import GoogleLogin
    googlelogin = GoogleLogin(app)
    # or
    googlelogin = GoogleLogin()
    googlelogin.init_app(app)

A `flask_login.LoginManager` instance is implicitly created in
`GoogleLogin.init_app` but you can also pass your own::

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    googlelogin = GoogleLogin(app, login_manager)

Next, you need to specify an OAuth2 callback route::

    @app.route('/oauth2callback')
    @googlelogin.oauth2callback
    def create_or_update_user(token, userinfo, **params):
        user = User.filter_by(google_id=userinfo['id']).first()
        if user:
            user.name = userinfo['name']
            user.avatar = userinfo['picture']
        else:
            user = User(google_id=userinfo['id'],
                        name=userinfo['name'],
                        avatar=userinfo['picture'])
        db.session.add(user)
        db.session.flush()
        login_user(user)
        return redirect(url_for('index'))

Decorate views with `flask_login.login_required` and you're done! ::

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')

Get the Google auth URL using `GoogleLogin.login_url`. You can also include
extra params to `login_url` and they'll be passed to your
`GoogleLogin.oauth2callback`::

    googlelogin.login_url(params=dict(section='notifications', next=url_for('.profile')))

You can also configure Google auth url params::

    googlelogin.login_url(approval_prompt='force', access_type='offline')
    googlelogin.login_url(redirect_uri=url_for('admin'))

Configuration
=============

Google API
------------------

============================== ===================================================
`GOOGLE_LOGIN_CLIENT_ID`       Client ID (create one at
                               https://code.google.com/apis/console)
`GOOGLE_LOGIN_CLIENT_SECRET`   Client Secret
`GOOGLE_LOGIN_SCOPES`          Default scopes
`GOOGLE_LOGIN_REDIRECT_URI`    Default redirect URI
`GOOGLE_LOGIN_REDIRECT_SCHEME` Scheme of redirect URI (defaults to http)
============================== ===================================================

API
===

.. autoclass:: GoogleLogin

    .. automethod:: init_app

    .. automethod:: login_url

    .. automethod:: unauthorized_callback

    .. automethod:: login

    .. automethod:: get_access_token

    .. automethod:: oauth2callback

    .. automethod:: user_loader

