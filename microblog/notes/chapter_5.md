## Chapter 5
## 2024-01-05

### User Logins 
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins

#### Password Hashing

In our `User` class we have a field `password_hash` which represents the hashed version of a user's password.

For our application we use Werkzeug - an example of how to hash a password

```python
>>> from werkzeug.security import generate_password_hash
>>> hash = generate_password_hash('foobar')
>>> hash
'scrypt:32768:8:1$DdbIPADqKg2nniws$4ab051ebb6767a...'
```

We transform the password, `foobar`, into a long unique encoded string via a series of cryptographic operations that have no known reverse operation. Even if someone has the hashed password, they won't be able to recover the original password.

Of note, even if two users share the same password, the hash function will return different results, since all hashed passwords get a different cryptographic _salt_. 

You can verify passwords as follows:

```python
>>> from werkzeug.security import check_password_hash
>>> check_password_hash(hash, 'foobar')
True
>>> check_password_hash(hash, 'barfoo')
False
```
And now, we add the password hashing logic to our `User` model as follows:
```python
# app/models.py: Password hashing and verification

from werkzeug.security import generate_password_hash, check_password_hash

# ...

class User(db.Model):
    # ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```
In action
```python
>>> u = User(username='susan', email='susan@example.com')
>>> u.set_password('mypassword')
>>> u.check_password('anotherpassword')
False
>>> u.check_password('mypassword')
True
```

#### Introduction to Flask-Login

What is this extension for? Flask-Login is used to help managed login state for an application. e.g. users navigating to different pages while staying logged in. providing the "remember me" functionality that allows users to remain logged in even after closing the browser window.

Install into virtual environment.

```commandline
(venv) $ pip install flask-login
```

Similar to other extensions, after installing, make sure to create and initialize after the app initialization in `app/__init__.py`.

```python
# app/__init__.py: Flask-Login initialization

# ...
from flask_login import LoginManager

app = Flask(__name__)
# ...
login = LoginManager(app)

# ...
```

#### Preparing The User Model for Flask-Login

Flask-Login works with our applications user model as long as certain properties and methods are implemented, four specifically.

- `is_authenticated`: a property that is `True` if the user has valid credentials, and `False` if otherwise
- `is_active`: a property that is `True` if the user is active, and `False` if otherwise
- `is_anonymous`: a property that is `False` for regular users, and `True` only for a special, anonymous user
- `get_id()`: a method that returns a unique identifier for the user as a string

While we can implement these properties/methods, Flask-Login provides a _mixin_ class, `UserMixin`, that includes safe implementations appropriate for most user model classes. We add this mixin class to our user model.

```python
# app/models.py: Flask-Login user mixin class

# ...
from flask_login import UserMixin

class User(UserMixin, db.Model):
    # ...
```
#### User Loader Function

Q: How does Flask-Login keep track of logged-in users?

A: Flask-Login stores the logged-in user's unique identifier in Flask's _user session_, a storage space assigned to each user who connects to the application. Every time a logged-in user navigates to a new page, Flask-Login retrieves the ID of the user from the session, then loads that user into memory.

Flask-Login knows nothing about databases, so it needs the application's help in loading a user. For this reason, the extension expects the application to configure a **user loader function**, that can be called to load a user given the ID. We add this function to the `app/models.py` module.

```python
app/models.py: Flask-Login user loader function

from app import login
# ...

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
```

**Logging Users In**

Let's take another look at our `login` view function in `routes.py`. Currently, we have a "fake login" and just `flash()` to the user. But now our application has access to a user database and knows how to generate/verify password hashes, so we can complete this view.

```python
app/routes.py: Login view function logic

# ...
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import db
from app.models import User

# ...

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
```

**Logging Users Out**

Flask-Login provides a `logout_user()` function to allow users to log out. Let's add a new logout view function.

```python
# app/routes.py: Logout view function

# ...
from flask_login import logout_user

# ...

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
```

And now we expose this new link to users. Let's make the "Login" link in the navigation bar change to "Log Out" after a user logs in.

```html
app/templates/base.html: Conditional login and logout links

        <div>
            Microblog:
            <a href="{{ url_for('index') }}">Home</a>
            {% if current_user.is_anonymous %}
            <a href="{{ url_for('login') }}">Login</a>
            {% else %}
            <a href="{{ url_for('logout') }}">Logout</a>
            {% endif %}
        </div>
```

Q: How does the `base.html` template know what `current_user.is_anonymous` is?

A: The `is_anonymous` property is one of the attributes that Flask-Login adds to user objects through the `UserMixin` class.

**Requiring Users To Login**

