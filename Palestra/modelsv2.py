# coding: utf-8
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, BigInteger, String, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

#generato con   sqlacodegen postgresql://postgres:a@localhost/Palestra --outfile modelsv2.py
#a è la password del mio db, sostituitela con la vostra quando lo usate

#questo model rispecchia il mio database che ho modificato.
#La modifica era che la relazione tra palestre e persone era M:N
#In questo la relazione fa riferimento ad una relazione 1:M
#1 le palestre, M le persone. Per le persone ho portato dentro i valori
#is_istruttore, is_proprietario e nome_palestra che fa da chiave esterna
#per identificare chi va in quale palestra (l'idea è che uno quando si
#registra seleziona a quale palestra registrarsi)

Base = declarative_base()
metadata = Base.metadata

login_manager = LoginManager()

class FasciaOraria(Base):
    __tablename__ = 'fascia_oraria'

    id_fascia = Column(Integer, primary_key=True)
    inizio = Column(Time, nullable=False)
    fine = Column(Time, nullable=False)


class GiorniSettimana(Base):
    __tablename__ = 'giorni_settimana'

    giorno = Column(Integer, primary_key=True, nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), primary_key=True, nullable=False, index=True)

    fascia_oraria = relationship('FasciaOraria')

    #non tutti i valori sono nullable = False, altri li ho messi a True per evitare problemi con
    #le registrazioni di utenti per prova
class Persone(UserMixin, Base, db.Model):
    __tablename__ = 'persone'
  
    codice_fiscale = Column(String(16), primary_key=True)
    nome = Column(String(50), nullable=False)
    cognome = Column(String(50), nullable=False)
    data_iscrizione = Column(Date, nullable=True)
    telefono = Column(BigInteger, nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)
    is_istruttore = Column(Boolean, nullable=True)
    is_proprietario_palestra = Column(Boolean, nullable=True)
    nome_palestra = Column(ForeignKey('palestre.nome_palestra'), nullable=True, index=True)

    palestre = relationship('Palestre')

    ##########
    #funzioni per il login manager
    def __repr__(self):
        return self._repr(
                            codice_fiscale = self.codice_fiscale,
                            nome = self.nome,
                            cognome = self.cognome,
                            data_iscrizione = self.data_iscrizione,
                            telefono = self.telefono,
                            email = self.email,
                            passwd = self.passwd,
                            is_istruttore = self.is_istruttore,
                            is_proprietario_palestra = self.is_proprietario_palestra
                          )

    #converte la password da normale ad "hashata"
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd, method = 'sha256', salt_length = 8)

    #controlla l'hash della password
    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    #ritorna true se l'utente è gestore, false altrimenti
    def isIstruttore(self):
        return self.is_istruttore

    def isProprietario(self):
        return self.is_proprietario_palestra

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


class Palestre(Base):
    __tablename__ = 'palestre'

    nome_palestra = Column(String(50), primary_key=True)
    indirizzo = Column(String(50), nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True)

    fascia_oraria = relationship('FasciaOraria')


class OccupazionePosti(Base):
    __tablename__ = 'occupazione_posti'

    data_inizio = Column(Date, primary_key=True, nullable=False)
    data_fine = Column(Date, primary_key=True, nullable=False)
    nome_palestra = Column(ForeignKey('palestre.nome_palestra'), primary_key=True, nullable=False, index=True)
    percentuale_occupabilità = Column(Integer, nullable=False)

    palestre = relationship('Palestre')



    
    ##########

class Sale(Base):
    __tablename__ = 'sale'

    id_sala = Column(Integer, primary_key=True)
    posti_totali = Column(Integer, nullable=False)
    solo_attrezzi = Column(Boolean, nullable=False)
    nome_palestra = Column(ForeignKey('palestre.nome_palestra'), nullable=False, index=True)

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

