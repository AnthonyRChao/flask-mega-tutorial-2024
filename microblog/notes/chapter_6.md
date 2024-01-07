## Chapter 6
## 2024-01-06

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
#### Using Jinja Sub-Templates
#### More Interesting Profiles
#### Recording The Last Visit Time For a User
#### Profile Editor
