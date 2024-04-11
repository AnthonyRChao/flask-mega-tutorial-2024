## Chapter 6
2024-01-06

### Profile Page and Avatars
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-vi-profile-page-and-avatars

#### User Profile Page

This chapter focuses on adding user profile pages to the application.

To start, add a `/user/<username` route to the application.

```python
# app/routes.py: User profile view function

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)
```

The `@app.route` we use for `user()` is a little different from the others, in that it has a dynamic component, `<username>`.

Flask-SQLAlchemy provides a function `db.first_or_404()` that works like `scalar()` except when there are no results, it automatically sends a **404 error** back to the client. The benefit of using this is we save ourselves needing to check if a user exists. As if they do not exist in the database, the function will not return and a 404 exception will be raised. Neat.

Now, let's implement the `user.html` template.

```html
app/templates/user.html User profile template

{% extends "base.html" %}

{% block content %}
    <h1>User: {{ user.username }}</h1>
    <hr>
    {% for post in posts %}
    <p>
        {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

Now, let's add a link to the navigation bar so users can check their own profile.

```html
app/templates/base.html: User profile template

<div>
    Microblog:
    <a href="{{ url_for('index') }}">Home</a>
    {% if current_user.is_anonymous %}
    <a href="{{ url_for('login') }}">Login</a>
    {% else %}
    <a href="{{ url_for('user', username=current_user.username) }}">Profile</a>
    <a href="{{ url_for('logout') }}">Logout</a>
    {% endif %}
</div>
```

The only change is we add a new **Profile** link where we use Flask-Login's `current_user` to generate the correct URL

#### Avatars

For Avatars, instead of having to store a large number of files for users, we will use the Gravatar service.

Here's an example of how we could get the Gravatar URL for a user with email: `john@example.com`

```python
>>> from hashlib import md5
>>> 'https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
```

Of note, the default image size returned is 80x80, but you can add an `s` argument to the URL's query string to request a different size, like 128x128.

```python
https://www.gravatar.com/avatar/729e26a2a2c7ff24a71958d4aa4e5f35?s=128
```

As avatars are associated with users, we add the logic to generate avatar URLs to the user model.

```python
app/models.py: User avatar URLs

from hashlib import md5
# ...

class User(UserMixin, db.Model):
    # ...
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
```

This new `avatar()` method of the `User` class will return the gravatar url for a user's avatar and if the user does not have an avatar registered, an "identicon" image will be generated.

- email to lower case: required by the Gravatar service to generate the MD5 hash
- utf-8: MD5 support in Python works on bytes and not on strings, so we encode the string as bytes before passing it to the hash function

Now, insert the avatar images in the user profile template

```html
app/templates/user.html: User avatar in template

{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
    <p>
    {{ post.author.username }} says: <b>{{ post.body }}</b>
    </p>
    {% endfor %}
{% endblock %}
```

And, we can also add avatars to user's posts on their user profile page to make the home page look nicer.

```html
app/templates/user.html: User avatars in posts

{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
    <table>
        <tr valign="top">
            <td><img src="{{ post.author.avatar(36) }}"></td>
            <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
        </tr>
    </table>
    {% endfor %}
{% endblock %}
```

#### Using Jinja Sub-Templates

So, we added avatars to the user profile page, now we want to add something similar to the index page.

We could copy/paste the portion of the template from the user page to the index page, but this isn't ideal because if we decided to make changes to the layout later, we'll have make the same update in two places.

Better to make a sub-template that just renders one post, then reference it from both the `user.html` and `index.html` templates.

Let's create `app/templates/_post.html`. The `_` prefix is just a naming convention to help use recognize which templates are sub-templates.

```html
app/templates/_post.html: Post sub-template

<table>
    <tr valign="top">
        <td><img src="{{ post.author.avatar(36) }}"></td>
        <td>{{ post.author.username }} says:<br>{{ post.body }}</td>
    </tr>
</table>
```

Now we can invoke this sub-template from the `user.html` template with Jinja's `include` statement.

```html
app/templates/user.html: User avatars in posts

{% extends "base.html" %}

{% block content %}
    <table>
        <tr valign="top">
            <td><img src="{{ user.avatar(128) }}"></td>
            <td><h1>User: {{ user.username }}</h1></td>
        </tr>
    </table>
    <hr>
    {% for post in posts %}
        {% include '_post.html' %}
    {% endfor %}
{% endblock %}
```

The index page of the application isn't fleshed out yet, we will wait on adding this functionality there for now.

#### More Interesting Profiles

Let's enhance our user profile page so users can add an "about me" section and a "last seen" so users can see when they last accessed the site and display it on their profile page. Kind of like with networthshare "last logged in".

Start with extending the `users` table with two new fields.

Added `about_me` and `last_seen` fields via new db migration.

"I hope you realize how useful it is to work with a migration framework. Any users that were in the database are still there, the migration framework surgically applies the changes in the migration script without destroying any data."

Add two new fields to user profile template.

#### Recording The Last Visit Time For a User

Write the current time on this field for a given user whenever that user sends a request to the server.

To do this, we can execute a bit of generic logic ahead of a request being dispatched to a view function. This is such a common task in web applications that Flask offers it as a native feature.

```python
# app/routes.py: Record time of last visit

from datetime import datetime, timezone

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
```

Adding this enables "Last seen on: ..." to show on User Profile pages.

#### Profile Editor

Introduce a way for users to enter information about themselves.

They should be able to change their username and about me sections.

Edits will involve updating:
- `app/forms.py`
- `app/templates/edit_profile.html`
- `app/templates/user.html`
- `app/routes.py`

```python
# app/forms.py: Profile editor form

from wtforms import TextAreaField
from wtforms.validators import Length

# ...

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
```