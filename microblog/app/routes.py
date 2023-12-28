from app import app


@app.route('/')
@app.route('/index')
@app.route('/fun')
def index():
	return "Hello, World!"
