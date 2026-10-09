"""Sport Quiz : sert le jeu + classement partagé (stdlib uniquement)."""
import hashlib
import json
import os
import secrets
import threading
import time
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get('QUIZ_DB', os.path.join(ROOT, 'data', 'scores.json'))
FILES = {'/': ('index.html', 'text/html; charset=utf-8'),
         '/index.html': ('index.html', 'text/html; charset=utf-8')}
# questions/<sport>.json (un fichier par sport ; l'app iOS les télécharge aussi depuis GitHub) et clubs.json (Aventure : clubs de cinq pays et Coupes du monde)
# sont les seules sources ; la page les reçoit sous forme de script pour rester synchrone au chargement.
QUESTIONS_DIR = os.path.join(ROOT, 'questions')
DATA_JS = {'/questions.js': ('QUESTIONS', None), '/clubs.js': ('CLUBS', 'clubs.json')}
MAX_SCORE = {'foot': 32_500, 'multi': 4500, 'hard': 400_000, 'hardfoot': 400_000, 'hardrugby': 400_000, 'hardbasket': 400_000, 'hardtennis': 400_000, 'hardf1': 400_000, 'hardvelo': 400_000, 'hardfr': 400_000, 'hardes': 400_000, 'harduk': 400_000, 'hardde': 400_000, 'hardit': 400_000, 'hardwc': 400_000, 'hardcan': 400_000}  # foot 100 questions (FOOT_PLAN : 100 × (10×1 + 20×2 + 25×3 + 25×4 + 20×5)) / multi 15, max niveau*100 pts ; hard* = sans fin
MAX_GOOD = {'foot': 100, 'multi': 15, 'hard': 400, 'hardfoot': 400, 'hardrugby': 400, 'hardbasket': 400, 'hardtennis': 400, 'hardf1': 400, 'hardvelo': 400, 'hardfr': 400, 'hardes': 400, 'harduk': 400, 'hardde': 400, 'hardit': 400, 'hardwc': 400, 'hardcan': 400}
# Profils web : pseudo + code secret pour retrouver ses badges sur un autre appareil (l'app iOS utilise Game Center).
PROFILES = os.environ.get('QUIZ_PROFILES', os.path.join(os.path.dirname(DB), 'profiles.json'))
CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # sans 0/O ni 1/I, faciles à confondre
BADGES = {'first', 'perfect', 'reflex', 'streak', 'supporter', 'tour', 'liga', 'albion', 'bundes', 'calcio', 'globe', 'marathon', 'multi', 'beast', 'allround',
          'footscore', 'multiscore', 'hard', 'hardfoot', 'hardrugby', 'hardbasket', 'hardtennis', 'hardf1', 'hardvelo', 'mondial', 'memoire', 'hardfr', 'hardes', 'harduk', 'hardde', 'hardit', 'hardwc', 'can', 'canall', 'hardcan'}
MAX_FAILS, LOCK_SECONDS = 8, 15 * 60          # 8 codes faux d'affilée → pseudo bloqué 15 min
fails = {}                                    # pseudo → (codes faux d'affilée, bloqué jusqu'à)
# ponytail: global lock + whole-file JSON rewrite and client-trusted scores, fine for friends; SQLite + server-side scoring if it goes public
lock = threading.Lock()


def read_data(name):
    with open(os.path.join(ROOT, name), 'rb') as f:
        return f.read().rstrip()


def questions_json():
    """Les questions de tous les sports en un objet { sport: [...] }, le sport étant le nom du fichier."""
    sports = sorted(n.removesuffix('.json') for n in os.listdir(QUESTIONS_DIR) if n.endswith('.json'))
    return b'{' + b','.join(json.dumps(s).encode() + b':' + read_data(os.path.join('questions', s + '.json')) for s in sports) + b'}'


def load(path=DB):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def save(db, path=DB):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False)
    os.replace(tmp, path)


def clean_name(v):
    return ' '.join(str(v or '').split())[:16]


def name_key(name):
    """Clé unique d'un pseudo : sans casse, accents, espaces ni ponctuation (« Léa », « lea » et « L.E.A » = une seule place)."""
    s = unicodedata.normalize('NFKD', name).casefold()
    return ''.join(c for c in s if c.isalnum())


def dedupe(db):
    """Fusionne les entrées d'un même pseudo (clés d'avant name_key), en gardant le meilleur score. Renvoie True si modifié."""
    changed = False
    for mode, board in db.items():
        merged = {}
        for p in board.values():
            k = name_key(p['name'])
            if k not in merged or p['score'] > merged[k]['score']:
                merged[k] = p
        if merged.keys() != board.keys():
            db[mode] = merged
            changed = True
    return changed


