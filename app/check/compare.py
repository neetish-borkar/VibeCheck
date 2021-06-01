from itertools import groupby
import operator
from typing import List, Tuple, Dict
from app.fingerprint.fingerprinting import fingerprint

def return_matches(hashes: List[Tuple[str, int]], conn, batch_size: int = 1000) -> Tuple[List[Tuple[int,int]], Dict[int,int]]:
    hashmap = {} #{hash: [offset,offset,,offset...],hash: [offset,offset,,offset...]...}
    for hsh, offset in hashes:
        if hsh in hashmap.keys():
            hashmap[hsh].append(offset)
        else:
            hashmap[hsh] = [offset]
    values = list(hashmap.keys())
    dedup_hashes = {} #{sid: count,sid:count...}
    result = [] #[(sid,db_offset-query_offset),(sid,db_offset-query_offset)...]
    with conn.cursor() as curr:
        for index in range (0,len(values),batch_size):
            query = f"""
                SELECT encode(hash, 'hex'), s_id, h_offset
                FROM fingerprints
                WHERE hash IN (%s);""" % ', '.join([f"decode(%s, 'hex')"] * len(values[index: index + batch_size]))
            curr.execute(query,values[index:index + batch_size])
            for hsh, sid, db_offset in curr:
                if sid not in dedup_hashes.keys():
                    dedup_hashes[sid] = 1
                else:
                    dedup_hashes[sid] += 1
                for query_offset in hashmap[hsh]:
                    result.append((sid,db_offset-query_offset))
        return result, dedup_hashes

def align_matches(matches: List[Tuple[int, int]], dedup_hashes: Dict[str, int], queried_hashes: int, conn, topn: int = 10) -> List[Dict[str, any]]:
    sorted_matches = sorted(matches, key=lambda m: (m[0], m[1])) #Sorted according to sid and then difference in offset
    counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=lambda m: (m[0], m[1]))] #(sid, difference in offset, count) 
    songs_matches = sorted(
        [max(list(group), key=lambda g: g[2]) for key, group in groupby(counts, key=lambda count: count[0])],
        key=lambda count: count[2], reverse=True
    )
    songs_result = []
    for song_id, offset, _ in songs_matches[0:topn]:  # consider top n sids in the result
        with conn.cursor() as curr:
            curr.execute(f"SELECT s_name, s_artist1 FROM songs WHERE s_id = {song_id};")
            song_details = curr.fetchone()
            song_name = song_details[0]
            song_artist = song_details[1]
            hashes_matched = dedup_hashes[song_id]

            song = {
                'SONG_ID': song_id,
                'SONG_NAME': song_name,
                'SONG_ARTIST': song_artist,
                'INPUT_HASHES': queried_hashes,
                'HASHES_MATCHED': hashes_matched,
                'INPUT_CONFIDENCE': round(hashes_matched / queried_hashes, 2),
            }
            songs_result.append(song)
    return songs_result

def check(fingerprints: List[Tuple[str, int]], conn) -> Dict[str, any]:
    matches, dedup_hashes = return_matches(fingerprints, conn)
    aligned_matches = align_matches(matches, dedup_hashes, len(fingerprints), conn, 1)
    if aligned_matches != []:
        return(aligned_matches[0])
    else:
        nm = 'Not Matched'
        return({'SONG_ID': -1,
                'SONG_NAME': nm,
                'SONG_ARTIST': nm,
                'INPUT_HASHES': len(fingerprints),
                'HASHES_MATCHED': 0,
                'INPUT_CONFIDENCE': 0,
            })

def generate_segments(audio: List[int], rate: int, segment_size: int) -> List[List[int]]:
    segmented_audio = []
    for i in range(0,len(audio), segment_size*rate):
        segmented_audio.append(audio[i:i+segment_size*rate])
    return (segmented_audio)


def check_segments(audio: List[int], rate: int, conn) -> List[Dict[str,any]]:
    segments = generate_segments(audio, rate, 3)
    segment_result = []
    only_matched_segment_result = []
    for segment in segments:
        fingerprints = fingerprint(segment)
        matches, dedup_hashes = return_matches(fingerprints, conn)
        aligned_matches = align_matches(matches, dedup_hashes, len(fingerprints), conn, 1)
        if aligned_matches != []:
            if aligned_matches[0]['INPUT_CONFIDENCE'] > 0.49:
                aligned_matches[0]['CLASS'] = 'red'
            elif aligned_matches[0]['INPUT_CONFIDENCE'] > 0.2:
                aligned_matches[0]['CLASS'] = 'yellow'
            elif aligned_matches[0]['INPUT_CONFIDENCE'] <= 0.2 :
                aligned_matches[0]['CLASS'] = 'green'
            segment_result.append(aligned_matches[0])
            only_matched_segment_result.append(aligned_matches[0])
        else:
            nm = 'Not Matched'
            segment_result.append({
                'SONG_ID': -1,
                'SONG_NAME': nm,
                'SONG_ARTIST': nm,
                'INPUT_HASHES': len(fingerprints),
                'HASHES_MATCHED': 0,
                'INPUT_CONFIDENCE': 0,
                'CLASS': 'green'
            })
    # sorted_segment_result = sorted(segment_result, key = lambda i: (i['SONG_ID'], i['INPUT_CONFIDENCE']))
    # grouped_result = [list(group) for i, group in groupby(sorted_segment_result, key = operator.itemgetter('SONG_ID'))]
    # final_result = []
    fingerprints = fingerprint(audio)
    matches, dedup_hashes = return_matches(fingerprints, conn)
    aligned_matches = align_matches(matches, dedup_hashes, len(fingerprints), conn, 1)
    final_result = aligned_matches[0]
    # for group in grouped_result:
    #     if group[0]['SONG_ID'] != -1:
    #         hashes_matched = sum([i['HASHES_MATCHED'] for i in group])
    #         queried_hashes = sum([i['INPUT_HASHES'] for i in group])
    #         final_result.append({
    #             'SONG_ID': group[0]['SONG_ID'],
    #             'SONG_NAME': group[0]['SONG_NAME'],
    #             'SONG_ARTIST': group[0]['SONG_ARTIST'],
    #             'INPUT_HASHES': queried_hashes,
    #             'HASHES_MATCHED': hashes_matched,
    #             'INPUT_CONFIDENCE': round(hashes_matched/queried_hashes, 2)
    #         })
    #     else:
    #         continue
    # final_result = sorted(final_result, key = lambda i: i['INPUT_CONFIDENCE'])
    return ({'result': final_result,
        'segment_result': segment_result})

