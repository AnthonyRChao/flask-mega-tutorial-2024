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

**Requiring Users To Login**

**Showing The Logged-In User in Templates** 

**User Registration**