def hash_code(salt, code):
    return hashlib.sha256((salt + ''.join(c for c in str(code).upper() if c.isalnum())).encode()).hexdigest()


def code_ok(profile, key, code):
    """Vérifie le code d'un profil, avec blocage après trop d'erreurs. Renvoie True, False ou 'bloqué'."""
    n, until = fails.get(key, (0, 0))
    if until > time.time():
        return 'bloqué'
    if secrets.compare_digest(profile['hash'], hash_code(profile['salt'], code)):
        fails.pop(key, None)
        return True
    n += 1
    fails[key] = (0, time.time() + LOCK_SECONDS) if n >= MAX_FAILS else (n, 0)
    return False


def merge_badges(mine, sent):
    """Union des badges, en gardant la date la plus ancienne de chacun."""
    for b, t in (sent or {}).items():
        if b in BADGES and isinstance(t, int) and t > 0:
            mine[b] = min(mine.get(b, t), t)
    return mine


def top(db, mode, n=100):  # 100 premiers affichés au classement
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
        if path in DATA_JS:
            var, name = DATA_JS[path]
            return self.send(200, f'const {var} = '.encode() + (read_data(name) if name else questions_json()) + b';\n', 'text/javascript; charset=utf-8')
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

    def body(self):
        n = int(self.headers.get('Content-Length', 0))
        if not 0 < n <= 1000:
            raise ValueError
        d = json.loads(self.rfile.read(n))
        if not isinstance(d, dict):
            raise ValueError
        return d

    def do_POST(self):
        if self.path in ('/api/profile/create', '/api/profile/sync'):
            return self.profile()
        if self.path != '/api/scores':
            return self.send(404, {'error': 'introuvable'})
        try:
            d = self.body()
            name = clean_name(d.get('name'))
            score = int(d.get('score', -1))
            good = int(d.get('good', 0))
            mode = d.get('mode')
            if not name_key(name) or mode not in MAX_SCORE or not 0 <= score <= MAX_SCORE[mode] or not 0 <= good <= MAX_GOOD[mode]:
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            return self.send(400, {'error': 'requête invalide'})
        key = name_key(name)
        with lock:
            profile = load(PROFILES).get(key)
            if profile:  # pseudo protégé : il faut son code
                ok = code_ok(profile, key, d.get('code', ''))
                if ok is not True:
                    return self.send(429 if ok == 'bloqué' else 403, {'error': 'pseudo protégé par un code'})
            db = load()
            board = db.setdefault(mode, {})
            p = board.get(key)
            if not p or score > p['score']:  # on garde le meilleur score par pseudo
                board[key] = {'name': name, 'score': score, 'good': good, 'date': int(time.time())}
                save(db)
            rows = top(db, mode)
        self.send(200, rows)


    def profile(self):
        try:
            d = self.body()
            name = clean_name(d.get('name'))
            if not name_key(name):
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            return self.send(400, {'error': 'requête invalide'})
        key = name_key(name)
        with lock:
            profiles = load(PROFILES)
            p = profiles.get(key)
            if self.path == '/api/profile/create':
                if p:
                    return self.send(409, {'error': 'pseudo déjà pris'})
                code = ''.join(secrets.choice(CODE_CHARS) for _ in range(6))
                salt = secrets.token_hex(8)
                p = profiles[key] = {'name': name, 'salt': salt, 'hash': hash_code(salt, code), 'badges': {}, 'date': int(time.time())}
                merge_badges(p['badges'], d.get('badges'))
                save(profiles, PROFILES)
                return self.send(200, {'name': name, 'code': code[:3] + '-' + code[3:], 'badges': p['badges']})
            # sync : retrouver son profil (pseudo + code) et fusionner les badges gagnés sur cet appareil
            if not p:
                return self.send(404, {'error': 'profil inconnu'})
            ok = code_ok(p, key, d.get('code', ''))
            if ok is not True:
                return self.send(429 if ok == 'bloqué' else 403, {'error': 'code incorrect'})
            before = dict(p['badges'])
            merge_badges(p['badges'], d.get('badges'))
            if p['badges'] != before:
                save(profiles, PROFILES)
            return self.send(200, {'name': p['name'], 'badges': p['badges']})


if __name__ == '__main__':
    db, profiles = load(), load(PROFILES)  # anciennes clés (minuscules seulement) → name_key
    if dedupe(db):
        save(db)
    if any(k != name_key(p['name']) for k, p in profiles.items()):
        save({name_key(p['name']): p for p in profiles.values()}, PROFILES)
    ThreadingHTTPServer(('', int(os.environ.get('PORT', 8000))), Handler).serve_forever()
