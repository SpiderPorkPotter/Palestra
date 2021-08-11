# coding: utf-8
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

#generato con   sqlacodegen postgresql://postgres:a@localhost/Palestra --outfile modelsv2.py
#a è la password del mio db, sostituitela con la vostra quando lo usate

Base = declarative_base()
metadata = Base.metadata

login_manager = LoginManager()
db = SQLAlchemy()

class FasciaOraria(Base):
    __tablename__ = 'fascia_oraria'

    id_fascia = Column(Integer, primary_key=True)
    inizio = Column(Time, nullable=False)
    fine = Column(Time, nullable=False)

#db.Model potrebbe dare fastidio facendo operazioni. Se le query eseguite non funzionano
#spostarlo dopo Base o toglierlo
class Persone(UserMixin, Base, db.Model):
    __tablename__ = 'persone'

    #quelli con #false significa che prima erano a nullable=True
    #è una mod temporanea
    codice_fiscale = Column(String(16), primary_key=True)
    nome = Column(String(50), nullable=False)
    cognome = Column(String(50), nullable=False)
    data_iscrizione = Column(Date, nullable=True) #False
    telefono = Column(Integer, nullable=False)
    is_istruttore = Column(Boolean, nullable=True) #False
    email = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)
    grado_accesso = Column(Integer, nullable=True) #False

    palestre = relationship('Palestre', secondary='palestre_persone')

    def __repr__(self):
        return self._repr(codice_fiscale=self.codice_fiscale,
                          nome = self.nome,
                          cognome = self.cognome,
                          data_iscrizione = self.data_iscrizione,
                          telefono = self.telefono,
                          is_istruttore = self.is_istruttore,
                          email = self.email,
                          passwd = self.passwd,
                          grado_accesso = self.grado_accesso)

    #converte la password da normale ad "hashata"
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd, method = 'sha256', salt_length = 8)

    #controlla l'hash della password
    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    #ritorna true se l'utente è gestore, false altrimenti
    def isIstruttore(self):
        return self.is_istruttore

    def is_active(self):
        """Vero sel'utente è attivo"""
        return True

    def get_id(self):
        return self.codice_fiscale

    def is_authenticated(self):
        """Ritorna true se l'utente è autenticato"""
        return True

    def is_anonymous(self):
        """Ritorna falso, perché gli utenti anonimi non sono supportati"""
        return False


class GiorniSettimana(Base):
    __tablename__ = 'giorni_settimana'

    giorno = Column(Integer, primary_key=True, nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), primary_key=True, nullable=False, index=True)

    fascia_oraria = relationship('FasciaOraria')


class Palestre(Base):
    __tablename__ = 'palestre'

    id_palestra = Column(String(50), primary_key=True)
    nome = Column(String(50), nullable=False)
    indirizzo = Column(String(50), nullable=False)
    codice_fiscale = Column(String(16), nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True)

    fascia_oraria = relationship('FasciaOraria')


class OccupazionePosti(Base):
    __tablename__ = 'occupazione_posti'

    data_inizio = Column(Date, primary_key=True, nullable=False)
    data_fine = Column(Date, primary_key=True, nullable=False)
    id_palestra = Column(ForeignKey('palestre.id_palestra'), primary_key=True, nullable=False, index=True)
    percentuale_occupabilità = Column(Integer, nullable=False)

    palestre = relationship('Palestre')


"""
Errore che viene fuori quando dopo aver inserito i dati sia nella pagina di registrazione,
sia nella pagina di login si preme submit quasi sicuramente a causa della relazione 
palestre_persone. Non so il perché penso sia dovuto al fatto 
che è una relazione molti a molti e quella terza tabella là
non viene riconosciuta. Ho provato a trasformarla in una class come quelle sopra,
ma non è cambiato nulla. 
Forse invece che farla molti a molti, la facciamo 1 a molti, così magari ci togliamo il pensiero.
È un'idea.

sqlalchemy.exc.InvalidRequestError: When initializing mapper mapped class Persone->persone, 
expression 'palestre_persone' failed to locate a name ("name 'palestre_persone' is not defined"). 
If this is a class name, consider adding this relationship() 
to the <class 'Palestra.models.Persone'> class after both dependent classes have been defined.
"""
t_palestre_persone = Table(
    'palestre_persone', metadata,
    Column('id_palestra', ForeignKey('palestre.id_palestra'), primary_key=True, nullable=False, index=True),
    Column('codice_fiscale', ForeignKey('persone.codice_fiscale'), primary_key=True, nullable=False, index=True)
)


class Sale(Base):
    __tablename__ = 'sale'

    id_sala = Column(Integer, primary_key=True)
    posti_totali = Column(Integer, nullable=False)
    solo_attrezzi = Column(Boolean, nullable=False)
    id_palestra = Column(ForeignKey('palestre.id_palestra'), nullable=False, index=True)

    palestre = relationship('Palestre')


class Corsi(Base):
    __tablename__ = 'corsi'

    id_corso = Column(Integer, primary_key=True)
    nome_corso = Column(String(50), nullable=False)
    max_partecipanti = Column(Integer, nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True)
    id_sala = Column(ForeignKey('sale.id_sala'), nullable=False, index=True)

    fascia_oraria = relationship('FasciaOraria')
    sale = relationship('Sale')


class Prenotazioni(Base):
    __tablename__ = 'prenotazioni'

    codice_prenotazione = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)
    id_sala = Column(ForeignKey('sale.id_sala'), nullable=False, index=True)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True)

    persone = relationship('Persone')
    fascia_oraria = relationship('FasciaOraria')
    sale = relationship('Sale')
