from flask import Blueprint

fingerprint_bp = Blueprint('fingerprint', __name__)

from app.fingerprint import routes_fingerprint
