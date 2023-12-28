## 2023-12-27

To install a package on your machine, you use pip as follows:
  
`$ pip install <package-name>`

> Interestingly, this method of installing packages will not work in most cases. If your Python interpreter was installed globally for all the users of your computer, chances are your regular user account is not going to have permission to make modifications to it, so the only way to make the command above work is to run it from an administrator account. But even without that complication, consider what happens when you install a package in this way. The pip tool is going to download the package from PyPI, and then add it to your Python installation. From that point on, every Python script that you have on your system will have access to this package.

What happens when you use `pip install <package-name>`?

- The pip tool is going to **download the package from PyPI**, then add it to your Python installation. From here, every Python script on your system will have access to this package.

What is PyPI?

- Python Package Index, the official Python package repository.

Why are virtual environments necessary?

- What happens if you have two web applications, one you built first with version 2 of Flask, the second you built after with version 3 of Flask. Once you upgrade your system Flask version from 2 to 3, your first application breaks. There should be a way to have both versions on your machine so that both your applications can run different versions of Flask.
- Python addresses this issue of **maintaining different versions of packages for different applications** with the concept of virtual environments.

What is a virtual environment?

- A virtual environment is a **complete copy of the Python interpreter**. When you install packages in a virtual environment, the system-wide Python interpreter is not affected.
- You solve the problem of needing to have different versions of packages for different projects by having a virtual environment for each project.
- Virtual environments are also owned by the user who created them, so they do not require an administrator account

How do you make a virtual environment?

- `python3` comes with support for virtual environments built in, e.g. the following creates a virtual environment named `venv` in the corresponding project directory

```
python3 -m venv venv
```

- Of note, it's common to create virtual environments with the name `venv` in the project directory so whenever one `cd`s into the project one can find its corresponding virtual environment easily.

What happens when you activate your virtual environment?

- When you activate a virtual environment, the configuration of your terminal session is modified so that the Python interpreter stored inside it is the one invoked when you type `python`

Why do some directories have a `__init__.py` file?

- In Python, a subdirectory that includes a `__init__.py` file is considered a package, and can be imported.
- When you import a package, the `__init__.py` executes and defines what symbols the package exposes to the outside world.

Explain what is going on in this `__init__.py` file.

```python
# app/__init__.py

from flask import Flask

app = Flask(__name__)

from app import routes
```

- The script above creates the application object as an instance of class `Flask` imported from the flask package.
- The `__name__` variable passed to the `Flask` class is a Python predefined variable, which is set to the name of the module in which it is used. Flask uses the location of the module passed here as a starting point when it needs to load associated resources, such as template files.
- There are two entities named `app`. (1) `app` is defined as a `Flask` class instance, then (2) we import `routes` from `app`. This feels strange doesn't it? Almost ... circular. The `routes` module is imported at the bottom and not the top (as it normally is done), because it is a well known workaround that avoids *circular imports*.

What are routes for?

- Routes handle the different URLs the application supports.
- In Flask, handlers for the application routes are written as Python functions, called *view functions*. View functions are mapped to one or more route URLs so that Flask knows what logic to execute when a client requests a given URL.

What do decorators do?

- A decorator modifies the function that follows it. A common pattern with decorators is to use them to register functions as callbacks for certain events.
- What does "register functions as callbacks for certain events" mean?
	- This refers to the practice of **associating specific functions (callbacks) with particular events** in a program.
	- **Callback Functions**: these are functions that are defined to be called when a specific event occurs. Instead of being explicitly called in your code, they are "called back" or invoked automatically when the associated event takes place.
	- **Events**: these are occurrences within a program that can be detected and responded to. Examples include button clicks, mouse movements, keypresses, data changes, and other changes in program's state.
	- **Registration**: "registering" a function as a callback for a particular event means to associate that function with the event. This is often done using a mechanism provided by a framework, language, or language feature.
	- **Decorator Pattern**: Decorators in Python are a way to modify or extend the behavior of functions or method. In the context of events and callbacks, decorators can be used to associate a function with a specific event by modifying or extending its behavior.

Simple example to demonstrate concept

```python
# Decorator to register a function as a callback for an event
def event_handler(callback_func):
	def wrapper(*args, **kwargs):
		# Perform some pre-event actions if needed
		print("Before event")
		# Call the actual callback function
		result = callback_func(*args, **kwargs)
		# Perform some post-event actions if needed
		print("After event")
		return result
	return wrapper

# Using the decorator to register a function as a callback
@event_handler
def on_button_click():
	print("Button clicked")

# Simulating a button click event
on_button_click()
```

Another example - in this case, the `@app.route` decorator creates an association between the URL given as an argument and the function. When a web browser requests either of these two URLs, Flask is going to invoke this function and pass its return value back to the browser as a response.

```python
# app/routes.py

from app import app

@app.route('/')
@app.route('/index')
def index():
	return "Hello, World!"
```

What's the difference between the two `app`s?

```python
# microblog.py

from app import app
```

- The first `app` refers to the module, the second `app` refers to variable in the `app` module.

What does `flask run` do?

- The command looks for a Flask application instance in the module referenced by the `FLASK_APP` environment variable, which in this case is *microblog.py*. The command sets up a web server that is configured to forward requests to this application.

Are environment variables remembered across terminal sessions?

- They are not. To avoid having to type `FLASK_APP=microblog.py` every time you open a new terminal window, you can make use of `python-dotenv` and the `.flaskenv` file.
```python
(venv) $ pip install python-dotenv

# .flaskenv

FLASK_APP=microblog.py
```

- The `flask` command will look for the *.flaskenv* file and import all the variables defined in it exactly as if they were defined in the environment