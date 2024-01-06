## Chapter 3
## 2023-12-28

### Web Forms
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

How do we accept input from users? Enter, web forms.

We will use the **Flask-WTF** extension.

```commandline
(venv) $ pip install flask-wtf
```

So far, this simple application has not needed to concern itself with **configuration**. Flask applications allow some freedom with which how to do things, and we will have to make some decisions, which we pass to the framework as a list of configuration variables. 

The simplest solution is to define configuration variables as keys in `app.config`, e.g.

```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
# ... add more variables here as needed
```
While the above would work, implementing a _separation of concerns_ and using a separate python class to store these variables keeps the application more organized. Something like this (top level directory):

```python
config.py: Secret key configuration

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
```

Now, we can update our flask application to reference this new `Config` class

This configuration is relevant to Web Forms because the `SECRET_KEY` configuration variable is an important part of Flask applications. Flask and some of its extensions use the value of the secret key as a cryptographic key, useful to generate signatures or tokens. Flask-WTF extension also sues it to prevent CRSF attacks.

#### User Login Form

The Flask-WTF extension uses Python classes to represent web forms.

We create `app/forms.py`.

```python
app/forms.py: Login form

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
```

#### Form Templates

Next, we add the form to an HTML template so it can be rendered on a web page.

```html
app/templates/login.html: Login form template

{% extends "base.html" %}

{% block content %}
    <h1>Sign In</h1>
    <form action="" method="post" novalidate>
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

We can see `app/templates/login.html` expects a `form` object instantiated from the `LoginForm` class we defined in` app/forms.py`. We will define this in a new login view function (in `routes.py`) later.

We use the HTML `<form></form>` element as a container for our web form. What do each of the attributes represent? (`<form action="" method="post" novalidate>`)
- The `action` attribute of the form is used to tell the browser what URL should be used when submitting the information entered in the form. When set to a blank string, `""`, this means to submit the form to the current URL in the address bar, e.g. the URL that rendered the form on the page.
- The `method` attribute specifies the HTTP request method that should be used when submitting the form to the server. The default is to send a `GET` request, but a `POST` request makes for a much better user experience because requests of `POST` type can submit the form data in the **body** of the request rather than the `GET` requests which add the form fields to the URL, cluttering the browser address bar.
- The `novalidate` attribute tells the browser to not apply any validation to the fields in this form, effectively leaving this task up to the Flask application running on the server. Using `novalidate` is completely optional, but for this first form it is important to set it because this will allow you to test server side validation later.

What does `{{ form.hidden_tag() }}` mean?

- This template argument creates a hidden field that includes a token used to protect your application from CRSF attacks. We can protect this form by including this hidden field and having the `SECRET_KEY` variable defined in the Flask configuration. Flask-WTF takes care of the rest. 

### Form Views

The last step to view the form in the browser is to write a new view function in the application that renders the template from the previous section.

```python
...
from app.forms import LoginForm
...
@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)
```

We import `LoginForm` from `forms.py`, instantiate an object from it, and send it down to the template `login.html`.

#### Receiving Form Data

- If we try to login currently, we get a "Method Not Allowed" page. Why do we receive this and how do we fix it? 
   - We get this error because the browser is submitting a `POST` request to the application, but it is not configured to accept it. 
   - The login view function we implemented so far only does half the job. It can render the login page and take input, but it does not have logic implemented to process the input.
 
```python
app/routes.py: Receiving login credentials

from flask import render_template, flash, redirect

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)
```
- We add `method=['GET', 'POST'])` to the route decorator to allow the view function to accept `POST` requests. By default, it only accepts `GET` requests. 
- HTTP protocol states `GET` requests are those that return information to the client (web browser in this case). And `POST` requests are those where the browser sends information to the server.
- `form.validate_on_submit()`: this handles validation of `form` data, if everything is okay, it will return `True`, indicating the data is valid and can be processed by the application. If validation fails, it will return `False`. We will add an error message later.
- `flash()`: useful way to show message to the user whether an action is successful or not
- `redirect()`: function that instructs the client web browser to automatically navigate to a different specified page. We redirect to the `/index` page in this case.
- Of note, when we call `flash()`, `Flask` stores the message, but the flashed messages don't magically appear. We need to update our base template

```html
app/templates/base.html: Flashed messages in base template

<html>
    <head>
        {% if title %}
        <title>{{ title }} - microblog</title>
        {% else %}
        <title>microblog</title>
        {% endif %}
    </head>
    <body>
        <div>
            Microblog:
            <a href="/index">Home</a>
            <a href="/login">Login</a>
        </div>
        <hr>
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <ul>
            {% for message in messages %}
            <li>{{ message }}</li>
            {% endfor %}
        </ul>
        {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </body>
</html>
```
- `get_flashed_messages()`: Flask function that returns all flashed messages registered with `flask()` previously. This isn't the best styling, but updating that will come later.
- Of note, the requested messages are "ephemeral". Once they are requested via `get_flashed_messages()` they are removed from the messages list, so they only appear once after the `flash()` function is called.

#### Improving Form Validation

- Currently, if users submit invalid data they don't get any feedback on the error. We can render this. The form validators already have descriptive error messages, we just need to add some additional logic to the template (`login.html`) to render them.
```html
app/templates/login.html: Validation errors in login form template

{% extends "base.html" %}

{% block content %}
    <h1>Sign In</h1>
    <form action="" method="post" novalidate>
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}<br>
            {% for error in form.username.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.password.label }}<br>
            {{ form.password(size=32) }}<br>
            {% for error in form.password.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.remember_me() }} {{ form.remember_me.label }}</p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

- We add two for loops, one for `username` and one for `password` to show the error message(s) in red.

**Generating Links**

- We have links in our application currently, but they are hardcoded. If we want to change/reorganize the links one day, we will have to find and replace all of them. e.g.

```html
<div>
    Microblog:
    <a href="/index">Home</a>
    <a href="/login">Login</a>
</div>
```
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # ...
        return redirect('/index')
    # ...
```
- To improve control over these links, we can use the `url_for()` function provided by Flask. This function generates URLs based on the internal mapping of URLs to view functions. The argument to `url_for()` is the endpoint name, which is the name of the function.
- This is better because URLs change more often than view function names. Another reason is some URLs may have dynamic components in them. The `url_for()` function can generate these automatically instead of having to handle them by hand.
- Updated:
```html
app/templates/base.html: Use url_for() function for links

<div>
    Microblog:
    <a href="{{ url_for('index') }}">Home</a>
    <a href="{{ url_for('login') }}">Login</a>
</div>
```
```python
app/routes.py: Use url_for() function for links

from flask import render_template, flash, redirect, url_for

# ...

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # ...
        return redirect(url_for('index'))
    # ...
```