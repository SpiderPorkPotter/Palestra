"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from Palestra import app

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'home.html',
        title='Home Page'
    )

@app.route('/calendario')
def calendario():
    return render_template(
        'calendario.html',
        title='calendario'
    )

@app.route('/corsi')
def corsi():
    return render_template(
        'corsi.html',
        title='corsi'
    )

@app.route('/istruttori')
def istruttori():
    return render_template(
        'istruttori.html',
        title='istruttori'
    )

@app.route('/login')
def login():
    return render_template(
        'login.html',
        title='login'
    )

@app.route('/profilo')
def profilo():
    """Renders the contact page."""
    return render_template(
        'profilo.html',
        title='profilo'
    )



