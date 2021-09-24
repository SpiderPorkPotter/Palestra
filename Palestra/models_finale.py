# coding: utf-8
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class FasciaOraria(Base):
    __tablename__ = 'fascia_oraria'

    id_fascia = Column(Integer, primary_key=True)
    inizio = Column(Time, nullable=False)
    fine = Column(Time, nullable=False)


class Persone(Base):
    __tablename__ = 'persone'

    codice_fiscale = Column(String(16), primary_key=True)
    nome = Column(String(50), nullable=False)
    cognome = Column(String(50), nullable=False)
    data_iscrizione = Column(Date, nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(80), nullable=False)


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

    cellulare = Column(String(11), primary_key=True)
    tel_fisso = Column(String(11), nullable=False)
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
