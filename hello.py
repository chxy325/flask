#-*-coding:utf-8-*-

from flask import Flask
from flask.ext.bootstrap import Bootstrap

import os

app = Flask(__name__)

@app.route('/')
def index():
	return '<h1>Hello World!!!</h1>'

@app.route('/user/<name>')
def user(name):
	return '<h1>Hello %s!!!</h1>' % name

bootstrap = Bootstrap(app)

if __name__ == '__main__':
    app.run(debug=True)