Flask-Login provides a useful feature that forces users to log in before they can view certain pages of the application. If a user who is not logged in tries to view a protected page, Flask-Login will automatically redirect the user to the login form.

For this to work, Flask-Login needs to know what is the view function that handles logins. This can be added in `app/__init__.py`.

```python
# ...
login = LoginManager(app)
login.login_view = 'login'
```

Flask-Login implements this feature with a decorator `@login_required`. When you add this decorator to a view function, the function becomes protected and won't allow users to access that are not authenticated. e.g.

```python
# app/routes.py: @login_required decorator

from flask_login import login_required

@app.route('/')
@app.route('/index')
@login_required
def index():
    # ...
```

Now, we want to implement the redirect back from the successful login to the page the user wanted to access.

Key: when a user that isn't logged in accesses a view function protected by the `@login_required` decorator, the decorator is going to redirect to the login page, but it is going to include some **extra information** in this redirect so the application can return to the user to the original page.

For example, if the user navigates to `/index` the `@login_required` decorator will intercept the request and respond with a redirect to `login` but it will add a query string argument to this URL, making the complete redirect url `/login?next=/index`. The `next` query string argument is set to the original URL, so the application can use that to redirect back after login.

Something like:

```commandline
127.0.0.1 - - [05/Jan/2024 15:15:29] "GET /logout HTTP/1.1" 302 -
127.0.0.1 - - [05/Jan/2024 15:15:29] "GET /index HTTP/1.1" 302 -
127.0.0.1 - - [05/Jan/2024 15:15:29] "GET /login?next=/index HTTP/1.1" 200 -
```

We want to read and process the `next` query string argument. Here are changes in the `login_user()` call.

```python
# app/routes.py: Redirect to \"next\" page

from flask import request
from urllib.parse import urlsplit

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ...
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    # ...
```

After user is logged in by calling Flask-Login's `login_user()` function, we extract the value of `next` query string argument by using Flask's provided `request` variable.

`request`: variable that contains all information that the client sent with the request.
`request.args`: attribute exposes the content of the query string as a dictionary

We then address three specific cases to determine where to redirect to after a successful login.

1. If the login URL does not have a `next` argument, redirect to `index` page
2. If the login URL has a `next` argument that is set to a **relative path** redirect user to that URL (e.g. 'index')
3. If the login URL has a `next` argument that is set to a full URL that includes a domain name, ignore this URL, and redirect user to `index` page.

The first two cases are self-explanatory. The third case makes the application more secure. An attacker could insert a URL to a malicious site in the `next` argument, so our application only redirects when a URL is **relative**, which ensures that the redirect stays within the same site as the application.

We determine if a URL is relative or absolute by parsing it with Python's `urlsplit()` function and then check if the `netloc` component is set or not.

**Showing The Logged-In User in Templates** 

We previously used a fake user to help design the home page of the application before the user subsystem was in place. The application has real users now, so we will update to support working with real users.

```html
app/templates/index.html: Pass current user to template

{% extends "base.html" %}

{% block content %}
    <h1>Hi, {{ current_user.username }}!</h1>
    {% for post in posts %}
    <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
    {% endfor %}
{% endblock %}
```

```python
# app/routes.py: Do not pass user to template anymore

@app.route('/')
@app.route('/index')
@login_required
def index():
    # ...
    return render_template("index.html", title='Home Page', posts=posts)
```

**User Registration**

Now, let's build a registration for so users can register. Start with a web form class in `app/forms.py`

```python
# app/forms.py: User registration form

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User

# ...

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
```

For the validation queries, these queries should never find more than one result so instead of running with `db.session.scalars()`, we use `db.session.scalar()` which returns `None` if there are no results, or else the first result.

To display this form on a web page, we need an HTML template, `app/templates/register.html`

```html
app/templates/register.html: Registration template

{% extends "base.html" %}

{% block content %}
    <h1>Register</h1>
    <form action="" method="post">
        {{ form.hidden_tag() }}
        <p>
            {{ form.username.label }}<br>
            {{ form.username(size=32) }}<br>
            {% for error in form.username.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>
            {{ form.email.label }}<br>
            {{ form.email(size=64) }}<br>
            {% for error in form.email.errors %}
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
        <p>
            {{ form.password2.label }}<br>
            {{ form.password2(size=32) }}<br>
            {% for error in form.password2.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </p>
        <p>{{ form.submit() }}</p>
    </form>
{% endblock %}
```

Login Form template needs a link to send users to the registration form, below the form

```html
app/templates/login.html: Link to registration page

    <p>New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
```

Add new register view function to ahndle user registrations in `app/routes.py`.

```python
app/routes.py: User registration view function

from app import db
from app.forms import RegistrationForm

# ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
```
