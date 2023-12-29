## Chapter 2
## 2023-12-28

### Templates
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates

What is one technique you can use to concentrate on one part of your application without having to worry about other parts of the system that may not exist yet?

- Create mock objects!

```python
user = {'username': 'Miguel'}
```

Why is updating `index()` as follows a non-scale friendly solution?

```python
@app.route('/')
@app.route('/index')
def index():
	user = {'username': 'Miguel'}
	return """
	<html>
		<head>
			<title>Home Page - Microblog</title>
		</head>
		<body>
			<h1>Hello, """ + user['username'] + """!</h1>
		</body>
	</html>
	"""
```

- New functionality would be hard to support, e.g. blog posts (which constantly change), or blog posts from multiple users
- More view functions associated with different URLs
- A change to the application layout would require updating all HTML in every view function, not ideal

Ideally, **the application logic should be separate from the layout/presentation** of your web pages. (e.g. you could hire a web designer to build the UI while you code the application logic)

**Templates** help achieve this separation between application logic and presentation.

- The operation of converting a template into a complete HTML page is called _rendering_, via the function provided by the Flask framework `render_template()`
- Of note, the `render_template()` function invokes the **Jinja** template engine that comes bundled with the Flask framework. Jinja substitutes `{{ ... }}` blocks with the corresponding values given by the arguments provided in the `render_template()` call.

**Conditional Statements**
- Jinja supports control statements inside `{% ... %}` blocks, e.g.
```html
    ...
    <head>
        {% if title %}
        <title>{{ title }} - Microblog</title>
        {% else %}
        <title>Welcome to Microblog!</title>
        {% endif %}
    </head>
    ...
```
**Loops**
- A list of `posts` can have any number of elements, it is up to the view function (`index()`) to decide how many posts are going to be presented in the page. For this problem, Jinja offers a `for` control structure.

```python

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in California!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Barbie movie was so cool!'
        },
        {
            'author': {'username': 'Tony'},
            'body': 'God, I love coffee!'
        }
    ]
    return render_template(
        'index.html',
        title='Home',
        user=user,
        posts=posts
    )
```
```html
    ...
    <body>
        <h1>Hi, {{ user.username }}!</h1>
        {% for post in posts %}
        <div><p>{{ post.author.username }} says: <b>{{ post.body }}</b></p></div>
        {% endfor %}
    </body>
    ...
```

**Template Inheritance**

- Almost all websites today have a navigation bar that appears on all pages of the application. While we could add a navigation bar with some HTML, as the application grows we would need to add this same bar to other pages. Ideally, we don't need to maintain several copies of the navigation bar.
- Jinja has a feature which specifically addresses this problem. Essentially, it involves moving all parts of the page layout that are common to all templates to a base template (e.g. `base.html`), from which all other templates are derived.