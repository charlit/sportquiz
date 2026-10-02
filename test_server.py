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
assert call('/api/scores', {'name': 'Max', 'mode': 'foot', 'score': 9999, 'good': 15})[0] == 400   # au-dessus du max
assert call('/api/scores', {'name': '  ', 'mode': 'foot', 'score': 100, 'good': 1})[0] == 400
assert call('/api/scores', {'name': 'Max', 'mode': 'golf', 'score': 100, 'good': 1})[0] == 400
assert call('/api/scores', {'name': 'Max', 'mode': 'foot', 'score': 1200, 'good': 8})[0] == 200
assert call('/api/scores', {'name': 'max', 'mode': 'foot', 'score': 500, 'good': 4})[1][0]['score'] == 1200  # garde le meilleur
code, rows = call('/api/scores', {'name': 'Léa', 'mode': 'foot', 'score': 3000, 'good': 13})
assert [r['name'] for r in rows] == ['Léa', 'Max']
assert call('/api/scores?mode=multi') == (200, [])                    # classements séparés
print('ok')
assert call('/api/scores', {'name': 'Max', 'mode': 'hard', 'score': 9999, 'good': 20})[0] == 200  # hard : pas plafonné à 4500
assert call('/api/scores', {'name': 'Max', 'mode': 'hard', 'score': 999999, 'good': 20})[0] == 400
print('ok hard')
assert call('/api/scores', {'name': 'Max', 'mode': 'hardrugby', 'score': 2000, 'good': 5})[0] == 200
assert call('/api/scores?mode=hardfoot') == (200, [])
print('ok hardcore')
