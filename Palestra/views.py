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
from wtforms import StringField, PasswordField, IntegerField, FormField, RadioField, validators
from wtforms.validators import InputRequired, Email, Length, Optional
from sqlalchemy import create_engine
from Palestra import app
from .models_finale import * 
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import re
import numpy
#importa le URI per il database dal file __init__.py
from .__init__ import DB_URI, DB_URI_ISCRITTO, DB_URI_CAPO , DB_URI_ADMIN , DB_URI_ISTRUTTORE

#costanti utili
nome_giorni_della_settimana=["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
RUOLI = ["adminDB", "capo", "istruttore", "iscritto" ]
mesi=["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]

#definizione delle varie engine le quali servono per eseguire le connessioni al db nel momento oppurtuno
engine = create_engine(DB_URI)
engine_iscritto = create_engine(DB_URI_ISCRITTO)
engine_capo = create_engine(DB_URI_CAPO)
engine_istruttore = create_engine(DB_URI_ISTRUTTORE)
engine_admin = create_engine(DB_URI_ADMIN)

#inizializza la libreria che gestisce i login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#funzione importante che serve affinché flask login tenga
#traccia dell'utente loggato, tramite il suo id di sessione
#segue l'esempio che c'è qui: https://flask-login.readthedocs.io/en/latest/#your-user-class
@login_manager.user_loader
def user_loader(id_utente):
    
    with  engine.connect().execution_options(isolation_level="READ UNCOMMITTED") as conn:
        conn.begin()
        try :
            return  Persone.query.filter_by(codice_fiscale = id_utente).first()
        except:
            flash("Errore")
            return null
        finally:
            conn.close()
            
           
    


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
    codice_fiscale = StringField('Codice fiscale', validators = [InputRequired(), Length(min = 2, max = 50)])
    nome = StringField('Nome', validators = [InputRequired(), Length(min = 3, max = 50)])
    cognome = StringField('Cognome', validators = [InputRequired(), Length(min = 3, max = 50)])
    #la data dell'iscrizione la prendiamo al momento della registrazione    
    email = StringField('Email', validators = [InputRequired(), Email(message = 'Email non valida'), Length(max = 50)])
    password = PasswordField('Password', validators = [InputRequired(), Length(min = 1, max = 50)])
    #mettiamo il conferma password? Boh, intanto c'è, poi al massimo lo eliminiamo
    #chk_password = PasswordField('conferma password', validators = [InputRequired(), Length(min = 8, max = 50)])
    #le opzioni di contatto 
    telefono = StringField('Telefono', validators = [InputRequired(), Length(max=11)])
    residenza = StringField('Luogo di residenza', validators = [InputRequired()])
    citta = StringField('Città di residenza', validators = [InputRequired()])


@app.route('/')
@app.route('/home')
def home():
    
    
    with engine_iscritto.connect().execution_options(isolation_level="READ COMMITTED") as conn:
        
        totale_lezioni_svolte_al_mese = text("SELECT COUNT(*) AS numcorsi, CAST(date_part('month',data)as int) AS meseint  FROM sale_corsi  GROUP BY date_part('month',data) ")
        tipologie_corsi_query = text("SELECT distinct (nome_tipologia), descrizione FROM tipologie_corsi ")
        lista_tipologie_corsi = conn.execute(tipologie_corsi_query)
        
        #creo delle copie ed agisco su di esse xk il cursore scarica la tabella
        tab_totale_lezioni_svolte_al_mese = conn.execute(totale_lezioni_svolte_al_mese)
        tab_totale_lezioni_svolte_al_mese_copia = conn.execute(totale_lezioni_svolte_al_mese)
        tab_totale_lezioni_svolte_al_mese_copia2 = conn.execute(totale_lezioni_svolte_al_mese)

        lista_num_corsi = []
        mesi_con_max_corsi = []
        max_corsi = 0
        for row in tab_totale_lezioni_svolte_al_mese_copia:
            lista_num_corsi.append(row['numcorsi'])
        if lista_num_corsi:
            max_corsi =  max(lista_num_corsi)
           
            for row in  tab_totale_lezioni_svolte_al_mese_copia2:
                if row['numcorsi'] == max_corsi:
                    mesi_con_max_corsi.append(row['meseint'])


        #affluenza media x ogni giorno della settimana
        cont_giorno_settimana  = contaGiorni()
        s = text("SELECT * FROM vista_prenotazioni_settimana")
        num_prenotazioni_per_giorno_settimana = conn.execute(s)
        arr_medie = [0,0,0,0,0,0,0]

        #calcolo le medie
        for row in num_prenotazioni_per_giorno_settimana:
            for i in range(0,len(arr_medie)):
                if cont_giorno_settimana[i] != 0 and row[nome_giorni_della_settimana[i].lower()] is not None  :
                    arr_medie[i] = int(row[nome_giorni_della_settimana[i].lower()]) / int(cont_giorno_settimana[i])
                else:
                    arr_medie[i] = 0
            print("medie calcolate :")        
            print(arr_medie)
    

        
        
    return render_template(
        'home.html',
        title='Home Page', nome_mesi = mesi, lezioni_al_mese = tab_totale_lezioni_svolte_al_mese, mesi_con_piu_corsi = mesi_con_max_corsi ,num_corsi =  max_corsi, medie = arr_medie , nome_giorni_della_settimana = nome_giorni_della_settimana, lista_tipologie_corsi = lista_tipologie_corsi
    )


@app.route('/login', methods = ['GET','POST'])
def login():
    #crea il form seguendo le istruzioni della classe login scritta sopra
    form = LoginForm()

    #se tutti i campi sono validati
    ema = form.email.data
    pwd = form.password.data
    #controlla che ci sia una sola email corrispondente
    if request.method == 'POST':
        utente = Persone.query.filter_by(email = ema).first()
        #se c'è, allora controlla anche la password (salvata criptata)
        if utente is not None and utente.check_password(pwd):
            #se tutto va bene, effettua il login, aggiungendo l'utente
            #alla sessione e riportandolo alla schermata profilo
            login_user(utente)
            if ema== "admin@gmail.com" and pwd == "admin":
                return redirect(url_for('admin'))
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

        persona_gia_presente = False
        with engine_iscritto.connect().execution_options(isolation_level="READ COMMITTED")as conn:
            lista_persone =  conn.execute(text("SELECT codice_fiscale FROM persone " ))
        for row in lista_persone:
            if row['codice_fiscale'] == codiceFisc and persona_gia_presente == False:
                persona_gia_presente = True
        if persona_gia_presente == True :
            flash("Sei gia iscritto? controlla meglio il tuo codice fiscale ")
            
        else:    
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



@app.route('/profilo', methods = ['POST','GET'])
@login_required
def profilo():
    flash("Ecco il tuo profilo!")
    #prendo l'id dell'utente corrente e le sue info
    if current_user != None:
        id = Persone.get_id(current_user)
        ruolo =RUOLI[Persone.get_role(current_user)]
        dati_utente_corrente = Persone.query.join(InfoContatti,Persone.codice_fiscale == InfoContatti.codice_fiscale)\
                                .add_columns(Persone.codice_fiscale,InfoContatti.telefono, Persone.email , Persone.cognome, Persone.nome, Persone.data_iscrizione).filter_by(codice_fiscale = id).first()
        print(ruolo)
        
        if ruolo == "istruttore" or ruolo == "iscritto": #se è istruttore o iscritto
            #in caso da cancellare sta parte
            if "autodistruzione" in request.form and request.form['autodistruzione'] == "Elimina Profilo":

                if ruolo == "iscritto": 
                    elimina_prenotazioni = text("DELETE FROM prenotazioni WHERE codice_fiscale = :cf");
                    elimina_info_contatti = text("DELETE FROM info_contatti WHERE codice_fiscale = :cf")
                    elimina_persona = text("DELETE FROM persone WHERE codice_fiscale = :cf")
                    with engine_iscritto.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
                        conn.execute(elimina_prenotazioni, cf=id)
                        conn.execute(elimina_info_contatti, cf=id)
                        conn.execute(elimina_persona, cf=id)
                return render_template("home.html")

            if "prenotaCorso" in request.form and request.form['prenotaCorso'] == "Prenotati":
                data_prenotata=request.form['dataPrenotata'].replace(" ", "-")
                id_sala=request.form['idSala']
                cf_utente=request.form['codiceFiscaleUtente']
                id_fascia=request.form['idFascia']

           
            
            #inserisco il posto x il corso
                try:
                    q_insert_posto = text("INSERT INTO prenotazioni(data,codice_fiscale,id_sala,id_fascia, codice_prenotazione) VALUES(:d,:cf,:ids,:idf, :cod_prenotazione) ")
                    with engine_iscritto.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                        conn.execute(q_insert_posto,d=data_prenotata, cf=cf_utente, ids=id_sala, idf=id_fascia, cod_prenotazione = creaIDprenotazione())
                        
                except:
                    raise
            #prenotazione della sala pesi
            if "prenotaSalaPesi" in request.form and request.form['prenotaSalaPesi'] == "Prenotati":
                data_prenotata=request.form['dataPrenotata'].replace(" ", "-")
                id_sala=request.form['idSala']
                cf_utente=request.form['codiceFiscaleUtente']
                id_fascia=request.form['idFascia']
                #inserisco il posto x la sala pessi
                try:
                    q_insert_posto = text("INSERT INTO prenotazioni(data,codice_fiscale,id_sala,id_fascia, codice_prenotazione) VALUES(:d,:cf,:ids,:idf, :cod_prenotazione) ")
                    with engine_istruttore.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                        conn.execute(q_insert_posto,d=data_prenotata, cf=cf_utente, ids=id_sala, idf=id_fascia, cod_prenotazione = creaIDprenotazione())
                        
                except:
                    
                    #QUA SCATAA IL TRIGGER CHE GENERA UN ECCEZIONE!!!!!
                    flash("AIA SONO FINITI I POSTI")
                    
            

            #se è stata confermata la cancellazione cancella la prenotazione
            try:
                if "Conferma" in request.form and request.form['Conferma'] == "Conferma Cancellazione" and "id_prenotazione_key" in  request.form :
                    
                    #q_disabilita/elimina la prenotazione CON VALORE 3 perchè la ha eliminata un iscritto
                    q_disabilita = text("UPDATE prenotazioni SET eliminata = 3 WHERE codice_prenotazione=:c ")
                    with engine_iscritto.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                        conn.execute(q_disabilita, c=request.form['id_prenotazione_key'])
                        
            except:
                raise

            #CANCELLA IL CORSO
                
            if request.method == "POST" and "cancellaCorso" in request.form:
                try:
                    id_corso = request.form['id_corso_da_cancellare']
                    dataCorso = request.form['dataCorso'] 
                    id_fascia = request.form['id_fascia']
                    id_sala = request.form['id_sala']
                    with engine_istruttore.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                        
                        
                        s = text("UPDATE prenotazioni SET eliminata = 2 WHERE data = :data AND id_sala = :ids AND id_fascia = :idf ")
                        conn.execute(s, data = dataCorso, ids = id_sala, idf=id_fascia)
                        s = text("DELETE FROM sale_corsi WHERE id_corso = :idc AND id_sala = :ids AND data = :data ")
                        conn.execute(s,idc=id_corso,ids = id_sala , data = dataCorso )
                        s = text("DELETE FROM corsi WHERE id_corso = :idc")
                        conn.execute(s,idc=id_corso)
                except:
                    
                    raise

            #prenotazioni gia fatte x questo utente
            q_lista_prenotazioni = text("SELECT p.data, p.id_sala, fs.id_fascia, p.codice_prenotazione, fs.inizio, fs.fine, "
                                    "CASE WHEN s.solo_attrezzi is TRUE  THEN 'Pesi' "
                                        "WHEN s.solo_attrezzi is FALSE  THEN 'Corso' END tipo_sala "
                                    "FROM prenotazioni p JOIN sale s ON p.id_sala = s.id_sala JOIN fascia_oraria fs  ON p.id_fascia=fs.id_fascia  WHERE p.codice_fiscale=:id_utente AND p.eliminata IS NULL" )
            with engine_iscritto.connect().execution_options(isolation_level="READ COMMITTED") as conn:
                tab_prenotazioni_effettuate = conn.execute(q_lista_prenotazioni,id_utente=id)

            if ruolo == "istruttore": # istruttore            
            #corsi creati da questo istruttore
                q_corsi_creati = text("SELECT sc.data, c.id_corso, f.inizio , f.fine, c.nome_corso, tc.nome_tipologia, f.id_fascia, sc.id_sala "
                " FROM corsi c JOIN sale_corsi sc ON sc.id_corso=c.id_corso JOIN fascia_oraria f ON sc.id_fascia= f.id_fascia JOIN tipologie_corsi tc ON c.id_tipologia = tc.id_tipologia " 
                "  WHERE c.codice_fiscale_istruttore = :id_utente "
                " ORDER BY sc.data, f.inizio ASC")
                #READ UNCOMMITTED perchè un corso non puo essere toccato da un altro istruttore o capo ma solo da chi lo ha creato
                with engine_istruttore.connect().execution_options(isolation_level="READ UNCOMMITTED") as conn:
                    tab_corsi_creati = conn.execute(q_corsi_creati,id_utente=id)

                
            if ruolo == "istruttore":     
                return render_template("profilo.html",title="profilo", dati_utente = dati_utente_corrente, ruolo=ruolo, prenotazioni_effettuate=tab_prenotazioni_effettuate, tab_corsi_creati = tab_corsi_creati)
            if ruolo == "iscritto":
                return render_template("profilo.html",title="profilo", dati_utente = dati_utente_corrente, ruolo=ruolo, prenotazioni_effettuate=tab_prenotazioni_effettuate)
        if ruolo == "capo": 
            if palestra_gia_creata() == True:
                mostra_link_creazione_palestra = "False";
            else:
                mostra_link_creazione_palestra_abilitato = "True";

            #puo fare upgrade da iscritto a istruttore e viceversa
            if 'modificavalori' in request.form and  request.form['modificavalori'] == "ModificaPermessi":
                cf_passato = request.form['id_passato']
                nome_radio_button = cf_passato + "_radio"
                v = request.form[nome_radio_button]
                print(v)
                with engine_capo.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                    if v == "istruttore":
                        s = text("UPDATE persone SET ruolo = 2 WHERE codice_fiscale = :cf AND ruolo <> '2'")
                        conn.execute(s,cf=cf_passato)
                    elif v == "iscritto":
                        s = text("UPDATE persone SET ruolo = 3 WHERE codice_fiscale = :cf AND ruolo <> '3' " )
                        conn.execute(s,cf=cf_passato)
            
            #mostra tutti gli iscritti e istruttori
            with engine_capo.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                s = text("SELECT p.codice_fiscale, p.nome, p.cognome, i.telefono , p.ruolo FROM  persone p JOIN info_contatti i ON p.codice_fiscale=i.codice_fiscale WHERE p.ruolo='3' OR p.ruolo='2' ORDER BY p.ruolo ")
                lista_persone = conn.execute(s)

            return render_template("profilo.html", title="profilo", lista_persone = lista_persone, dati_utente = dati_utente_corrente, ruolo=ruolo, mostra_link_creazione_palestra = mostra_link_creazione_palestra )
    else :
        return render_template("registrazione.html", title="registrazione")
   



@app.route('/logout')
@login_required
def logout():
    #elimina dalla sessione l'utente attuale
    logout_user()
    return redirect('/home')

@login_required
@app.route('/corsi', methods = ['POST', 'GET'])
def corsi():
    

    #controlla se va bene che sia messa solo sta parte dentro la richiesta post
    if request.method == 'POST':
        data = request.form['dataSelezionata']
        tmp_data = data[2 : len(data) : ]
        data_for_DB = str(datetime.strptime(tmp_data,"%y %m %d")).split(' ')
        data_for_DB = data_for_DB[0]
        id_utente = Persone.get_id(current_user)
        ruolo = RUOLI[Persone.get_role(current_user)]
        intGiorno_settimana = data_to_giorno_settimana(data_for_DB)

    is_ricerca_setted = request.method == 'POST' and "ricerca" in request.form and request.form['ricerca'] == "Cerca"

    if "dataSelezionata" in request.form:
        if ruolo == "istruttore":
            #INSERIMENTO DEL CORSO
            if request.method == 'POST'and "inserimentoCorso" in request.form and request.form['inserimentoCorso'] == "Inserisci il corso":
                nome_lista_delle_fasce = []
                for namesID in request.form:
                   if re.match('nomeRadioIdFascia [0-9]*',namesID):
                       nome_lista_delle_fasce.append(namesID)
                if nome_lista_delle_fasce:
                    for e in nome_lista_delle_fasce:
                        v = request.form[e]
                        try:
                            print(v)
                            id_tipologia_corso = request.form['tipologie']
                            nome_corso = request.form['nomeCorso']
                            nuovo_id_corso = creaIDcorso()
                            idfascia_e_id_sala = v.split(' ')
                            id_fascia = idfascia_e_id_sala[0].split('_')[1]
                            id_sala = idfascia_e_id_sala[1].split('_')[1]
                            print(id_fascia )
                            print(id_sala )
                            #inserisce il corso
                            with engine_istruttore.connect().execution_options(isolation_level="REPEATABLE READ") as conn :
                                prep_query2 = text("INSERT INTO corsi( id_corso, nome_corso, codice_fiscale_istruttore , id_tipologia) VALUES( :idc , :nc ,:cfi, :idt)")
                                conn.execute(prep_query2, idc = nuovo_id_corso , nc=nome_corso , cfi= id_utente, idt=id_tipologia_corso )
                                prep_query = text("INSERT INTO sale_corsi(id_sala, id_corso, data, id_fascia) VALUES(:ids , :idc , :d , :idf)")
                                conn.execute(prep_query, ids=id_sala, idc=nuovo_id_corso, d= data_for_DB, idf=id_fascia)
                            
                        except:
                            flash("Aia! sembra che qualcuno ti abbia preceduto, rifai l'operazione")
                        else:
                            flash("inserimento riuscito!")
                else : 
                    flash("seleziona almeno una fascia oraria!")                       
                       
                              
                

                
                

        if is_ricerca_setted :
            if current_user != None and "ora_iniziale_ricerca" in request.form and "ora_finale_ricerca" in request.form:
                
                input_ora_inizio = request.form['ora_iniziale_ricerca']
                input_ora_fine = request.form['ora_finale_ricerca']
                if input_ora_inizio == '' or  input_ora_fine == '':
                        flash("riempire i campi")
                        return  render_template( 'corsi.html',title='Corsi Disponibili', data = data, ruolo = ruolo)


                if ruolo == 'capo':
                    #lista prenotazioni in un certo giorno 
                    with engine_capo.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                        s = text("SELECT pr.id_sala , f.inizio, f.fine , pr.codice_fiscale , p.nome , p.cognome, i.telefono "
                                "FROM prenotazioni pr JOIN fascia_oraria f ON (f.id_fascia = pr.id_fascia) JOIN persone p ON (p.codice_fiscale = pr.codice_fiscale) JOIN info_contatti i ON (i.codice_fiscale = pr.codice_fiscale) " 
                                "WHERE f.inizio >= :oraInizio AND f.fine <= :oraFine AND f.giorno = :intGiorno AND pr.data = :input_data "
                                
                            )
                        tab_lista_prenotazioni = conn.execute(s, oraInizio=input_ora_inizio , oraFine = input_ora_fine  ,intGiorno = intGiorno_settimana, input_data = data_for_DB )                  
                    return render_template( 'corsi.html',title='Corsi Disponibili', data = data, ruolo = ruolo,  tab_lista_prenotazioni = tab_lista_prenotazioni )

                if ruolo == "iscritto" or ruolo == "istruttore" : #ricerca corsi disponibili
                    
                    with engine_iscritto.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                        q_lista_tipologie = text("SELECT id_tipologia, nome_tipologia FROM tipologie_corsi ")
                        lista_tipologie_tab = conn.execute(q_lista_tipologie)
                        
                        s = text("SELECT sc.id_fascia,f.inizio,f.fine, sc.id_sala,tc.nome_tipologia, pi.nome AS nome_istruttore, pi.cognome AS cognome_istruttore "
                            "FROM sale_corsi sc JOIN fascia_oraria f ON sc.id_fascia=f.id_fascia "
                            "JOIN sale s ON sc.id_sala= s.id_sala JOIN corsi co ON co.id_corso=sc.id_corso JOIN persone pi ON (pi.codice_fiscale =co.codice_fiscale_istruttore AND co.codice_fiscale_istruttore <> :cf ) JOIN tipologie_corsi tc ON co.id_tipologia=tc.id_tipologia "
                            "WHERE f.inizio >= :oraInizio AND f.fine <= :oraFine AND f.giorno = :intGiorno AND sc.data = :input_data "
                            "AND s.posti_totali > (SELECT Count(*)AS numPrenotati " 
                                    "FROM prenotazioni pr JOIN sale_corsi sc1 ON (sc1.id_sala=sc.id_sala AND pr.id_sala= sc.id_sala) "
                                    "JOIN fascia_oraria f1 ON f1.id_fascia=f.id_fascia "
                                    "WHERE pr.data = :input_data) "
                            
                                    "AND f.id_fascia NOT IN (SELECT id_fascia FROM prenotazioni WHERE data = :input_data AND codice_fiscale = :cf AND eliminata IS NULL) "
                          
                            )


                        q_sale_pesi_libere = text(
                            "SELECT s1.id_sala, f1.id_fascia , f1.inizio, f1.fine "
                            "FROM sale s1  JOIN fascia_oraria f1 ON (f1.giorno = :intGiorno AND f1.inizio >= :oraInizio AND f1.fine <= :oraFine) "
                            "WHERE s1.solo_attrezzi IS TRUE " 
		                            "AND s1.posti_totali > (SELECT count(*) " 
							                                "FROM prenotazioni p JOIN sale s ON p.id_sala = s1.id_sala "
							                                "WHERE p.data= :input_data AND s.solo_attrezzi IS TRUE AND p.eliminata IS NULL  AND p.id_fascia = f1.id_fascia )"
                                    "AND f1.id_fascia NOT IN (SELECT p.id_fascia "
                                                            "FROM prenotazioni p  " 
                                                            "WHERE p.data= :input_data AND p.codice_fiscale = :cf AND p.eliminata IS NULL) "
                                    "AND f1.id_fascia NOT IN (SELECT id_fascia "
                                                            "FROM sale_corsi sc JOIN corsi c ON  (sc.id_corso= c.id_corso  ) "
                                                            "WHERE  c.codice_fiscale_istruttore = :cf AND sc.data = :input_data ) "
							)

                    try:
                        with engine_iscritto.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                            corsi_liberi = conn.execute(s, oraInizio=input_ora_inizio , oraFine = input_ora_fine  ,intGiorno = intGiorno_settimana, input_data = data_for_DB, cf= id_utente )
                            sale_pesi_libere = conn.execute(q_sale_pesi_libere, oraInizio=input_ora_inizio , oraFine = input_ora_fine  ,intGiorno = intGiorno_settimana, input_data = data_for_DB,cf= id_utente )
                    except:
                        raise
                

                if ruolo == "istruttore": 
               
                    q_sale_libere = text(
                        "SELECT s.id_sala  , f1.inizio ,f1.fine ,f1.id_fascia, s.posti_totali "
                        "FROM sale s JOIN fascia_oraria f1 ON ( f1.inizio >= :oraInizio AND f1.fine <= :oraFine AND f1.giorno = :g ) "
                        "WHERE s.id_sala NOT IN (SELECT sc.id_sala FROM sale_corsi sc JOIN fascia_oraria f ON sc.id_fascia = f.id_fascia WHERE f1.id_fascia = f.id_fascia AND sc.data = :dataDB) "
                        "AND s.solo_attrezzi IS FALSE "
                        "GROUP BY  s.id_sala, f1.id_fascia "
                        "ORDER BY f1.id_fascia "
                    )
                    try:
                        with engine_istruttore.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
                            sale_disp_con_fasce = conn.execute(q_sale_libere, dataDB=data_for_DB, oraInizio = input_ora_inizio, oraFine = input_ora_fine , g= intGiorno_settimana)
                    except: 
                        raise
                    return render_template( 'corsi.html',title='Corsi Disponibili', data = data, ruolo = ruolo, sale_disp_con_fasce =sale_disp_con_fasce , info_corsi =corsi_liberi, lista_tipologie_tab = lista_tipologie_tab,cf_utente = id_utente, sale_pesi_libere = sale_pesi_libere )
                return render_template( 'corsi.html',title='Corsi Disponibili', data = data, ruolo = ruolo,  info_corsi =corsi_liberi, lista_tipologie_tab = lista_tipologie_tab,cf_utente = id_utente, sale_pesi_libere = sale_pesi_libere )
        else:
           return  render_template( 'corsi.html',title='Corsi Disponibili', data = data)   
        
    else: 
        return redirect(url_for("home"))

@app.route('/istruttori')
@login_required
def istruttori():
    with engine_istruttore.connect().execution_options(isolation_level="READ UNCOMMITTED") as conn:
        q = text("SELECT p.nome,p.cognome,i.telefono  FROM persone p  JOIN info_contatti i ON p.codice_fiscale=i.codice_fiscale WHERE p.ruolo=2")
        lista_istruttori = conn.execute(q)
    
    return render_template('istruttori.html',title='Elenco istruttori',lista_istruttori = lista_istruttori )


@app.route('/creazionePalestra',methods=['POST', 'GET'])
@login_required
def creazionePalestra():
    tipologie_presenti = []
    
    if "AggiungiTipoCorso" in request.form and request.form['AggiungiTipoCorso'] is not None and "nomeTipologiaCorso" in request.form and request.form['nomeTipologiaCorso'] is not None :
        nome_tipo = request.form['nomeTipologiaCorso']
        descrizione = request.form['descrizioneTipologiaCorso']
        #tipologie gia inserite
        with engine_capo.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
            res = conn.execute(" SELECT nome_tipologia FROM tipologie_corsi")
            tipologie_presenti = []
            for row in res:
                tipologie_presenti.append(row['nome_tipologia'])
            #se non c'è la tipologia la inserisce
            if nome_tipo not in tipologie_presenti:
                s = text("INSERT INTO tipologie_corsi(id_tipologia,nome_tipologia,descrizione) VALUES( :id, :n, :d )")
                conn.execute(s, id=creaIDtipologiaCorso(), n=nome_tipo , d=descrizione )
                flash("inserimento della tipologia riuscito")
            else:
                flash('la tipologia è gia presente')
            
            
            

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
                #inserimento fascia oraria read uncommitted xk tanto viene inserita solo la prima volta dal primo capo
                with engine_capo.connect().execution_options(isolation_level="READ UNCOMMITTED") as conn:    
                    s = text("INSERT INTO Fascia_oraria(id_fascia, giorno, inizio, fine) VALUES (:id, :g, :ora_i, :ora_f)" )
                    conn.execute(s,id=i, g =intGiorno, ora_i=ora_inizio, ora_f= ora_fine )
        
    
    
    #mostrare le tipologie di corsi già aggiunte (per agevolare l'inserimento)
    #in teoria ne hai una già fatta, ma non capivo dove mostrasse i dati, quindi l'ho aggiunta
    #sull'html. In caso rimuoviamo la mia
    with engine_capo.connect().execution_options(isolation_level="REPEATABLE READ") as conn:    
            s = text("SELECT nome_tipologia FROM tipologie_corsi" )
            el_tipologie = conn.execute(s)
            
    return render_template('creazionePalestra.html',title='Crea La Palestra',nome_giorni_della_settimana = nome_giorni_della_settimana, tipologie_corsi =tipologie_presenti, el_tipologie = el_tipologie)


@app.route('/calendario', methods=['POST', 'GET'])
@login_required
def calendario():
    #calendario
    if current_user != None:
        ruolo = Persone.get_role(current_user)
        
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
@login_required
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
        
        
        try:
            with engine_admin.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
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
@login_required
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
@login_required
def policy_occupazione():


    #update della policy modificata
    if "confermaModifica" in request.form and "dataInizioModificata" in request.form and "dataFineModificata" in request.form and "percModificata" in request.form and "id_policy" in request.form:


        with engine_capo.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            s = text("UPDATE policy_occupazione SET data_inizio=:inizio , data_fine = :fine , percentuale_occupabilità = :perc WHERE id_policy=:id")
            conn.execute(s, inizio=request.form['dataInizioModificata'],fine=request.form['dataFineModificata'], perc = request.form['percModificata'], id=request.form['id_policy']  )
            
    
   
    #inserimento di una policy    
    if request.method== 'POST' and 'confermaPolicy' in request.form:
        input_data_inizio = request.form['dpcm-start']    
        input_data_fine = request.form['dpcm-end']
        perc = request.form['perc']

        with engine_capo.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            s = text("SELECT id_policy "
                    "FROM policy_occupazione p "
                    "WHERE p.id_policy in (	SELECT p2.id_policy "
						                    "FROM policy_occupazione p2 "
						                    "WHERE p2.id_policy = p.id_policy "
								            "AND "
							                "( "
                                                "( :di BETWEEN p2.data_inizio and p2.data_fine OR :df BETWEEN p2.data_inizio and p2.data_fine) "
                                                "OR :di < now() " 
                                                "OR :df < now() "
                                                "OR (:di <= p2.data_inizio AND :df >= p2.data_fine) "
								            ") "
					                    ")"
                    )
            lista_policy_in_contrasto = conn.execute(s, di=input_data_inizio , df=input_data_fine)

        errore = "ok"
        for row in lista_policy_in_contrasto:
            if row['id_policy'] != null:
                errore = "Controlla meglio le date"
        
        if errore != "ok":
            flash(errore)
        else:    
            inserimento_policy = text("INSERT INTO policy_occupazione(data_inizio,data_fine, percentuale_occupabilità) VALUES(:i , :f, :p) ")
            with engine_capo.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
                conn.execute(inserimento_policy, i=input_data_inizio, f=input_data_fine, p=perc)
                flash("inserimento riuscito")

    #stampa tutte le policy
    tutte_le_policy = text("SELECT * FROM policy_occupazione ")
    with engine_capo.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        policies = conn.execute(tutte_le_policy)

    return render_template("policyOccupazione.html", title = "Occupazione", policies  = policies )


@app.route('/corsi/lista',  methods=['POST', 'GET'])
@login_required
def lista_corsi():

    #----------------------------------------------------DA FAREEEEE
    s = text("SELECT distinct c.nome_corso,  p.nome, p.cognome,t.nome_tipologia, t.descrizione , i.telefono "
            "FROM corsi c JOIN persone p ON (p.codice_fiscale = c.codice_fiscale_istruttore AND p.ruolo = 2) " 
            "JOIN tipologie_corsi t ON  t.id_tipologia = c.id_tipologia "
            "JOIN info_contatti i ON c.codice_fiscale_istruttore = i.codice_fiscale "
            "GROUP BY c.nome_corso, c.codice_fiscale_istruttore , p.nome, p.cognome ,t.nome_tipologia, t.descrizione,  i.telefono ;"
            )
    with engine_iscritto.connect() as conn:
        tab_lista_corsi = conn.execute(s)


    return render_template('lista_corsi.html', tab_lista_corsi = tab_lista_corsi)



#-------------------UTILI--------------

def creaIDsala():
    try:
        with engine_iscritto.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            s = "SELECT COUNT(id_sala) AS num_sala FROM SALE "
            res = conn.execute(s)
            for row in res:
                num_sala = row['num_sala']
                break

            next_id = int(num_sala) + 1
            return next_id
    except:
        flash("errore ricarica la pagina")
        raise 
def data_to_giorno_settimana(dataString):
    arr = []
    arr = dataString.split('-')
    giorno = arr[2]
    mese = arr[1]
    anno = arr[0]
    d = date(int(anno),int(mese),int(giorno))

    return int(d.weekday())+1


def creaIDcorso():
    try:
        with engine_iscritto.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            s = "SELECT COUNT(id_corso) AS num_corso FROM corsi "
            res = conn.execute(s)
            for row in res:
                num_corso = row['num_corso']
                break

            next_id = int(num_corso) + 1
            return next_id
    except:
        flash("errore ricarica la pagina")

def creaIDtipologiaCorso():
    try:
        with engine_capo.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
            s = "SELECT COUNT(*) AS num_tipologie FROM tipologie_corsi "
            res = conn.execute(s)
            for row in res:
                num_tipologie = row['num_tipologie']
                break

            next_id = int(num_tipologie) + 1
            return next_id
    except:
        flash("errore ricarica la pagina")

def creaIDprenotazione():
     with engine_iscritto.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
        s = "SELECT COUNT(*) AS num_prenotazioni FROM prenotazioni"
        res = conn.execute(s)
        for row in res:
            num_prenotazioni = row['num_prenotazioni']
            break

        next_id = int(num_prenotazioni) + 1
        return next_id


def contaGiorni():
    num_gs = [0,0,0,0,0,0,0]

    with engine_iscritto.connect().execution_options(isolation_level="READ COMMITTED") as conn: 
        
        #la data piu vechia (circa la creazione della palestra è la data di iscrizione del capo piu vecchia)
        query_data_piu_vecchia = text("SELECT data_iscrizione as data_creazione FROM persone WHERE ruolo = 1 ORDER BY data_iscrizione ASC limit 1")
        tab_data_vecchia = conn.execute(query_data_piu_vecchia)
       

    for row in tab_data_vecchia:
        data_piu_vecchia = row['data_creazione']
    
        #sono di tipo datetime.date
        data_corrente = date.today()
        
        while  data_piu_vecchia < data_corrente:
            gs = data_piu_vecchia.weekday()
            num_gs[gs] = num_gs[gs] + 1 
            data_piu_vecchia = data_piu_vecchia + timedelta(days=1)
    
            
    return num_gs


def palestra_gia_creata():
    #raed uncommitted perchè il capo che crea la palestra è uno solo
    with engine_capo.connect().execution_options(isolation_level="READ UNCOMMITTED") as conn:
        s = text("SELECT COUNT(*) as num_fasce FROM fascia_oraria")
        tab = conn.execute(s)
        for row in tab:
            if row['num_fasce'] != 0 :
                return True
            else:
                return False



@app.route('/lista_prenotazioni', methods=['POST', 'GET'])
@login_required
def lista_prenotazioni():
    if current_user != None:
        
        
        query_lista_prenotazioni_sale_pesi = text("SELECT pr.data, pr.codice_fiscale, pr.codice_prenotazione , pr.id_sala, pe.nome , pe.cognome , pe.email , f.inizio, f.fine , i.telefono "
                "FROM prenotazioni pr JOIN persone pe ON pr.codice_fiscale = pe.codice_fiscale "
                "JOIN info_contatti i ON i.codice_fiscale = pr.codice_fiscale "
                "JOIN fascia_oraria f ON f.id_fascia = pr.id_fascia "
                "JOIN sale s ON pr.id_sala = s.id_sala "
                "WHERE pr.eliminata IS NULL ORDER BY pr.data "
                )
        query_lista_prenotazioni_sale_corsi = text("SELECT pr.data, pr.codice_fiscale, pr.codice_prenotazione , pr.id_sala, pe.nome , pe.cognome , pe.email , f.inizio, f.fine , i.telefono , c.nome_corso , t.nome_tipologia "
                "FROM prenotazioni pr JOIN persone pe ON pr.codice_fiscale = pe.codice_fiscale JOIN info_contatti i ON i.codice_fiscale = pr.codice_fiscale "
                "JOIN fascia_oraria f ON f.id_fascia = pr.id_fascia "
                "JOIN sale_corsi s ON pr.id_sala = s.id_sala "
                "JOIN corsi c ON s.id_corso = c.id_corso "
                "JOIN tipologie_corsi t ON c.id_tipologia = t.id_tipologia "
                "WHERE pr.eliminata IS NULL ORDER BY pr.data "
                ) 
        query_prenotazioni_eliminate = text("SELECT pr.data, pr.codice_fiscale, pr.codice_prenotazione , pr.id_sala, pe.nome , pe.cognome , pe.email , f.inizio, f.fine, i.telefono "
                "FROM prenotazioni pr JOIN persone pe ON pr.codice_fiscale = pe.codice_fiscale JOIN info_contatti i ON i.codice_fiscale = pr.codice_fiscale "
                "JOIN fascia_oraria f ON f.id_fascia = pr.id_fascia "
                "WHERE pr.eliminata IS NOT NULL ORDER BY pr.data "
                )
        with engine_capo.connect().execution_options(isolation_level="READ COMMITTED") as conn:
            tab_lista_prenotazioni_sale_pesi = conn.execute(query_lista_prenotazioni_sale_pesi)
            tab_lista_prenotazioni_eliminate = conn.execute(query_prenotazioni_eliminate)
            tab_lista_prenotazioni_sale_corsi = conn.execute(query_lista_prenotazioni_sale_corsi)
        return render_template("lista_prenotazioni.html", tab_lista_prenotazioni_sale_pesi = tab_lista_prenotazioni_sale_pesi , tab_lista_prenotazioni_eliminate = tab_lista_prenotazioni_eliminate, tab_lista_prenotazioni_sale_corsi = tab_lista_prenotazioni_sale_corsi)

    return render_template("lista_prenotazioni.html")
