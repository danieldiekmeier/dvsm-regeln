# -*- coding: utf-8 -*-

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from contextlib import closing
from random import choice

# create our little application
app = Flask(__name__)
app.config.from_pyfile('../config.py')

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])
	query_db('PRAGMA foreign_keys = ON;')

def init_db():
	with closing(connect_db()) as db:
		db.commit()

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

@app.route('/')
def index():
	data = query_db('SELECT * FROM rules ORDER BY id desc')
	rule = choice(data)
	return render_template('index.html', rule=rule)