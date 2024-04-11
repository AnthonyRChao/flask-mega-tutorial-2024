## Chapter 7
2024-04-08

Intentional bug left in. Create two users. Change one user's name to the other via "Edit Your Profile Link". You will receive a `500 Internal Server Error`.

```bash
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: user.username
[SQL: UPDATE user SET username=?, about_me=? WHERE user.id = ?]
[parameters: ('anthony', '', 6)]
```

## Error Handling in Flask

The stack trace helps you determine what is the bug. The application allows a user to change the username, but it does not validate that the new username chosen does not collide with another user already in the system. The error comes from SQLAlchemy, which tries to write the new username to the database, but the database rejects it because the username column is defined with the unique=True option.


## Debug Mode

The error on the page doesn't help the user whatsoever, which is reasonable when a system is running on a production server. If there is an error, the user gets a vague error page, and the important details of the error are in the server process output or in a log file.

But, if we are running in a DEV environment, Flask has a cool mode with a nice debugger directly on your browser!

To active debug mode, stop the application and set the following environment variable.

```
(venv) $ export FLASK_DEBUG=1
```

The debugger allows you to expand each stack frame and see the corresponding source code. You can also open a Python prompt and execute valid Python expressions, e.g. to check the value of variables! (prety cool)

Never run a Flask application in debug mode on a production server. The debuggers allows a user to remotely execute code in the server.

Fun fact, debug mode has a nice feature called the `reloader`. It automatically restarts the application when a source file is modified. If you `flask run` while in debug mode you can then work on your application and any time you save a file, the application will restart to pick up the new code.

## Custom Error Pages

Let's define some custom error pages so users don't have to see the plain boring default ones - starting with 500 and 404.

```python
from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
```

Error functions are similar to view functions. In the above code we are returning the values of their respective templates. The functions also return a second number, which is the error code number.

We haven't returned a second number for all other view functions because the default (successful response) value is 200.

## Sending Errors by Email

Right now, as we are developing, errors are printed to the terminal, but once we deploy to a production server, no one is going to be looking at the output of the server, so we need to be notified if something breaks.

Let's configure flask to email us immediately after an error, with the stack trace of the error in the email body.

First step, add email server details to the configuration file.

```python
# config.py: Email configuration

class Config:
    # ...
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
```

Flask uses Python's `logging` package to write its logs, and this package has the ability to send logs by email. We just need to add a `SMTPHandler` instance to the Flask logger object, which is `app.logger`.

```python
# app/__init__.py: Log errors by email

import logging
from logging.handlers import SMTPHandler

# ...

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

from app import routes, models, errors
```

The code above is a bit tedious, but the main point is we are creating a `SMTPHandler` instance, and sets its level so that it only reports errors and not warnings, information or debugging messages, and finally attached it to the `app.logger` object from Flask.


> How can we test this feature?

Two ways. Easiest is to use an SMTP debugging server. This is a fake email server that accepts emails, but instead of sending them, prints them to console. Run this server by opening a second terminal session, activate virtual environment, and install the `aiosmtpd` package.

In a new terminal, run
```bash
(venv) $ pip install aiosmtpd
(venv) $ aiosmtpd -n -c aiosmtpd.handlers.Debugging -l localhost:8025
```
In the original terminal, run
```bash
export MAIL_SERVER=localhost
export MAIL_PORT=8025
```

## Logging to a File

Email is nice, but logging to a file is more scalable and robust.

We will use `RotatingFileHandler` which will attach to the application logger.

```python
# app/__init__.py: Logging to a file

# ...
from logging.handlers import RotatingFileHandler
import os

# ...

if not app.debug:
    # ...

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
```

We write to `logs/microbog.log` file. We create the directory if it does not already exist.

The `logging.Formatter` class provides custome formatting for log messages. They're going in a file, so we want as much relevant information as possible (timestamp, logging level, message, source file, line number)

We are lowering the logging level to the `INFO` category, both in the application logger and the file logger handler. In case you're not familiar with the logging categories, they are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAl` in increasing order of severity.

## Fixing the Duplicate Username Bug

Let's fix the bug.

Previously in `RegistrationForm` we implement validation for usernames, but the requirements for the `EditProfileForm` are slightly different.

During registration, we make sure the username does not already exist in the database.

During edit profile, we do the same check (user not in db) but there is one exception. If the user leaves the original username untouched, validation should allow it, since that username is already assigned to that user.

```python
app/forms.py: Validate username in edit profile form.

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
```

The validation implementation is in a custom validation method, but there is an overloaded constructor that accepts the original username as an argument. This username is saved as an instance variable, and checked in the `validate_username()` method. If the username entered in the form is the same as the original username, then there is no reason to check the database for duplicates.

To use this new validation method, we need to add the original username argument in the view function, where the form object is created:

```python
app/routes.py: Validate username in edit profile form.

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    # ...
```

This should fix the bug in the majority of cases. One exception is when two or more processes are accessing the database at the same time. In this situation, a race condition could cause the validation to pass, but a moment later when the rename is attempted the database was already changed by another process and cannot rename the user. This is mostly unlikely unless for very busy applications that have a lot of server processes, so we will let this slide for now.

## Enabling Debug Mode Permanently

Debug mode is useful in development, we can have it on permanently by adding the `FLASK_DEBUG` environment variable to the `.flaskenv` file.

```python
.flaskenv: Environment variables for flask command

FLASK_APP=microblog.py
FLASK_DEBUG=1
```