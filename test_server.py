import json
import os
import tempfile
import threading
import urllib.error
import urllib.request

os.environ['QUIZ_DB'] = os.path.join(tempfile.mkdtemp(), 'scores.json')
import server  # noqa: E402

srv = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{srv.server_address[1]}'


def call(path, body=None):
    req = urllib.request.Request(URL + path, json.dumps(body).encode() if body else None,
                                 {'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


assert call('/api/scores?mode=foot') == (200, [])
assert call('/api/scores?mode=golf')[0] == 400
assert call('/api/scores', {'name': 'Max', 'mode': 'foot', 'score': 99999, 'good': 15})[0] == 400   # au-dessus du max (30 000)
assert call('/api/scores', {'name': '  ', 'mode': 'foot', 'score': 100, 'good': 1})[0] == 400
assert call('/api/scores', {'name': 'Max', 'mode': 'golf', 'score': 100, 'good': 1})[0] == 400
assert call('/api/scores', {'name': 'Max', 'mode': 'foot', 'score': 1200, 'good': 8})[0] == 200
assert call('/api/scores', {'name': 'max', 'mode': 'foot', 'score': 500, 'good': 4})[1][0]['score'] == 1200  # garde le meilleur
code, rows = call('/api/scores', {'name': 'Léa', 'mode': 'foot', 'score': 3000, 'good': 13})
assert [r['name'] for r in rows] == ['Léa', 'Max']
assert call('/api/scores?mode=multi') == (200, [])                    # classements séparés
print('ok')
assert call('/api/scores', {'name': 'Max', 'mode': 'hard', 'score': 9999, 'good': 20})[0] == 200  # hard : pas plafonné à 4500
assert call('/api/scores', {'name': 'Max', 'mode': 'hard', 'score': 9999999, 'good': 20})[0] == 400
print('ok hard')
assert call('/api/scores', {'name': 'Max', 'mode': 'hardrugby', 'score': 2000, 'good': 5})[0] == 200
assert call('/api/scores?mode=hardfoot') == (200, [])
assert call('/api/scores', {'name': 'Max', 'mode': 'hardit', 'score': 2500, 'good': 4})[0] == 200  # Hardcore par pays
assert call('/api/scores', {'name': 'Ève Lu', 'mode': 'hardes', 'score': 900, 'good': 3})[0] == 200
assert call('/api/scores', {'name': 'eve-lu', 'mode': 'hardes', 'score': 500, 'good': 2})[0] == 200   # même pseudo, moins bien : gardé
rows = call('/api/scores', {'name': 'EVE LU', 'mode': 'hardes', 'score': 1200, 'good': 4})[1]     # même pseudo, mieux : remplace
assert [(r['name'], r['score']) for r in rows] == [('EVE LU', 1200)]                           # une seule ligne par pseudo
assert call('/api/scores', {'name': '!!!', 'mode': 'hardes', 'score': 1, 'good': 0})[0] == 400
assert server.dedupe(d := {'foot': {'léa': {'name': 'Léa', 'score': 5, 'date': 1}, 'lea': {'name': 'lea', 'score': 9, 'date': 2}}}) and list(d['foot'].values())[0]['score'] == 9
assert call('/api/scores', {'name': 'Max', 'mode': 'hardwc', 'score': 2500, 'good': 4})[0] == 200  # Hardcore Coupe du monde
print('ok hardcore')
assert call('/api/scores', {'name': 'Max', 'mode': 'hardbasket', 'score': 3000, 'good': 6})[0] == 200
assert call('/api/scores?mode=hardbasket')[1][0]['name'] == 'Max'
print('ok basket')
assert call('/api/scores', {'name': 'Cent', 'mode': 'foot', 'score': 25000, 'good': 95})[0] == 200   # Spécial Foot : 100 questions
assert call('/api/scores', {'name': 'Cent', 'mode': 'multi', 'score': 25000, 'good': 15})[0] == 400  # multi reste plafonné
print('ok foot 100')
for m in ('hardtennis', 'hardf1', 'hardvelo'):
    assert call('/api/scores', {'name': 'Max', 'mode': m, 'score': 1500, 'good': 3})[0] == 200
print('ok tennis f1 velo')
with urllib.request.urlopen(URL + '/questions.js') as r:  # questions.js fabriqué depuis questions.json
    js = r.read().decode()
assert js.startswith('const QUESTIONS = {') and js.rstrip().endswith('};')
assert json.loads(js.removeprefix('const QUESTIONS = ').rstrip().rstrip(';')) == json.load(open(os.path.join(os.path.dirname(server.__file__), 'questions.json'), encoding='utf-8'))
print('ok questions.js')
with urllib.request.urlopen(URL + '/clubs.js') as r:  # clubs.js fabriqué depuis clubs.json (Aventure : France, Espagne, Royaume-Uni, Allemagne, Italie, Mondial)
    js = r.read().decode()
clubs = json.loads(js.removeprefix('const CLUBS = ').rstrip().rstrip(';'))
assert sorted(sum(c['pays'] == p for c in clubs.values()) for p in ('fr', 'es', 'uk', 'de', 'it')) == [10, 10, 10, 10, 18] and all(sum(q[0] == k for q in c['q']) >= 5 for c in clubs.values() if c['pays'] != 'wc' for k in range(1, 11))
wc = [c for c in clubs.values() if c['pays'] == 'wc']   # Mondial : 22 éditions (1930-2022), 5 étapes de 5 questions au moins
assert sorted(c['annee'] for c in wc) == [y for y in range(1930, 2023, 4) if y not in (1942, 1946)] and all(sum(q[0] == k for q in c['q']) >= 5 for c in wc for k in range(1, 6))
assert all(len(q) == 6 and len(set(q[2:])) == 4 for c in clubs.values() for q in c['q'])                  # 4 réponses distinctes
texts = [q[1] for c in wc for q in c['q']]
assert len(texts) == len(set(texts))                                                                      # intitulés uniques (questions vues retenues par leur texte)
print('ok clubs.js')
# profils web : pseudo + code
st, p = call('/api/profile/create', {'name': 'Zoé', 'badges': {'first': 1700000000, 'triche': 5}})
assert st == 200 and len(p['code']) == 7 and p['badges'] == {'first': 1700000000}   # badge inconnu ignoré
code = p['code']
assert call('/api/profile/create', {'name': 'zoé'})[0] == 409                      # pseudo déjà pris
assert call('/api/profile/sync', {'name': 'Zoé', 'code': 'AAA-AAA'})[0] == 403
st, p = call('/api/profile/sync', {'name': 'ZOÉ', 'code': code.lower().replace('-', ''), 'badges': {'first': 1800000000, 'reflex': 1750000000, 'globe': 1760000000}})
assert st == 200 and p['name'] == 'Zoé' and p['badges'] == {'first': 1700000000, 'reflex': 1750000000, 'globe': 1760000000}  # fusion, date la plus ancienne
assert call('/api/profile/sync', {'name': 'Personne', 'code': code})[0] == 404
# pseudo protégé au classement
for i in range(105):
    call('/api/scores', {'name': f'J{i}', 'mode': 'hardfoot', 'score': 10 + i, 'good': 1})
rows = call('/api/scores?mode=hardfoot')[1]
assert len(rows) == 100 and rows[0]['name'] == 'J104'   # classement : les 100 premiers
print('ok top 100')
assert call('/api/scores', {'name': 'Zoé', 'mode': 'foot', 'score': 100, 'good': 1})[0] == 403
assert call('/api/scores', {'name': 'Zoé', 'mode': 'foot', 'score': 100, 'good': 1, 'code': code})[0] == 200
# trop de codes faux : bloqué, même avec le bon code
for _ in range(server.MAX_FAILS):
    call('/api/profile/sync', {'name': 'Zoé', 'code': 'BBB-BBB'})
assert call('/api/profile/sync', {'name': 'Zoé', 'code': code})[0] == 429
print('ok profils')

