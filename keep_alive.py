import logging
from flask import Flask
from threading import Thread
from waitress import serve

app = Flask('')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "Bot is alive"

def run():
    # Use a production-grade WSGI server instead of Flask's dev server so the
    # platform's health check gets a fast, reliable response even under load.
    serve(app, host='0.0.0.0', port=8080, threads=4)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
