"""
The flask application package.
"""
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

#db = SQLAlchemy()

app = Flask(__name__)

#db.init_app(app)

import Palestra.views, Palestra.models
