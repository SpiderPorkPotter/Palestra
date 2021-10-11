"""
Routes and views for the flask application.
"""

from datetime import *
from calendar import monthrange
from flask import render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm, form
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import null, text
from wtforms import StringField, PasswordField, IntegerField, FormField, RadioField
from wtforms.validators import InputRequired, Email, Length, Optional
from sqlalchemy import create_engine
from Palestra import app
from .models_finale import * 
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import re
import numpy

nome_giorni_della_settimana=["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
#psycopg2 è il driver che si usa per comunicare col database

DB_URI = "postgresql+psycopg2://postgres:passwordsupersegreta@localhost:5432/Palestra"
#DB_URI = "postgresql+psycopg2://postgres:a@localhost:5432/Palestra"
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
        return redirect('/login')
        

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
        type_tel = request.form['menuContatti']
        resdz = form.residenza.data
        citt = form.citta.data

        #creo l'oggetto utente
        nuovo_utente = Persone( nome = nom,
                                cognome = cogn,
                                email = em ,
                                data_iscrizione = datetime.today(),
                                codice_fiscale = codiceFisc,
                                residenza = resdz,
                                citta = citt,
                                ruolo = 3  # RUOLI :  adminDB=0, capo=1, istruttore=2, iscritto=3 
                               )
        nuovo_utente.set_password(passwd)

        info_nuovo_utente = InfoContatti(
                    telefono = tel,
                    descrizione = type_tel,
                    codice_fiscale = codiceFisc,
                    )

        
       
        db.session.add(nuovo_utente)
        db.session.commit()

        db.session.add(info_nuovo_utente)
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
                with engine.connect() as conn:
                    s = text("UPDATE persone SET ruolo = 2 WHERE codice_fiscale = :cf")
                    conn.execute(s,cf=cf_passato)
                #query update da iscritto a istruttore dopo averla fatta levare l'isstruzione "pass"
               
            if v == "iscritto":
                with engine.connect() as conn:
                    s = text("UPDATE persone SET ruolo = 3 WHERE codice_fiscale = :cf")
                    conn.execute(s,cf=cf_passato)
                #query update da istruttore passa a iscritto dopo averla fatta levare l'isstruzione "pass"
                

        #prendo gli id di tutti i capi
        s = text("SELECT codice_fiscale FROM persone  WHERE ruolo=1 AND codice_fiscale=:id_c")
        with engine.connect() as conn:
            dati_capi = conn.execute(s,id_c=id)
            #creo una lista fatta da tutti gli id dei capi
            ids_capi=[]
            for d in dati_capi:
               ids_capi.append(d['codice_fiscale'])
            
            #se l'id è nella lista dei capi stampo tutti gli iscritti
            if id in ids_capi:

                s = text("SELECT p.codice_fiscale, p.nome, p.cognome, i.telefono , p.ruolo FROM  persone p JOIN info_contatti i ON p.codice_fiscale=i.codice_fiscale WHERE p.ruolo=3 OR p.ruolo=2 ")
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
    
    data = request.form['dataSelezionata']
    tmp_data = data[2 : len(data) : ]
    data_for_DB = str(datetime.strptime(tmp_data,"%y %m %d")).split(' ')
    data_for_DB = data_for_DB[0]
    print(data_for_DB)
    is_ricerca_setted = request.method == 'POST' and "ricerca" in request.form and request.form['ricerca'] == "Cerca"
    
    if "dataSelezionata" in request.form:

        if request.method == 'POST'and "inserimentoCorso" in request.form and request.form['inserimentoCorso'] == "Inserisci il corso" and "fasceSaleSelezionate" in request.form:
            checkboxes_inputs = request.form.getlist("fasceSaleSelezionate")
            for e in checkboxes_inputs:
                #TODO DA FARE INSERIMANTO
                print(e)


        if is_ricerca_setted :
            if current_user != None and "ora_iniziale_ricerca" in request.form and "ora_finale_ricerca" in request.form:
                ruolo_utente = Persone.get_role(current_user)
                    #if ruolo_utente == 2: # istruttore
               
               
                intGiorno_settimana = data_to_giorno_settimana(data_for_DB)

                q_sale_libere = text(
                    "SELECT s.id_sala  , f1.inizio ,f1.fine ,f1.id_fascia "
                    "FROM sale s , fascia_oraria f1 "
                    "WHERE s.id_sala NOT IN (SELECT sc.id_sala FROM sale_corsi sc JOIN fascia_oraria f ON sc.id_fascia = f.id_fascia WHERE f1.id_fascia = f.id_fascia AND sc.data = :dataDB) "
                        " AND f1.inizio >= :oraInizio AND f1.fine <= :oraFine AND f1.giorno = :g AND s.solo_attrezzi IS FALSE "
					"GROUP BY s.id_sala , f1.id_fascia "
                    "ORDER BY f1.id_fascia "
                )
                input_ora_inizio = request.form['ora_iniziale_ricerca']
                input_ora_fine = request.form['ora_finale_ricerca']

                with engine.connect() as conn:
                    sale_libere = conn.execute(q_sale_libere, dataDB=data_for_DB, oraInizio = input_ora_inizio, oraFine = input_ora_fine , g= intGiorno_settimana)
                
                return render_template( 'corsi.html',title='Corsi Disponibili', data = data, ruolo_utente = ruolo_utente, sale_disp_con_fasce =sale_libere)
        else:
            render_template( 'corsi.html',title='Corsi Disponibili', data = data)   
        
        
        
        # SE VOGLIO USARE GET USO QUESTA SINTASSI : data = request.args.get('dataSelezionata', '')
        # da fare query dei corsi in quella 'data'
        ruolo_utente =100   # da levare
        return render_template( 'corsi.html',title='Corsi Disponibili', data = data, livelloUtente = ruolo_utente)
    else: 
        return render_template( 'corsi.html',title='Corsi Disponibili' )


@app.route('/istruttori')
def istruttori():
    with engine.connect() as conn:
        q = text("SELECT p.nome,p.cognome,i.telefono  FROM persone p  JOIN info_contatti i ON p.codice_fiscale=i.codice_fiscale WHERE p.ruolo=2")
        lista_istruttori = conn.execute(q)
    
    return render_template('istruttori.html',title='Elenco istruttori',lista_istruttori = lista_istruttori )


@app.route('/creazionePalestra',methods=['POST', 'GET'])
def creazionePalestra():
    
    """pagina della creazione della palestra"""

    if "inviaFasce" in request.form:
        copia_POST_array = numpy.array(list(request.form))
        for i in range(len(copia_POST_array)-1):
            
            if re.match("[1-7]_inizioFascia_[1-9]", str(copia_POST_array[i]) ) and re.match("[1-7]_fineFascia_[1-9]", str(copia_POST_array[i+1]) ) :

                s_fasciaInizio = str(copia_POST_array[i])
                s_fasciaFine = str(copia_POST_array[i+1])
               
                args_fascia_inizio = s_fasciaInizio.split('_')
                args_fascia_fine = s_fasciaFine.split('_')
                intGiorno = args_fascia_inizio[0]
                numFascia = args_fascia_inizio[2]

                ora_inizio = request.form[intGiorno + "_" + args_fascia_inizio[1] + "_" + numFascia]
                ora_fine =  request.form[intGiorno + "_" + args_fascia_fine[1] + "_" + numFascia]
                print(ora_inizio)
                print(ora_fine)
                
                with engine.connect() as conn:    
                    s = text("INSERT INTO Fascia_oraria(id_fascia, giorno, inizio, fine) VALUES (:id, :g, :ora_i, :ora_f)" )
                    conn.execute(s,id=i, g =intGiorno, ora_i=ora_inizio, ora_f= ora_fine )
     #mostrare le fasce gia aggiunte:
    with engine.connect() as conn:    
            s = text("SELECT * FROM Fascia_oraria  ORDER BY id_fascia, giorno " )
            tab_fasce = conn.execute(s)        
           
    return render_template('creazionePalestra.html',title='Crea La Palestra',tab_fasce = tab_fasce,nome_giorni_della_settimana = nome_giorni_della_settimana)


@app.route('/calendario', methods=['POST', 'GET'])
def calendario():
    #calendario
    if current_user != None:
        ruolo = Persone.get_role(current_user)
        
    
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
    indice_settimana_del_primo_giorno = primo_giorno_indice,
    ruolo = ruolo)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        nome = request.form['nome']
        cf = request.form['cf']
        cognome = request.form['cognome']
        email = request.form['email']
        pwd = request.form['psw']
        cell = request.form['cell']
        tipoCell = request.form['cellAdmin']
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
                s = text("INSERT INTO persone(codice_fiscale,nome,cognome,email,data_iscrizione,password,citta,residenza ,ruolo) VALUES (:codice_fiscale, :nome, :cognome, :email, :data_iscrizione, :password,:citta,:res,1)")
                conn.execute(s,codice_fiscale=cf, nome=nome, cognome=cognome,email=email, data_iscrizione = datetime.today(),password=generate_password_hash(pwd, method = 'sha256', salt_length = 8),citta=citta,res=residenza)

                s = text("INSERT INTO info_contatti(codice_fiscale,telefono,descrizione) VALUES (:codice_fiscale,:cellulare,:descrizione)")
                conn.execute(s,codice_fiscale=cf,cellulare=cell, descrizione=tipoCell)
               
                flash("inserimento")
                
           
        except:
            flash("errore nell'inserimento")
            raise
            
    
    return render_template("admin.html" , title='Amministrazione')
    


