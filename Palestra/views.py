"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FormField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Email, Length
from sqlalchemy import create_engine
from Palestra import app
#from .modelsv2 import Persone, Palestre, Base
from .models import Persone, Palestre, t_palestre_persone, Base
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

#psycopg2 è il driver che si usa per comunicare col database

DB_URI = "postgresql+psycopg2://postgres:a@localhost/Palestra"
engine = create_engine(DB_URI)

#inizializza la libreria che gestisce i login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#funzione importante che serve affinché flask login tenga
#traccia dell'utente loggato, tramite il suo id di sessione
@login_manager.user_loader
def user_loader(id):
    return Persone.query.get(id)

#classe di wtforms che contiene il form di login
#scrivendo nell'html usando la sintassi di jinja2
#{{ form.email('class_='form-control') }} si otterrà
#come risultato il campo email da riempire. In pratica
#tu nella pagina html scrivi python, questo poi viene
#tradotto in html
class LoginForm(FlaskForm):
    email = StringField('Email', validators = [InputRequired(), Email(message = 'Email non valida'), Length(max = 50)])
    password = PasswordField('Password', validators = [InputRequired(), Length(min = 8, max = 50)])

#stessa cosa di quello sopra, ma per la registrazione
class RegistrazioneForm(FlaskForm):
    codice_fiscale = StringField('Codice fiscale', validators = [InputRequired(), Length(min = 11, max = 16)])
    nome = StringField('Nome', validators = [InputRequired(), Length(min = 3, max = 50)])
    cognome = StringField('Cognome', validators = [InputRequired(), Length(min = 3, max = 50)])
    #probabilmente questo campo è inutile
    #data = DateTimeLocalField('seleziona la data di oggi', format = '%d/%m/y', validators = InputRequired())
    telefono = IntegerField('Telefono', validators = [InputRequired()])
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
    #crea il form seguendo le istruzioni della classe login scritta sopra
    form = LoginForm()

    #se tutti i campi sono validati
    em = form.email.data
    pwd = form.password.data
    #controlla che ci sia una sola email corrispondente
    if form.validate_on_submit():
        utente = Persone.query.filter_by(email = em).first()
        #se c'è, allora controlla anche la password (salvata criptata)
        if utente is not None and utente.check_password(pwd):
            #se tutto va bene, effettua il login, aggiungendo l'utente
            #alla sessione e riportandolo alla schermata profilo
          #  if check_password_hash(Persone.password, form.password.data):
            login_user(utente)
            return redirect(url_for('profilo'))
        #else
        flash('Email o Password errati')
        return redirect('/profilo')
        

    return render_template('login.html', title = 'login', form = form)


@app.route('/registrazione', methods = ['GET','POST'])
def registrazione():
    #si basa sulla classe definita sopra
    form = RegistrazioneForm()

    if form.validate_on_submit():
        
        #prendo il contenuto del form di registrazione
        codiceFisc = form.codice_fiscale.data
        nom = form.nome.data
        cogn = form.cognome.data
        tel = form.telefono.data
        em = form.email.data
        passwd = form.password.data

        nuovo_utente = Persone(codice_fiscale = codiceFisc,
                               nome = nom,
                               cognome = cogn,
                               telefono = tel,
                               email = em 
                               )

        nuovo_utente.set_password(passwd)

        #guardare documentazione per session
        db.session.add(nuovo_utente)
        db.session.commit()

        flash('Registrazione completata')
        return redirect('/login')

    return render_template('registrazione.html', title = 'registrazione', form = form)


@login_required
@app.route('/profilo')
def profilo():

    id = Persone.get_id(current_user)
    user = Persone.query.filter_by(codice_fiscale = id).first()
    print(user)


    return render_template(
        'profilo.html',
        #user = Persone.query.filter_by(codice_fiscale = id).first(),
        #dati_richiesti = db.session.execute("SELECT p.email, p.nome, p.cognome, p.is_istruttore FROM Persone as p WHERE p.codice_fiscale = :id", {"id": current_user.get_id()}).first(),
        title = 'Il mio profilo'
        )


@login_required
@app.route('/logout')
def logout():
    #elimina dalla sessione l'utente attuale
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
        title='Corsi Disponibili'
    )


@app.route('/istruttori')
def istruttori():
    return render_template(
        'istruttori.html',
        title='istruttori'
    )


@app.route('/creazionePalestra')
def creazionePalestra():
    """pagina della creazione della palestra"""
    return render_template(
        'creazionePalestra.html',
        title='Crea La Palestra'
    )


