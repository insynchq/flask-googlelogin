"""
Flask-GoogleLogin
-----------------
Flask-GoogleLogin extends Flask-Login to use Google's OAuth2 authorization

Links
`````
* `documentation <http://packages.python.org/Flask-GoogleLogin>`_
* `development version <https://github.com/marksteve/flask-googlelogin>`_
"""
from setuptools import setup


setup(
    name='Flask-GoogleLogin',
    version='0.0.6',
    url='https://github.com/marksteve/flask-googlelogin',
    license='MIT',
    author="Mark Steve Samson",
    author_email='hello@marksteve.com',
    description="Extends Flask-Login to use Google's OAuth2 authorization",
    long_description=__doc__,
    py_modules=['flask_googlelogin'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'requests<1.0',
        'Flask-Login==0.1.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
