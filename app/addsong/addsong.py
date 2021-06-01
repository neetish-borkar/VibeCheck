from flask import request
from numpy import s_
import soundfile as sf
from os import path, remove
from app.addsong import addsong_bp
from app.fingerprint.fingerprinting import fingerprint
from app.database.database import conn
from app.check.compare import check

def insertDetails(conn, sName, sArtist1, sArtist2 = '', sGenre = ''):
    with conn.cursor() as curr:
        curr.execute(f"""SELECT s_id, s_name, s_artist1, s_artist2, s_genre FROM songs WHERE s_name = '{sName}' AND s_artist1 = '{sArtist1}'""")
        sDetails = curr.fetchall()
        if sDetails != []:
            return (sDetails[0][0], False)
        curr.execute("INSERT INTO songs (s_name, s_artist1, s_artist2, s_genre) VALUES " + f"('{sName}','{sArtist1}','{sArtist2}','{sGenre}')")
        curr.execute(f"SELECT s_id FROM songs WHERE s_name = '{sName}'")
        s_id = curr.fetchone()[0]
        return (s_id, True)

def insertFingerprints(fingerprints, s_id, conn):
    with conn.cursor() as curr:
            args_str = b','.join(curr.mogrify("(decode(%s,'hex'), {},%s)".format(s_id), (x[0], x[1].item())) for x in fingerprints)
            curr.execute(b"INSERT INTO fingerprints (hash, s_id, h_offset) VALUES" + args_str)
            conn.commit()
            

@addsong_bp.route('/addsong', methods = ['POST'])
def addSong():
    file = request.files['file']
    file.save(file.filename)
    Sname = request.form['Sname']
    artist1 = request.form['artist1']
    if request.form['artist2']:
        artist2 = request.form['artist2']
    else:
        artist2 = ''
    if request.form['genre']:
        genre = request.form['genre']
    else:
        genre = ''
    samples, rate = sf.read(file.filename, dtype = 'int16')
    s_id, Status = insertDetails(conn, Sname, artist1, artist2, genre)
    if path.exists(file.filename):
        remove(file.filename)
    if Status == True:
        fingerprints = fingerprint(samples)
        result = check(fingerprints, conn)
        print(result)
        if result['INPUT_CONFIDENCE'] < 0.30:
            insertFingerprints(fingerprints, s_id, conn)
            output = {'s_id': s_id,
                'status': 'Song fingerprints Inserted'}
        else:
            output = {"s_id": result['SONG_ID'],
                'status': 'Song Matched with a song already in the database',
                'song_matched':result}
    else:
        output = {"s_id": s_id,
            'status': 'Song with this name and artist is already in the database'}
    return output
        
