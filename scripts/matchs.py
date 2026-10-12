"""Met à jour matchs.json : les grosses affiches des 8 prochains jours entre deux clubs de clubs.json
(Ligue 1, Liga, Premier League, Bundesliga, Serie A, Ligue des champions), d'après football-data.org.
Lancé par le robot GitHub (.github/workflows/matchs.yml) avec la clé FOOTBALL_DATA_KEY ; sans clé, ne change rien."""
import datetime
import json
import os
import sys
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPETITIONS = {'FL1': 'Ligue 1', 'PD': 'Liga', 'PL': 'Premier League', 'BL1': 'Bundesliga', 'SA': 'Serie A', 'CL': 'Ligue des champions'}
# Mots qui suffisent à reconnaître chaque club dans les noms officiels (« Paris Saint-Germain FC », « FC Internazionale Milano »…).
# En cas de doute, le nom le plus précis l'emporte (« Paris FC » ne prend pas le PSG) ; « FC Barcelona » et pas « RCD Espanyol de Barcelona ».
ALIASES = {
    'psg': ['paris saint germain'], 'om': ['marseille'], 'ol': ['lyonnais', 'lyon'], 'lens': ['lens'], 'losc': ['lille'],
    'rennes': ['rennais', 'rennes'], 'monaco': ['monaco'], 'nice': ['nice'], 'rcsa': ['strasbourg'], 'tfc': ['toulouse'],
    'aja': ['auxerre'], 'lorient': ['lorient'], 'brest': ['brestois', 'brest'], 'sco': ['angers'], 'hac': ['le havre'],
    'pfc': ['paris fc'], 'estac': ['troyes'], 'lemans': ['le mans'],
    'real': ['real madrid'], 'barca': ['fc barcelona'], 'atleti': ['atletico'], 'sevilla': ['sevilla'], 'betis': ['betis'],
    'valencia': ['valencia'], 'athletic': ['athletic'], 'realsoc': ['real sociedad'], 'villarreal': ['villarreal'], 'celta': ['celta'],
    'manutd': ['manchester united', 'man united'], 'mancity': ['manchester city', 'man city'], 'liverpool': ['liverpool'],
    'everton': ['everton'], 'arsenal': ['arsenal'], 'chelsea': ['chelsea'], 'spurs': ['tottenham'], 'newcastle': ['newcastle'],
    'celtic': ['celtic'], 'rangers': ['rangers'],
    'bayern': ['bayern'], 'bvb': ['dortmund'], 'b04': ['leverkusen'], 'hertha': ['hertha'], 'vfb': ['stuttgart'],
    'sge': ['frankfurt'], 'bmg': ['monchengladbach', 'gladbach'], 'werder': ['werder', 'bremen'], 'hsv': ['hamburger', 'hamburg'],
    's04': ['schalke'],
    'juve': ['juventus'], 'inter': ['internazionale', 'inter'], 'milan': ['ac milan', 'milan'], 'napoli': ['napoli'], 'roma': ['roma'],
    'lazio': ['lazio'], 'atalanta': ['atalanta'], 'fiorentina': ['fiorentina'], 'bologna': ['bologna'], 'parma': ['parma'],
}


def words(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return set(''.join(c if c.isalnum() else ' ' for c in s).split())


def club_of(team):
    """Identifiant clubs.json d'une équipe football-data, ou None. Le nom le plus précis (le plus de mots) gagne."""
    names = words(team.get('name')) | words(team.get('shortName'))
    best = max(((len(a.split()), cid) for cid, al in ALIASES.items() for a in al if set(a.split()) <= names), default=None)
    return best and best[1]


def main():
    key = os.environ.get('FOOTBALL_DATA_KEY')
    if not key:
        print('Pas de clé FOOTBALL_DATA_KEY : matchs.json inchangé.')
        return
    today = datetime.datetime.now(datetime.timezone.utc).date()
    url = (f'https://api.football-data.org/v4/matches?competitions={",".join(COMPETITIONS)}'
           f'&dateFrom={today}&dateTo={today + datetime.timedelta(days=8)}')
    with urllib.request.urlopen(urllib.request.Request(url, headers={'X-Auth-Token': key}), timeout=30) as r:
        data = json.load(r)
    clubs = json.load(open(os.path.join(ROOT, 'clubs.json'), encoding='utf-8'))
    out, unknown = [], set()
    for m in data.get('matches', []):
        if m.get('status') not in ('SCHEDULED', 'TIMED'):
            continue
        home, away = club_of(m['homeTeam']), club_of(m['awayTeam'])
        for team, cid in ((m['homeTeam'], home), (m['awayTeam'], away)):
            if not cid:
                unknown.add(team.get('name'))
        if home in clubs and away in clubs and home != away:
            out.append({'id': m['id'], 'date': m['utcDate'], 'comp': COMPETITIONS.get(m['competition']['code'], m['competition']['name']),
                        'dom': home, 'ext': away})
    out.sort(key=lambda x: x['date'])
    with open(os.path.join(ROOT, 'matchs.json'), 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join('  ' + json.dumps(x, ensure_ascii=False) for x in out) + ('\n' if out else '') + ']\n')
    print(f'{len(out)} grosses affiches ; équipes non reconnues (petits clubs, normal) : {len(unknown)}')


if __name__ == '__main__':
    sys.exit(main())
