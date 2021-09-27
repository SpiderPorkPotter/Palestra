"""
Routes and views for the flask application.
"""

from datetime import datetime
from calendar import monthrange
from flask import render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm, form
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import text
from wtforms import StringField, PasswordField, IntegerField, FormField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Email, Length
from sqlalchemy import create_engine
from Palestra import app
from .models_finale import * 
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

#psycopg2 è il driver che si usa per comunicare col database

#DB_URI = "postgresql+psycopg2://postgres:passwordsupersegreta@localhost:5432/Palestra"
DB_URI = "postgresql+psycopg2://postgres:a@localhost:5432/Palestra"
engine = create_engine(DB_URI)

#inizializza la libreria che gestisce i login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#funzione importante che serve affinché flask login tenga
#traccia dell'utente loggato, tramite il suo id di sessione
#segue l'esempio che c'è qui: https://flask-login.readthedocs.io/en/latest/#your-user-class
@login_manager.user_loader
def user_loader(id_utente):
    return Persone.query.filter_by(codice_fiscale = id_utente).first()


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
    #la data dell'iscrizione la prendiamo al momento della registrazione    
    email = StringField('Email', validators = [InputRequired(), Email(message = 'Email non valida'), Length(max = 50)])
    password = PasswordField('Password', validators = [InputRequired(), Length(min = 8, max = 50)])
    #mettiamo il conferma password? Boh, intanto c'è, poi al massimo lo eliminiamo
    #chk_password = PasswordField('conferma password', validators = [InputRequired(), Length(min = 8, max = 50)])
    #le opzioni di contatto 
    telefono = StringField('Telefono', validators = [InputRequired(), Length(min = 9, max = 11)])
    telefonoFisso = StringField('Telefono fisso', validators = [Length(min = 9, max = 11)])
    residenza = StringField('Luogo di residenza', validators = [InputRequired()])
    citta = StringField('Città di residenza', validators = [InputRequired()])


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
    if request.method == 'POST':
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
    

    #if form.validate_on_submit():
    if request.method == 'POST':
        
        #prendo il contenuto del form di registrazione
        codiceFisc = form.codice_fiscale.data
        nom = form.nome.data
        cogn = form.cognome.data
        em = form.email.data
        passwd = form.password.data

        #per l'oggetto contatti
        tel = form.telefono.data
        telFisso = form.telefonoFisso.data
        resdz = form.residenza.data
        citt = form.citta.data

        #creo l'oggetto utente
        nuovo_utente = Persone(nome = nom,
                                cognome = cogn,
                                email = em ,
                                data_iscrizione = datetime.today(),
                                codice_fiscale = codiceFisc,
                               )
        nuovo_utente.set_password(passwd)

        info_nuovo_utente = InfoContatti(
                    cellulare = tel,
                    tel_fisso = telFisso,
                    residenza = resdz,
                    città = citt,
                    codice_fiscale = codiceFisc)
        ruoli_utente = Ruoli(is_iscritto = True,is_capo = False,is_istruttore = False, is_responsabile  =False, codice_fiscale = codiceFisc)
       
        db.session.add(nuovo_utente)
        db.session.commit()

        db.session.add(info_nuovo_utente)
        db.session.commit()
        db.session.add(ruoli_utente)
        db.session.commit()      

        flash('Registrazione completata')
        return redirect('/login')

    return render_template('registrazione.html', title = 'registrazione', form = form)

#per ora la commento
@login_required
@app.route('/profilo', methods = ['POST','GET'])
def profilo():

    ruolo = ""
    #prendo l'id dell'utente corrente e le sue info
    if current_user != None:
        id = Persone.get_id(current_user)

        dati_utente_corrente = Persone.query.filter_by(codice_fiscale = id).first()
        #se voglio il telefono devo fare un'altra query


        if 'modificavalori' in request.form and  request.form['modificavalori'] == "ModificaPermessi":
            cf_passato = request.form['id_passato']
            nome_radio_button = cf_passato + "_radio"
            v = request.form[nome_radio_button]
            print(v)
            if v == "istruttore":
                #query update da iscritto a istruttore dopo averla fatta levare l'isstruzione "pass"
                pass
            if v == "iscritto":
                #query update da istruttore passa a iscritto dopo averla fatta levare l'isstruzione "pass"
                pass

        #prendo gli id di tutti i capi
        s = text("SELECT codice_fiscale FROM ruoli r WHERE is_capo IS TRUE AND codice_fiscale=:id_c")
        with engine.connect() as conn:
            dati_capi = conn.execute(s,id_c=id)
            #creo una lista fatta da tutti gli id dei capi
            ids_capi=[]
            for d in dati_capi:
               ids_capi.append(d['codice_fiscale'])
            
            #se l'id è nella lista dei capi stampo tutti gli iscritti
            if id in ids_capi:

                s = text("SELECT p.codice_fiscale, p.nome, p.cognome, i.cellulare FROM ruoli r JOIN persone p ON p.codice_fiscale=r.codice_fiscale JOIN info_contatti i ON p.codice_fiscale=i.codice_fiscale WHERE r.is_iscritto IS TRUE OR r.is_istruttore IS TRUE ")
                lista_persone = conn.execute(s)
                
                return render_template("profilo.html", title="profilo", lista_persone = lista_persone, dati_utente = dati_utente_corrente, ruolo="capo")
    

    #queste tre righe sono di prova per vedere se effettivamente prende
    #qualcosa dal database, ma per ora non appare nulla. Le commento
   # user = Persone.query.filter_by(codice_fiscale = id).first()
   # a = current_user.nome
   # print(a)

   #queste due sotto sono quelle che dovrebbero funzionare bene
   #creo l'oggetto utente filtrandolo per il suo id (preso sopra)
   #dati_richiesti è la tabella con i dati che poi viene mostrata in profilo.html
    return render_template(
        'profilo.html',
        dati_utente = dati_utente_corrente,
        title = 'Il mio profilo',
        ruolo = "iscritto"
        )


