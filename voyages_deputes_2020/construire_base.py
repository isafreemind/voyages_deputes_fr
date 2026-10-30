import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from relations import enrichir

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'voyages_deputes.csv'
OUTPUT = ROOT / 'base_voyages.json'

def normaliser(texte):
    return ''.join(c for c in unicodedata.normalize('NFKD', texte.casefold()) if not unicodedata.combining(c))

MOIS = {x: i for i, x in enumerate(['janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre'], 1)}
DATE_RE = re.compile(r'(\d{1,2})\s+(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+(\d{4})')
MONTANT_RE = re.compile(r'(?<![\w\d])\d{1,3}(?:[\u00a0\u202f ]\d{3})*(?:[,.]\d{1,2})?\s*(?:€|euros?\b|EUR\b)', re.I)
TAG_PATTERNS = {
    'transport_avion': r'\b(avion|aerien|aerienne|aeriens|aeriennes|vols?|billets? d.avion)\b',
    'transport_train': r'\b(train|sncf|ferroviaire)\b',
    'hebergement': r'\b(hotel|hotels|hebergement|nuitees?|logement)\b',
    'restauration': r'\b(repas|restauration|dejeuner|diner)\b',
    'transport_local': r'\b(transports? sur place|deplacements? sur place|taxi|navette)\b',
    'conference_forum': r'\b(conference|colloque|forum|congres|sommet|seminaire)\b',
    'groupe_amitie': r'\bgroupe[s]? d.amitie\b',
    'delegation_parlementaire': r'\bdelegation parlementaire\b',
    'rencontres_institutionnelles': r'\b(rencontres? institutionnelles?|entretiens? institutionnels?)\b',
    'sport': r'\b(rugby|football|match|jeux olympiques|competition sportive)\b',
    'culture': r'\b(festival|culturel|culturelle|cinema)\b',
    'financement_personnel_mentionne': r'\b(contribution personnelle|participation personnelle|fonds personnels|frais personnels)\b',
}

def parse_dates(raw):
    dates=[]
    for m in DATE_RE.finditer(normaliser(raw)):
        try:
            dates.append(datetime(int(m[3]), MOIS[m[2]], int(m[1])).date().isoformat())
        except ValueError:
            pass
    return (dates[0] if dates else None, dates[1] if len(dates)>1 else None)

def split_name(raw):
    parts=raw.split()
    index=0
    for part in parts:
        letters=''.join(x for x in part if x.isalpha())
        if letters and letters.isupper(): index+=1
        else: break
    return (' '.join(parts[:index]) or None, ' '.join(parts[index:]) or None)

def montants(fields):
    result=[]
    for champ, texte in fields.items():
        for match in MONTANT_RE.finditer(texte):
            raw=match.group().strip()
            number=re.sub(r'\s*(?:€|euros?|EUR)\s*$', '', raw, flags=re.I)
            number=re.sub(r'[\u00a0\u202f ]', '', number).replace(',', '.')
            result.append({'valeur': float(number), 'devise': 'EUR', 'texte': raw, 'champ': champ,
                           'contexte': texte[max(0, match.start()-90):min(len(texte),match.end()+90)].strip()})
    return result

with SOURCE.open(encoding='utf-8-sig', newline='') as f:
    reader=csv.DictReader(f, delimiter=';')
    rows=list(reader)

voyages=[]
ids=set()
for line, row in enumerate(rows, start=2):
    nom, prenom=split_name(row['Député(e) bénéficiaire'])
    debut, fin=parse_dates(row['Dates du déplacement'])
    try: date_declaration=datetime.strptime(row['Date de déclaration'], '%d/%m/%Y').date().isoformat()
    except ValueError: date_declaration=None
    duree=re.search(r'\d+',row['Durée'])
    champs={'financeur':row['Tiers financeur'], 'descriptif':row['Descriptif']}
    tags=[]
    for tag, pattern in TAG_PATTERNS.items():
        sources=[name for name, value in champs.items() if re.search(pattern, normaliser(value))]
        if sources: tags.append({'tag':tag,'champs':sources})
    key=json.dumps(row,ensure_ascii=False,sort_keys=True).encode('utf-8')
    identifiant='voyage-'+hashlib.sha256(key).hexdigest()[:16]
    if identifiant in ids: raise ValueError('Déclaration identique : '+identifiant)
    ids.add(identifiant)
    voyages.append({
        'id':identifiant, 'ligne_csv':line,
        'depute':{'nom_complet':row['Député(e) bénéficiaire'],'nom':nom,'prenom':prenom},
        'legislature':int(row['Législature']),
        'declaration':{'date':date_declaration,'date_texte':row['Date de déclaration']},
        'destination':{'texte':row['Destination']},
        'periode':{'debut':debut,'fin':fin,'texte':row['Dates du déplacement'],'duree_jours':int(duree.group()) if duree else None,'duree_texte':row['Durée']},
        'financement':{'texte_declare':row['Tiers financeur'],'montants_mentionnes':montants(champs)},
        'descriptif':row['Descriptif'], 'tags':tags, 'source_url':row['Page source'],
        'donnees_originales':row,
    })

doc={'metadonnees':{
    'titre':'Déclarations de voyages des députés', 'fichier_source':SOURCE.name,
    'source':'Assemblée nationale, registre des invitations à des déplacements',
    'nombre_declarations':len(voyages),
    'perimetre':'Déclarations présentes dans le CSV, législatures 15, 16 et 17 ; le registre ne couvre pas tous les déplacements.',
    'methode':'Chaque ligne source devient une déclaration. Les noms sont séparés selon les mots en majuscules ; les dates et durées sont extraites automatiquement. Les tags sont des correspondances de mots, pas des faits vérifiés.',
    'limites':'Les textes originaux sont conservés. Un référentiel relie certaines variantes de noms d’organisations ; sa couverture est partielle et mesurée. Les montants restent des mentions en euros, sans attribution automatique, dédoublonnage ni qualification de coût total. Aucune valeur absente ne vaut zéro.',
    'tags_disponibles':list(TAG_PATTERNS),
}, 'voyages':voyages}
doc=enrichir(doc)
with OUTPUT.open('w',encoding='utf-8',newline='\n') as f:
    json.dump(doc,f,ensure_ascii=False,indent=2)
    f.write('\n')
assert len(json.loads(OUTPUT.read_text(encoding='utf-8'))['voyages']) == len(rows)
print('Déclarations:',len(voyages))
print('Dates début / fin:',sum(bool(v['periode']['debut']) for v in voyages),sum(bool(v['periode']['fin']) for v in voyages))
print('Noms séparés:',sum(bool(v['depute']['nom'] and v['depute']['prenom']) for v in voyages))
print('Déclarations avec montants:',sum(bool(v['financement']['montants_mentionnes']) for v in voyages))
print('Tags:',dict(Counter(t['tag'] for v in voyages for t in v['tags'])))
