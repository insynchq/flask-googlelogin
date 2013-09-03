Changelog
=========

0.3.0
-----

* Refactored to allow client-side flow.
* Divided ``GoogleLogin.login`` into ``GoogleLogin.exchange_code`` and
  ``GoogleLogin.get_userinfo``.
* Redirect URI no longer passed through ``state``. It's now being formed using
  ``url_for`` along with the additional config ``GOOGLE_LOGIN_REDIRECT_SCHEME``.
  The additional config is required because ``request.base_url`` always uses
  ``http`` as scheme.

0.2.2
-----

* Allow setting of ``response_type`` when generating login url
