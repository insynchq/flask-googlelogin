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

A `flaskext.login.LoginManager` instance is implicitly created in
`GoogleLogin.init_app` but you can also pass your own::

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    googlelogin = GoogleLogin(app, login_manager)

.. tip::
    `flask_googlelogin` imports `*` from `flaskext.login` so you can do
    something like this::

        from flask_googlelogin import LoginManager

Next, you need to specify an OAuth2 callback route::

    @app.route('/oauth2callback')
    @googlelogin.oauth2callback
    def create_or_update_user(userinfo=None, credentials=None, **kwargs):
        if userinfo and credentials:
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
        else:
            return googlelogin.login_manager.unauthorized()

Notice that you still have to do the call for `login_user`. Flask-GoogleLogin
just sets the `login_view` and `refresh_view` of the
`flaskext.login.LoginManager` to Google's OAuth2 authorization url.
This is step one of the Google's OAuth2 webserver flow. The second step
(retrieving tokens) happens inside the `GoogleLogin.oauth2callback` decorator.
After getting tokens, they're used to fetch `userinfo`, which is then passed
as a keyword argument to the decorated view function.

Decorate views with `flaskext.login.login_required` and you're done! ::

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')

Configuration
=============

Google API
------------------

============================ ===================================================
`GOOGLE_LOGIN_CLIENT_ID`     Client ID (create one at
                             https://code.google.com/apis/console)
`GOOGLE_LOGIN_CLIENT_SECRET` Client Secret
`GOOGLE_LOGIN_REDIRECT_URI`  Redirect URI
============================ ===================================================

API
===

.. autoclass:: GoogleLogin

    .. automethod:: init_app

    .. automethod:: login

    .. automethod:: oauth2callback

    .. automethod:: user_loader

TODO
====
* OAuth2 `state` support
* Use `access_token` for `is_authenticated`