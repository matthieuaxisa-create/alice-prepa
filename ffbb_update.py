import json, sys
from datetime import datetime, timezone

URL = 'https://competitions.ffbb.com/competitions/nfu18-elite-b'
KEYS = {'LA SEYNE BASKET - 1': 'LSB', 'LA SEYNE BASKET': 'LSB', 'UNION SPORTIVE ASM BEAUMONT BASKET-BALL': 'BEA', 'ST CHAMOND BASKET VALLEE DU GIER': 'STC', 'CANET RBC': 'CRB', 'MONACO BASKET ASSOCIATION': 'MON', 'ST GENIS OULLINS STE FOY FEMININ': 'SGO'}

html = sys.stdin.read()
chunks = [p.split('"])')[0] for p in html.split('self.__next_f.push([1,"')[1:]]
flight = ''.join(chunks).encode('latin-1', 'ignore').decode('unicode_escape')
dec = json.JSONDecoder()

def arrays(key):
    out, i, tag = [], 0, '"' + key + '":['
    while True:
        i = flight.find(tag, i)
        if i < 0:
            return out
        out.append(dec.raw_decode(flight, i + len(tag) - 1)[0])
        i += len(tag)

matches = {}
for arr in arrays('rencontres'):
    for r in arr:
        if (r.get('idPoule') or {}).get('nom') != 'Poule A':
            continue
        s1, s2 = r.get('resultatEquipe1'), r.get('resultatEquipe2')
        played = bool(r.get('joue')) and s1 not in (None, '') and s2 not in (None, '')
        matches[r['id']] = {'d': r['date_rencontre'][:16], 'h': KEYS.get(r['nomEquipe1']), 'a': KEYS.get(r['nomEquipe2']), 'sh': int(s1) if played else None, 'sa': int(s2) if played else None}

if len(matches) != 30 or any(not v['h'] or not v['a'] for v in matches.values()):
    sys.exit('ERREUR : ' + str(len(matches)) + ' matchs de poule A trouves (30 attendus) ou equipe inconnue')

standings = {}
for arr in arrays('classements'):
    for t in arr:
        k = KEYS.get((t.get('idEngagement') or {}).get('nom', ''))
        if k:
            standings[k] = {'t': k, 'pts': int(t['points']), 'j': int(t['matchJoues']), 'v': int(t['gagnes']), 'd': int(t['perdus']), 'pm': int(t['paniersMarques']), 'pe': int(t['paniersEncaisses'])}
    if standings:
        break

# Le widget FFBB n'affiche parfois que 5 equipes : on complete les manquantes a partir des resultats.
for k in set(KEYS.values()) - set(standings):
    row = {'t': k, 'pts': 0, 'j': 0, 'v': 0, 'd': 0, 'pm': 0, 'pe': 0}
    for v in matches.values():
        if v['sh'] is None or k not in (v['h'], v['a']):
            continue
        us, them = (v['sh'], v['sa']) if v['h'] == k else (v['sa'], v['sh'])
        row['j'] += 1
        row['pm'] += us
        row['pe'] += them
        if us > them:
            row['v'] += 1
            row['pts'] += 2
        else:
            row['d'] += 1
            row['pts'] += 1
    standings[k] = row

rows = sorted(standings.values(), key=lambda r: (-r['pts'], -(r['pm'] - r['pe'])))
doc = {'asOf': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': URL, 'matches': {i: {'d': v['d'], 'sh': v['sh'], 'sa': v['sa']} for i, v in matches.items()}, 'standings': rows}
json.dump(doc, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
played = sum(1 for v in matches.values() if v['sh'] is not None)
canet = [m for m in matches.values() if 'CRB' in (m['h'], m['a']) and m['sh'] is not None]
last = canet[-1] if canet else None
print('OK : ' + str(played) + ' matchs joues sur 30 ; classement : ' + ', '.join(r['t'] + ' ' + str(r['pts']) for r in rows) + (' ; dernier match Canet : ' + last['h'] + ' ' + str(last['sh']) + '-' + str(last['sa']) + ' ' + last['a'] if last else ''))
