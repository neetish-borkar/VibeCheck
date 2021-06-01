from flask import Blueprint

check_bp = Blueprint('compare', __name__)

from app.check import check
