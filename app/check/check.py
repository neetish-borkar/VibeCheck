from flask import request
from app.check.compare import *
from os import path, remove
import soundfile as sf
from app.check import check_bp
from app.check.compare import *
from app.fingerprint.fingerprinting import fingerprint
from app.database.database import conn

@check_bp.route('/check', methods = ['GET'])
def check():
    file = request.files['file']
    file.save(file.filename)
    samples, rate = sf.read(file.filename, dtype = 'int16')
    result = check_segments(samples,rate, conn)
    if path.exists(file.filename):
        remove(file.filename)
    return (result)

    
