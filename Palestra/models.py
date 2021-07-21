# coding: utf-8
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Table, Time
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
    telefono = Column(Integer, nullable=False)
    is_istruttore = Column(Boolean, nullable=False)
    email = Column(String(50), nullable=False)
    passwd = Column(String(50), nullable=False)
    grado_accesso = Column(Integer, nullable=False)

    palestre = relationship('Palestre', secondary='palestre_persone')


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
