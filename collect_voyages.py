import concurrent.futures, csv, re, time
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import requests
from bs4 import BeautifulSoup

BASE = 'https://www.assemblee-nationale.fr/dyn/{}/donsetvoyages/voyages'
OUT = Path('voyages_deputes_2020')
OUT.mkdir(exist_ok=True)
def get(leg, page):
    url = BASE.format(leg)
    for attempt in range(4):
        try:
            r = requests.get(url, params={'page':page,'limit':5}, timeout=60)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
            rows = [[c.get_text(' ', strip=True) for c in tr.find_all('td', recursive=False)] for tr in soup.select('table tr')]
            rows = [r for r in rows if len(r)==7]
            if not rows: raise ValueError('Table vide: '+r.url)
            pages = [int(parse_qs(urlparse(a.get('href','')).query).get('page',['1'])[0]) for a in soup.select('a[href*="page="]')]
            return leg, page, max(pages, default=1), rows
        except Exception:
            if attempt == 3: raise
            time.sleep(2**attempt)

first = [get(leg,1) for leg in (15,16,17)]
jobs = [(leg,p) for leg,_,last,_ in first for p in range(2,last+1)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    rest = list(pool.map(lambda x: get(*x),jobs))
allpages = sorted(first+rest)
headers=['Député(e) bénéficiaire','Date de déclaration','Destination','Dates du déplacement','Durée','Tiers financeur','Descriptif','Législature','Page source']
records=[]
for leg,page,last,rows in allpages:
    for row in rows: records.append(row+[str(leg),BASE.format(leg)+'?page='+str(page)+'&limit=5'])
with (OUT/'voyages_deputes.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter=';'); w.writerow(headers); w.writerows(records)
with (OUT/'voyages_deputes.csv').open(encoding='utf-8-sig',newline='') as f:
    assert sum(1 for _ in csv.reader(f,delimiter=';')) == len(records)+1
print('pages et lignes par législature:',[(leg,len([p for p in allpages if p[0]==leg]),sum(len(p[3]) for p in allpages if p[0]==leg)) for leg in (15,16,17)])
print('lignes:',len(records),'doublons exacts:',len(records)-len(set(tuple(r[:7]) for r in records)))
