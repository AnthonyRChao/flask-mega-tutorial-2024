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

**User Login Form**

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

**Form Templates**

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

**Form Views**

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
**Receiving Form Data**

**Improving Form Validation**

**Generating Links**