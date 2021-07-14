"""
This script runs the Palestra application using a development server.
"""

from logging import debug
from os import environ
from Palestra import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
        """ il flag debug true vuol dire che dopo ogni modifica del codice la applicazione il web server si riavvia """
    app.run(HOST, PORT, debug=True )
    