class CreaSalaForm(FlaskForm):
   
    nPosti = IntegerField('Numero posti totali', validators = [InputRequired(), Length(min = 1, max = 3)])
    attrezzi = RadioField('Seleziona se contiene solo attrezzi', choices=[('True','SI'),('False','NO')])
    
    
    


@app.route('/crea_sala', methods=['POST', 'GET'])
def crea_sala():
   
    if  "Submit" not in request.form :
        id_next_sala = creaIDsala()
   
    form = CreaSalaForm()

    if request.method == 'POST' and request.form['Submit'] == "Invia":
        id_next_sala = creaIDsala()
        posti = form.nPosti.data
        attrez = eval(form.attrezzi.data)

        nuova_sala = Sale(
                            id_sala = id_next_sala,
                            posti_totali = posti,
                            solo_attrezzi = attrez
                            )
        
        db.session.add(nuova_sala)
        db.session.commit()
        flash('Creazione completata')

    

    return render_template("creazioneSala.html", title = "Crea una nuova sala nella tua palestra", form = form, id_sala = id_next_sala)

@app.route('/policy_occupazione', methods=['POST', 'GET'])
def policy_occupazione():
    
    tutte_le_policy = text("SELECT * FROM policy_occupazione ")
    with engine.connect() as conn:
        policies = conn.execute(tutte_le_policy)
        copia = conn.execute(tutte_le_policy)
    
    lista_date_inizio = []
    lista_date_fine = []   
    for row in copia:
        if row['data_inizio'] != null and row['data_fine'] != null: 
            lista_date_inizio.append(row['data_inizio'])
            lista_date_fine.append(row['data_fine'])


    if request.method== 'POST' and 'confermaPolicy' in request.form:
        data_inizio = request.form['dpcm-start']    
        data_fine = request.form['dpcm-end']
        perc = request.form['perc']

        if data_inizio in lista_date_inizio or data_fine in lista_date_fine:
            flash('controlla meglio le date')
        else:    
            inserimento_policy = text("INSERT INTO policy_occupazione(data_inizio,data_fine, percentuale_occupabilità) VALUES(:i , :f, :p) ")
        with engine.connect() as conn:
            conn.execute(inserimento_policy, i=data_inizio, f=data_fine, p=perc)
            flash("inserimento riuscito")
        
    return render_template("policyOccupazione.html", title = "Occupazione", policies  = policies )


#-------------------UTILI--------------

def creaIDsala():
    with engine.connect() as conn:
        s = "SELECT COUNT(id_sala) AS num_sala FROM SALE "
        res = conn.execute(s)
        for row in res:
            num_sala = row['num_sala']
            break

        next_id = int(num_sala) + 1
        return next_id

def data_to_giorno_settimana(dataString):
    print("la datastring")
    print(dataString)
    arr = []
    arr = dataString.split('-')
    giorno = arr[2]
    mese = arr[1]
    anno = arr[0]
    d = date(int(anno),int(mese),int(giorno))

    return int(d.weekday())+1





