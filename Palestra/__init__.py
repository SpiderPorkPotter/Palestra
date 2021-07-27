"""
The flask application package.
"""
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

#psycopg2 è il driver che si usaper comunicare col database


app = Flask(__name__)

#psycopg2 è il driver che si usa per comunicare col database
DB_URI = "postgresql+psycopg2://postgres:a@localhost/Palestra"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'

#usato per inizializzare l'applicazione per essere usata con questo
#setup di database
db.init_app(app)


#questi import vanno qua sotto perché app è stata creata
#mettendoli in alto assieme agli altri, non funzionerebbero
#perché app non esisterebbe ancora
import Palestra.views
#import Palestra.models
import Palestra.modelsv2
