"""Кто добавил себя на сайте сам (событие saff_join в Amplitude) → в конец people.json.
Запуск из ~/AndroidStudioProjects/quran_widget (там growth-agent/.env): python3 ~/saff-site/scripts/joins.py [дней=3]
Ник проверяется тем же правилом, что и на сайте; повторы и уже стоящие во дворе пропускаются.
"""
import base64, json, os, re, sys, requests, datetime
sys.path.insert(0, 'growth-agent/scripts')
import live_users as lu
env = lu.load_env()
H = {"Authorization": "Basic " + base64.b64encode(f"{env['AMPLITUDE_API_KEY']}:{env['AMPLITUDE_SECRET_KEY']}".encode()).decode()}
days = int(sys.argv[1]) if len(sys.argv) > 1 else 3
end = datetime.date.today(); start = end - datetime.timedelta(days=days)
e = {"event_type": "saff_join", "group_by": [{"type": "event", "value": "u"}, {"type": "event", "value": "dua"}]}
r = requests.get(f"https://{env['AMPLITUDE_HOST']}/api/2/events/segmentation", headers=H, timeout=120,
                 params={"e": json.dumps(e), "start": start.strftime('%Y%m%d'), "end": end.strftime('%Y%m%d'), "m": "totals", "limit": 1000})
if r.status_code == 400 and 'not_found' in r.text: print('saff_join ещё ни разу не было'); sys.exit(0)
if r.status_code != 200: print(r.status_code, r.text[:300])
r.raise_for_status(); d = r.json()['data']
BAD = re.compile(r'(sex|porn|xxx|fuck|suka|blyad|xuy|huy|pidor|casino|1xbet)', re.I)
path = os.path.expanduser('~/saff-site/people.json')
people = json.load(open(path))
have = {(p[0] or '').lower() for p in people}
added = []
for lab in d['seriesLabels']:
    parts = str(lab[1] if isinstance(lab, list) else lab).split('; ') + ['']
    u, dua = parts[0], parts[1]
    u = u.strip().lower().lstrip('@'); dua = dua.strip() if dua.strip() in ('fam', 'ease', 'hajj', 'calm', 'forgive') else ''
    if not re.fullmatch(r'[a-z0-9._]{2,30}', u) or u in have or BAD.search(u) or u in ('quran.widget.app', 'indiedev2000', '123123123asdasd', 'temirlantemirlantemirlantemir'):  # свои аккаунты и тесты владельца
        continue
    have.add(u); people.append([u, '', 's', dua] if dua else [u, '', 's']); added.append(u)
json.dump(people, open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
print(f'saff_join за {days} дн.: новых {len(added)} → всего {len(people)}', added)
