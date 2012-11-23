from setuptools import setup


setup(
    name='Flask-GoogleLogin',
    version='0.0.1',
    py_modules=['flask_googlelogin'],
    author="Mark Steve Samson",
    author_email='hello@marksteve.com',
    description="Extends Flask-Login to use Google's OAuth2 authentication",
    install_requires=[
        'google-api-python-client==1.0',
        'Flask-Login==0.1.3',
    ],
)
