"""Construit un extrait traçable des mandats officiels, pour les députés du CSV."""
import csv
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'acteurs_historique_source.zip'
OUTPUT=ROOT/'politique_reference.json'
SOURCE='https://data.assemblee-nationale.fr/static/openData/repository/17/amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip'

def key(text):
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',text.casefold()).encode('ascii','ignore').decode())

with (ROOT/'voyages_deputes.csv').open(encoding='utf-8-sig',newline='') as f:
    wanted={key(row['Député(e) bénéficiaire']) for row in csv.DictReader(f,delimiter=';')}

actors={}; orgs={}
with zipfile.ZipFile(ARCHIVE) as z:
    for path in z.namelist():
        if not path.startswith('json/acteur/') or not path.endswith('.json'): continue
        actor=json.loads(z.read(path))['acteur']
        ident=actor.get('etatCivil',{}).get('ident',{})
        nom,prenom=ident.get('nom'),ident.get('prenom')
        if not isinstance(nom,str) or not isinstance(prenom,str):continue
        k=key(nom+prenom)
        if k not in wanted:continue
        if k in actors:raise ValueError('Homonymie à vérifier : '+nom+' '+prenom)
        uid=actor['uid'].get('#text') if isinstance(actor['uid'],dict) else actor['uid']
        mandats=actor.get('mandats',{}).get('mandat',[])
        if not isinstance(mandats,list): mandats=[mandats] if mandats else []
        filtered=[]
        for mandat in mandats:
            if mandat.get('typeOrgane') not in ('GP','PARPOL'):continue
            references=(mandat.get('organes') or {}).get('organeRef',[])
            if not isinstance(references,list):references=[references]
            for ref in references:
                if not isinstance(ref,str):continue
                if ref not in orgs:
                    obj=json.loads(z.read('json/organe/'+ref+'.json'))['organe']
                    orgs[ref]={'uid':ref,'nom':obj.get('libelle'),'sigle':obj.get('libelleAbrege'),'type':obj.get('codeType')}
                filtered.append({'uid':mandat.get('uid'),'type':mandat.get('typeOrgane'),'organe_id':ref,
                                 'legislature':mandat.get('legislature'),
                                 'debut':mandat.get('dateDebut') if isinstance(mandat.get('dateDebut'),str) else None,
                                 'fin':mandat.get('dateFin') if isinstance(mandat.get('dateFin'),str) else None,
                                 'qualite':(mandat.get('infosQualite') or {}).get('libQualite')})
        actors[k]={'uid':uid,'nom':nom,'prenom':prenom,'mandats':filtered}
if wanted-set(actors):raise ValueError('Députés absents : '+str(sorted(wanted-set(actors))))
result={'source':SOURCE,'sha256_archive':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'notice':'Extrait des mandats GP et PARPOL pour les députés du CSV. PARPOL est un rattachement au titre du financement de la vie politique, pas nécessairement une adhésion ; GP est un groupe parlementaire.',
        'acteurs':actors,'organes':orgs}
OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Acteurs :',len(actors),'organes :',len(orgs))
