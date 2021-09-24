# coding: utf-8
#generato con sqlacodegen postgresql://postgres:a@localhost/Palestra --outfile modelsv_finale.py
#a è la password del mio db
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from . import db



Base = declarative_base()
metadata = Base.metadata

login_manager = LoginManager()

class FasciaOraria(Base):
    __tablename__ = 'fascia_oraria'

    id_fascia = Column(Integer, primary_key=True)
    inizio = Column(Time, nullable=False)
    fine = Column(Time, nullable=False)


class Persone(UserMixin, Base, db.Model):
    __tablename__ = 'persone'

    codice_fiscale = Column(String(16), primary_key=True)
    nome = Column(String(50), nullable=False)
    cognome = Column(String(50), nullable=False)
    data_iscrizione = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)

    #############
    #__repr__ restituisce un array associativo contentente i valori qui sotto elencati, vedi link per chiarimenti
    #https://stackoverflow.com/questions/57647799/what-is-the-purpose-of-thing-sub-function-returning-repr-with-f-str
    def __repr__(self):
        return self._repr(
                            codice_fiscale = self.codice_fiscale,
                            nome = self.nome,
                            cognome = self.cognome,
                            data_iscrizione = self.data_iscrizione,
                            telefono = self.telefono,
                            email = self.email,
                            password = self.password,
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

    def is_authenticated(self):
        """Ritorna true se l'utente è autenticato"""
        return True

    def is_anonymous(self):
        """Ritorna falso, perché gli utenti anonimi non sono supportati"""
        return False


class Ruoli(Persone):
    __tablename__ = 'ruoli'

    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), primary_key=True, index=True)
    is_istruttore = Column(Boolean, nullable=False)
    is_responsabile = Column(Boolean, nullable=False)


class Sale(Base):
    __tablename__ = 'sale'

    id_sala = Column(Integer, primary_key=True)
    posti_totali = Column(Integer, nullable=False)
    solo_attrezzi = Column(Boolean, nullable=False)


class Corsi(Base):
    __tablename__ = 'corsi'

    nome_corso = Column(String(50), nullable=False)
    max_partecipanti = Column(Integer, nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True)
    id_sala = Column(ForeignKey('sale.id_sala'), nullable=False, index=True)
    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)
    id_corso = Column(Integer, primary_key=True)

    persone = relationship('Persone')
    fascia_oraria = relationship('FasciaOraria')
    sale = relationship('Sale')


class GiorniSettimana(Base):
    __tablename__ = 'giorni_settimana'

    giorno = Column(Integer, primary_key=True, nullable=False)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), primary_key=True, nullable=False, index=True)
    mese = Column(Integer, nullable=False)

    fascia_oraria = relationship('FasciaOraria')


class InfoContatti(Base):
    __tablename__ = 'info_contatti'

    cellulare = Column(String(11), primary_key=True, nullable=False)
    tel_fisso = Column(String(11), nullable=True)
    residenza = Column(String(50), nullable=False)
    città = Column(String(50), nullable=False)
    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)

    persone = relationship('Persone')


class PolicyOccupazione(Base):
    __tablename__ = 'policy_occupazione'

    data_inizio = Column(Date, primary_key=True, nullable=False)
    data_fine = Column(Date, primary_key=True, nullable=False)
    percentuale_occupabilità = Column(Integer, nullable=False)
    id_sala = Column(ForeignKey('sale.id_sala'), nullable=False, index=True)

    sale = relationship('Sale')


class Prenotazioni(Base):
    __tablename__ = 'prenotazioni'

    data = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    codice_fiscale = Column(ForeignKey('persone.codice_fiscale'), nullable=False, index=True)
    id_sala = Column(ForeignKey('sale.id_sala'), nullable=False, index=True)
    id_corso = Column(ForeignKey('corsi.id_corso'), nullable=False, index=True)
    id_fascia = Column(ForeignKey('fascia_oraria.id_fascia'), nullable=False, index=True)
    codice_prenotazione = Column(Integer, primary_key=True)

    persone = relationship('Persone')
    corsi = relationship('Corsi')
    fascia_oraria = relationship('FasciaOraria')
    sale = relationship('Sale')