@login_required
@app.route('/logout')
def logout():
    #elimina dalla sessione l'utente attuale
    logout_user()
    return redirect('/home')

@app.route('/corsi', methods = ['POST', 'GET'])
def corsi():
    if request.method == 'POST':
        data = request.form['dataSelezionata']
        #livelloUtente è il livello dell'utente (da fare) come prova ho messo 2
        livello_utente = 2
        
        # SE VOGLIO USARE GET USO QUESTA SINTASSI : data = request.args.get('dataSelezionata', '')
        # da fare query dei corsi in quella 'data'
        return render_template( 'corsi.html',title='Corsi Disponibili', data = data, livelloUtente = livello_utente)
    else: 
        return render_template( 'corsi.html',title='Corsi Disponibili' )


@app.route('/istruttori')
def istruttori():
    with engine.connect() as conn:
        q = text("SELECT p.nome,p.cognome,i.cellulare  FROM persone p JOIN ruoli r ON p.codice_fiscale = r.codice_fiscale JOIN info_contatti i ON p.codice_fiscale=i.codice_fiscale WHERE r.is_istruttore is TRUE")
        lista_istruttori = conn.execute(q)
    
    return render_template('istruttori.html',title='Elenco istruttori',lista_istruttori = lista_istruttori )


@app.route('/creazionePalestra')
def creazionePalestra():
    """pagina della creazione della palestra"""
    return render_template(
        'creazionePalestra.html',
        title='Crea La Palestra'
    )


@app.route('/calendario', methods=['POST', 'GET'])
def calendario():
    #calendario
    
    mesi=["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]
    nome_giorni_della_settimana=["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
    data_corrente = datetime.today()
   
    anno = data_corrente.year
    mese = data_corrente.month
    
    data_corrente = {"anno" : anno , "mese" : mese , "giorno" : data_corrente.day } # anno mese giorno

    if request.method == 'POST':
        if request.form['cambiaMese'] == '<-':
            mese = int(request.form['meseCorrenteSelezionato'])-1
            if mese == 0:
                anno = int(request.form['annoCorrenteSelezionato'])-1
                mese = 12

        if request.form['cambiaMese'] == '->':
            mese = int(request.form['meseCorrenteSelezionato'])+1
            if mese == 13:
                anno = int(request.form['annoCorrenteSelezionato'])+1
                mese = 1

    primo_giorno_indice = datetime(anno,mese,1).weekday()
    primo_giorno_nome = nome_giorni_della_settimana[primo_giorno_indice]
   
   

    
    num_giorni = monthrange(anno, mese)[1]
    return render_template('calendario.html',title='calendario', 
    meseNumerico=mese, num_giorni=num_giorni, nomeMese=mesi[mese-1],annoNumerico = anno,
    dataCorrente = data_corrente,primo_giorno_nome = primo_giorno_nome, nome_giorni_settimana=nome_giorni_della_settimana,
    indice_settimana_del_primo_giorno = primo_giorno_indice)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        nome = request.form['nome']
        cf = request.form['cf']
        cognome = request.form['cognome']
        email = request.form['email']
        pwd = request.form['psw']
        cell = request.form['cell']
        residenza =  request.form['residenza']
        citta = request.form['citta']
        
        # esiste =  Persone.query.filter_by(codice_fiscale = cf).first()
        #if esiste is not None:
         #   flash("persona gia esistente")
         #   return redirect(url_for("admin"))
        #else:
            #inserisco i dati
        try:
            with engine.connect() as conn:
                s = text("INSERT INTO persone(codice_fiscale,nome,cognome,email,data_iscrizione,password) VALUES (:codice_fiscale, :nome, :cognome, :email, :data_iscrizione, :password)")
                conn.execute(s,codice_fiscale=cf, nome=nome, cognome=cognome,email=email, data_iscrizione = datetime.today(),password=generate_password_hash(pwd, method = 'sha256', salt_length = 8) )
                s = text("INSERT INTO info_contatti(codice_fiscale,cellulare,città,residenza) VALUES (:codice_fiscale,:cellulare, :citta,:residenza)")
                conn.execute(s,codice_fiscale=cf,cellulare=cell, citta = citta , residenza = residenza)
                s = text("INSERT INTO ruoli(codice_fiscale,is_capo,is_iscritto,is_istruttore,is_responsabile) VALUES (:codice_fiscale,True,False,False,False)")
                conn.execute(s,codice_fiscale=cf)
                flash("inserimento")
                
           
        except:
            flash("errore nell'inserimento")
            raise
            
    
    return render_template("admin.html" , title='Amministrazione')
    
   