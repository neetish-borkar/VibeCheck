from flask import request
import soundfile as sf
from os import path, remove
from app.fingerprint import fingerprint_bp
from app.fingerprint.fingerprinting import fingerprint

@fingerprint_bp.route('/fingerprint', methods = ['GET'])
def gen_fingerprints():
    file = request.files['file']
    file.save(file.filename)
    samples, rate = sf.read(file.filename, dtype = 'int16')
    fingerprints = fingerprint(samples)
    if path.exists(file.filename):
        remove(file.filename)
    return {"fingerprints" : fingerprints}
    