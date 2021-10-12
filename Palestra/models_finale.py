# coding: utf-8


from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, String, Time, text, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

#generato con:
#sqlacodegen postgresql://postgres:a@localhost/Palestra --outfile modelsv_finale.py

Base = declarative_base()
metadata = Base.metadata

login_manager = LoginManager()

class FasciaOraria(Base):
    __tablename__ = 'fascia_oraria'

    id_fascia = Column(Integer, primary_key=True, server_default=text("nextval('fascia_oraria_id_fascia_seq'::regclass)"))
    giorno = Column(Integer, primary_key=True)
    inizio = Column(Time, nullable=False)
    fine = Column(Time, nullable=False)


class Persone(UserMixin, Base, db.Model):
    __tablename__ = 'persone'

    codice_fiscale = Column(String(16), primary_key=True)
    nome = Column(String(50), nullable=False)
    cognome = Column(String(50), nullable=False)
    data_iscrizione = Column(Date, nullable=False)
    residenza = Column(String(50), nullable=False)
    citta = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)
    ruolo = Column(Integer, nullable=False)

        #############
    #__repr__ restituisce un array associativo contentente i valori qui sotto elencati, vedi link per chiarimenti
    #https://stackoverflow.com/questions/57647799/what-is-the-purpose-of-thing-sub-function-returning-repr-with-f-str
    def __repr__(self):
        return self._repr(
                            codice_fiscale = self.codice_fiscale,
                            nome = self.nome,
                            cognome = self.cognome,
                            data_iscrizione = self.data_iscrizione,
                            residenza = self.residenza,
                            citta = self.citta,
                            email = self.email,
                            password = self.password,
                            ruolo = self.ruolo
                          )

    #converte la password da normale ad "hashata"
    def set_password(self, pwd):
        self.password = generate_password_hash(pwd, method = 'sha256', salt_length = 8)

    #controlla l'hash della password
    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)   

    def is_active(self):
        """Vero sel'utente è attivo"""
        return True

    def get_id(self):
        return self.codice_fiscale
    
    def get_role(self):
        return self.ruolo

    def is_authenticated(self):
        """Ritorna true se l'utente è autenticato"""
        return True

    def is_anonymous(self):
        """Ritorna falso, perché gli utenti anonimi non sono supportati"""
        return False

class PolicyOccupazione(Base):
    __tablename__ = 'policy_occupazione'

    data_inizio = Column(Date, primary_key=True, nullable=False)
    data_fine = Column(Date, primary_key=True, nullable=False)
    percentuale_occupabilità = Column(Integer, nullable=False)


class Sale(Base):
    __tablename__ = 'sale'

    id_sala = Column(Integer, primary_key=True)
    posti_totali = Column(Integer, nullable=False)
    solo_attrezzi = Column(Boolean, nullable=False)


class Corsi(Base):
    __tablename__ = 'corsi'

    id_corso = Column(Integer, primary_key=True)
    nome_corso = Column(String(50), nullable=False)
    codice_fiscale_istruttore = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)
    id_tipologia = Column(ForeignKey('tipologie_corsi.id_tipologia'))

    persone = relationship('Persone')
    tipologie_corsi = relationship('TipologieCorsi')

class TipologieCorsi(Base):
    __tablename__ = 'tipologie_corsi'

    id_tipologia = Column(Integer, primary_key=True)
    nome_tipologia = Column(String(50), nullable=False)
    descrizione = Column(Text, nullable=False)


class InfoContatti(Base):
    __tablename__ = 'info_contatti'

    telefono = Column(String(11), primary_key=True)
    descrizione = Column(Enum('Cellulare', 'Casa', 'Altro', name='tipo_numero'), nullable=False)
    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)

    persone = relationship('Persone')


class Prenotazioni(Base):
    __tablename__ = 'prenotazioni'

    data = Column(Date, nullable=False)
    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)
    id_sala = Column(ForeignKey('sale.id_sala'), nullable=False, index=True)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True, server_default=text("nextval('prenotazioni_id_fascia_seq'::regclass)"))
    codice_prenotazione = Column(Integer, primary_key=True)

    persone = relationship('Persone')
    fascia_oraria = relationship('FasciaOraria')
    sale = relationship('Sale')


class SaleCorsi(Base):
    __tablename__ = 'sale_corsi'

    id_sala = Column(ForeignKey('sale.id_sala'), primary_key=True, nullable=False, index=True)
    id_corso = Column(ForeignKey('corsi.id_corso'), primary_key=True, nullable=False, index=True)
    data = Column(Date, primary_key=True, nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), primary_key=True, nullable=False, index=True, server_default=text("nextval('sale_corsi_id_fascia_seq'::regclass)"))

    corsi = relationship('Corsi')
    fascia_oraria = relationship('FasciaOraria')
    sale = relationship('Sale')
