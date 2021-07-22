"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FormField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Email, Length
from sqlalchemy import create_engine
from Palestra import app
from .models import Persone
from werkzeug.security import generate_password_hash, check_password_hash

#psycopg2 è il driver che si usaper comunicare col database
DB_URI = "postgresql+psycopg2://postgres:a@localhost/Palestra"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'

db = SQLAlchemy(app)

engine = create_engine(DB_URI)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#da verificare se id è corretto
@login_manager.user_loader
def user_loader(id):
    return Persone.query.get(id)


class LoginForm(FlaskForm):
    email = StringField('Email', validators = [InputRequired(), Email(message = 'Email non valida'), Length(max = 50)])
    password = PasswordField('Password', validators = [InputRequired(), Length(min = 8, max = 50)])

class RegistrazioneForm(FlaskForm):
    codice_fiscale = StringField('Codice fiscale', validators = [InputRequired(), Length(min = 11, max = 16)])
    nome = StringField('Nome', validators = [InputRequired(), Length(min = 3, max = 50)])
    cognome = StringField('Cognome', validators = [InputRequired(), Length(min = 3, max = 50)])
    #probabilmente questo campo è inutile
    #data = DateTimeLocalField('seleziona la data di oggi', format = '%d/%m/y', validators = InputRequired())
    telefono = IntegerField('Telefono', validators = [InputRequired(), Length(min = 9, max = 11)])
    email = StringField('Email', validators = [InputRequired(), Email(message = 'Email non valida'), Length(max = 50)])
    password = PasswordField('Password', validators = [InputRequired(), Length(min = 8, max = 50)])
    #mettiamo il conferma password? Boh, intanto c'è, poi al massimo lo eliminiamo
    #chk_password = PasswordField('conferma password', validators = [InputRequired(), Length(min = 8, max = 50)])




@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'home.html',
        title='Home Page'
    )


@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        utente = Persone.query.filter_by(email = form.email.data).first()
        if utente:
            if check_password_hash(Persone.passwd, form.password.data):
                login_user(utente)
                return redirect(url_for('profilo'))

        return '<h1> email o password sbagliati'
        

    return render_template('login.html', form = form)


@app.route('/registrazione', methods = ['GET','POST'])
def registrazione():
    form = RegistrazioneForm()

    if form.validate_on_submit():
        #mettere sha256 alzando a 80 il n° max di caratteri nella tabella, perché sha256 genera 80 caratteri
        hashed_passwd = generategenerate_password_hash(form.password.data, method='sha128')
        nuovo_utente = Persone(codice_fiscale = form.codice_fiscale.data,
                               nome = form.nome.data,
                               cognome = form.cognome.data,
                          #    data = form.data.data,
                               telefono = form.telefono.data,
                               email = form.email.data, 
                               password = hashed_passwd,
                          #     chk_password = form.chk_password.data,)
                               )

        db.session.add(nuovo_utente)
        db.session.commit()

        return '<h1> È stato inserito un nuovo utente'

    #hash della password

    return render_template('registrazione.html', title = 'registrazione', form = form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')

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

@app.route('/profilo')
def profilo():
    """Renders the contact page."""
    return render_template(
        'profilo.html',
        title='profilo'
    )


@app.route('/creazionePalestra')
def creazionePalestra():
    """pagina della creazione della palestra"""
    return render_template(
        'creazionePalestra.html',
        title='Crea La Palestra'
    )


