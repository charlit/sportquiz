"""Sport Quiz : sert le jeu + classement partagé (stdlib uniquement)."""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get('QUIZ_DB', os.path.join(ROOT, 'data', 'scores.json'))
FILES = {'/': ('index.html', 'text/html; charset=utf-8'),
         '/index.html': ('index.html', 'text/html; charset=utf-8'),
         '/questions.json': ('questions.json', 'application/json; charset=utf-8')}
# questions.json est la seule source des questions (l'app iOS le télécharge aussi depuis GitHub) ;
# la page web le reçoit sous forme de script pour rester synchrone au chargement.
QUESTIONS_JSON = os.path.join(ROOT, 'questions.json')
MAX_SCORE = {'foot': 30_000, 'multi': 4500, 'hard': 400_000, 'hardfoot': 400_000, 'hardrugby': 400_000, 'hardbasket': 400_000, 'hardtennis': 400_000, 'hardf1': 400_000, 'hardvelo': 400_000}  # foot 100 questions / multi 15, max niveau*100 pts ; hard* = sans fin
MAX_GOOD = {'foot': 100, 'multi': 15, 'hard': 400, 'hardfoot': 400, 'hardrugby': 400, 'hardbasket': 400, 'hardtennis': 400, 'hardf1': 400, 'hardvelo': 400}
# ponytail: global lock + whole-file JSON rewrite and client-trusted scores, fine for friends; SQLite + server-side scoring if it goes public
lock = threading.Lock()


def load():
    try:
        with open(DB, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def save(db):
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    tmp = DB + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False)
    os.replace(tmp, DB)


def top(db, mode, n=20):
    rows = sorted(db.get(mode, {}).values(), key=lambda p: (-p['score'], p['date']))
    return rows[:n]


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype='application/json'):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path, _, query = self.path.partition('?')
        if path == '/questions.js':
            with open(QUESTIONS_JSON, 'rb') as f:
                return self.send(200, b'const QUESTIONS = ' + f.read().rstrip() + b';\n', 'text/javascript; charset=utf-8')
        if path in FILES:
            name, ctype = FILES[path]
            with open(os.path.join(ROOT, name), 'rb') as f:
                return self.send(200, f.read(), ctype)
        if path == '/api/scores':
            mode = query.removeprefix('mode=')
            if mode not in MAX_SCORE:
                return self.send(400, {'error': 'mode inconnu'})
            return self.send(200, top(load(), mode))
        self.send(404, {'error': 'introuvable'})

    def do_POST(self):
        if self.path != '/api/scores':
            return self.send(404, {'error': 'introuvable'})
        try:
            n = int(self.headers.get('Content-Length', 0))
            if not 0 < n <= 1000:
                raise ValueError
            d = json.loads(self.rfile.read(n))
            name = ' '.join(str(d.get('name', '')).split())[:16]
            score = int(d.get('score', -1))
            good = int(d.get('good', 0))
            mode = d.get('mode')
            if not name or mode not in MAX_SCORE or not 0 <= score <= MAX_SCORE[mode] or not 0 <= good <= MAX_GOOD[mode]:
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            return self.send(400, {'error': 'requête invalide'})
        key = name.lower()
        with lock:
            db = load()
            board = db.setdefault(mode, {})
            p = board.get(key)
            if not p or score > p['score']:  # on garde le meilleur score par pseudo
                board[key] = {'name': name, 'score': score, 'good': good, 'date': int(time.time())}
                save(db)
            rows = top(db, mode)
        self.send(200, rows)


if __name__ == '__main__':
    ThreadingHTTPServer(('', int(os.environ.get('PORT', 8000))), Handler).serve_forever()
