from flask import Blueprint

addsong_bp = Blueprint('addsong', __name__)

from app.addsong import addsong
