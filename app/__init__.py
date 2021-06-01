from app.addsong import addsong
from flask import Flask

app = Flask(__name__)

from app.fingerprint import fingerprint_bp
from app.addsong import addsong_bp
from app.check import check_bp

app.register_blueprint(fingerprint_bp)
app.register_blueprint(addsong_bp)
app.register_blueprint(check_bp)

from app import app
