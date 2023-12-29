from flask import render_template
from app import app
from forms import LoginForm


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

@app.route('/login')
def login():
	form = LoginForm()
	return render_template('login.html', title='Sign In', form=form)