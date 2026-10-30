"""Rapproche les rattachements officiels avec la date de début de chaque voyage."""
import json
import re
import unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def key(text):
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',text.casefold()).encode('ascii','ignore').decode())

def enrichir_politique(doc):
    ref=json.loads((ROOT/'politique_reference.json').read_text(encoding='utf-8'))
    regroupements=json.loads((ROOT/'regroupements_politiques.json').read_text(encoding='utf-8'))
    index={}
    for field in ('parti','groupe'):
        index[field]={}
        for famille in regroupements[field]:
            for oid in famille['organes']:
                if oid in index[field]: raise ValueError('Organe présent dans plusieurs regroupements : '+oid)
                if oid in ref['organes'] and ref['organes'][oid]['nom'] not in famille['libelles']:
                    raise ValueError('Libellé du regroupement à vérifier : '+oid)
                index[field][oid]=famille
    couverture={'parti_identifie':0,'groupe_identifie':0,'parti_inconnu':0,'groupe_inconnu':0}
    for voyage in doc['voyages']:
        acteur=ref['acteurs'].get(key(voyage['depute']['nom_complet']))
        date=voyage['periode']['debut']
        result={'date_reference':date,'acteur_id':acteur['uid'] if acteur else None,
                'source_url':'https://www.assemblee-nationale.fr/dyn/deputes/'+acteur['uid'] if acteur else None}
        for field,typ in [('parti','PARPOL'),('groupe','GP')]:
            records=[]
            if acteur and date:
                records=[m for m in acteur['mandats'] if m['type']==typ and m['debut'] and m['debut']<=date
                         and (not m['fin'] or date<=m['fin'])
                         and (typ!='GP' or str(m['legislature'])==str(voyage['legislature']))]
            ids=sorted({m['organe_id'] for m in records})
            if len(ids)==1:
                oid=ids[0];o=ref['organes'][oid]
                result[field]={'statut':'identifie','id':oid,'nom':o['nom'],'sigle':o['sigle'],
                               'mandats':[{'id':m['uid'],'debut':m['debut'],'fin':m['fin'],'qualite':m['qualite']} for m in records]}
                famille=index[field].get(oid)
                result[field]['regroupement']={'id':famille['id'] if famille else 'libelle:'+o['nom'],
                    'nom':famille['nom'] if famille else o['nom']}
                couverture[field+'_identifie']+=1
            else:
                result[field]={'statut':'ambigu' if len(ids)>1 else 'inconnu','candidats':[ref['organes'][i] for i in ids]}
                couverture[field+'_inconnu']+=1
        voyage['politique']=result
    doc['metadonnees']['politique']={'source':ref['source'],'sha256_archive':ref['sha256_archive'],
        'date':'Date de début déclarée du déplacement ; dates de fin incluses.',
        'parti':'Rattachement à un parti ou groupement au titre du financement public. Il ne démontre pas une adhésion ; l’absence de donnée est laissée inconnue.',
        'groupe':'Groupe parlementaire au cours de la législature de la déclaration, non assimilé à un parti.',
        'methode':'Rapprochement par nom et prénom normalisés puis comparaison des périodes officielles ; homonymies ou mandats contradictoires laissés non attribués.',
        'regroupements':regroupements, 'couverture':couverture}
    return doc
