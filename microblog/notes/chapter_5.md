## Chapter 5
## 2024-01-05

### User Logins 
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins

**Password Hashing**

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

**Introduction to Flask-Login**

What is this extension for?

**Preparing The User Model for Flask-Login**

**User Loader Function**

**Logging Users In**

**Logging Users Out**

**Requiring Users To Login**

**Showing The Logged-In User in Templates** 

**User Registration**