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
	if not session.get('rule'):
		session['rule'] = -1
	data = query_db('SELECT * FROM rules ORDER BY id desc')
	rule = choice(data)
	while session['rule'] == rule['id']:
		rule = choice(data)
	session['rule'] = rule['id']
	return render_template('index.html', rule=rule)

@app.route('/<id>')
def permalink(id):
	rule = query_db('SELECT * FROM rules WHERE id = ?', id, True)
	return render_template('index.html', rule=rule)


@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		if (request.form['username'] == app.config['DANIEL_USER'] and request.form['password'] == app.config['DANIEL_PW']) or (request.form['username'] == app.config['MAX_USER'] and request.form['password'] == app.config['MAX_PW']):
			session['logged_in'] = True
			return redirect(url_for('admin'))
	else:
		return render_template('login.html')

@app.route('/admin')
def admin():
	if not session['logged_in']:
		abort(401)
	rules = query_db('SELECT * FROM rules ORDER BY id asc')
	return render_template('admin.html', rules=rules)

@app.route('/add', methods=['POST'])
def add():
	if not session['logged_in']:
		abort(401)
	rule = request.form['rule']
	other_rules = query_db('SELECT rule from rules')
	if rule:
		g.db.execute('INSERT INTO rules (rule) values (?)', [rule])
		g.db.commit()
	return redirect(url_for('admin'))

@app.route('/delete/<id>')
def delete(id):
	if not session['logged_in']:
		abort(401)
	if id:
		g.db.execute('DELETE FROM rules WHERE id = ?', [id])
		g.db.commit()
	return redirect(url_for('admin'))
