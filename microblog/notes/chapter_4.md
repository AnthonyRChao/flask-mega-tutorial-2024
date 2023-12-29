## Chapter 4
## 2023-12-29

### Database
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

For the vast majority of applications, we will need to persist and retrieve data - so we need a database.

**Databases in Flask**

- Of note, Flask doesn't support databases natively. This is by design, to allow the user to choose a database that best fits their needs rather than being forced to adapt to one.
- Databases generally separate into two categories: relational and non-relational (often referenced as NoSQL).
- Structured data (users, blogs, posts, etc.) generally fits well with relational databases, which we will move forward with.
- In the previous chapter we used a Flask extension, `flask-wtf` for working with web forms. In this chapter we will use two more: `Flask-SQLAlchemy` and `Flask-Migrate`
  - `Flask-SQLAlchemy`: Flask friendly wrapper to the popular SQLAlchemy package, which is an ORM (Object Relational Mapper)
    - **ORMs allow applications to manage a database using high-level entities like classes, objects and methods instead of tables and SQL. An ORM exists to translate high-level operations into database commands**
    - The nice thing about SQLAlchemy is that it supports multiple database engines (e.g. MySQL, SQLite, PostgreSQL). This is nice because you can develop with something like a SQLite database (which doesn't need a server) then when it's time to deploy to production you can switch to a more robust database like MySQL or PostgreSQL without having to alter your application
    
**Database Migrations**

- `Flask-Migrate`: Flask wrapper for Alembic, a database migration framework for SQLAlchemy
- While setting up `Flask-Migrate` adds some overhead work, it is worth it for the ability to more easily make changes to your database in the future.

**Flask-SQLAlchemy Configuration**

- During development, we will use a SQLite database. The advantage here is that SQLite databases are a single file and don't need a database server running like MySQL & PostgreSQL do.
- Add new configuration item to `config.py`

```python
config.py: Flask-SQLAlchemy configuration

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
```
- Flask-SQLAlchemy takes the location of the application's database from the `SQLALCHEMY_DATABASE_URI` configuration variable. As we did with `SECRET_KEY` it is a good practice to set configuration from environment variables, and provide a fallback value when the environment does not define the variable.
- In the example above we are taking the database URL from either the `DATABASE_URL` environment variable, and if that isn't defined, we configure a database named `app.db` located in the main directory of the application, which is stored in the `basedir` variable.
- In the application, we will represent the database as a database instance. The database migration engine will also have an instance. We create these objects are creating the application in the `app/__init__.py` file.

```python
app/__init__.py: Flask-SQLAlchemy and Flask-Migrate initialization

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
```
We make three changes here (notice, there is a pattern here of how to work with Flask extensions)
- 1, we added a `db` object, which represents the database
- 2, we added a `migrate` object, which represents the database migration engine
- 3, we import a new module called `models`, this will define the structure of the database
 
**Database Models**

**Creating The Migration Repository**

**The First Database Migration**

**Database Upgrade and Downgrade Workflow**

**Database Relationships**

**Playing with the Database**

**Shell Context**

