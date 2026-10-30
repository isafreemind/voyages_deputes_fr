"""Résolution déterministe et traçable des noms, sans inférence de causalité."""
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def fold(text):
    chars, positions = [], []
    for i, c in enumerate(text):
        for f in unicodedata.normalize('NFKD', c.casefold()):
            if not unicodedata.combining(f):
                chars.append(f)
                positions.append(i)
    return ''.join(chars), positions

def pattern(alias):
    tokens = re.findall(r'\w+', fold(alias)[0])
    return re.compile(r'(?<!\w)' + r'[\W_]+'.join(map(re.escape, tokens)) + r'(?!\w)')

def matches(text, aliases):
    normalized, positions = fold(text)
    found, occupied = [], set()
    for alias in sorted(aliases, key=len, reverse=True):
        for m in pattern(alias).finditer(normalized):
            start, end = positions[m.start()], positions[m.end()-1]+1
            if any(i in occupied for i in range(start,end)):
                continue
            occupied.update(range(start,end))
            found.append((start, end, alias))
    return sorted(found)

def evidence(text, start, end, alias, field):
    before, after = fold(text[max(0,start-120):start])[0], fold(text[end:end+120])[0]
    roles = {'cite_dans_financement' if field == 'financement.texte_declare' else 'mention'}
    # Negations are retained as evidence and never counted as funding.
    if re.search(r'(?:pas|non)\s+(?:par\s+)?(?:l[’\x27]|la |le )?$', before) or re.match(r'\s+ne\b.{0,50}\bpas\b', after):
        roles = {'financement_exclu'}
    else:
        if re.search(r'(?:organis\w*|organizer?)\s+par\s+(?:l[’\x27]|la |le |les )?$', before) or re.match(r'\s*[,;:]?\s*(?:qui\s+)?organis\w*\b', after):
            roles.add('organisateur_mentionne')
        if re.search(r'(?:invitation\s+(?:de|d)|invit\w*\s+par)\s*[’\x27]?\s*(?:l[’\x27]|la |le |les )?$', before):
            roles.add('invitant_mentionne')
        if re.search(r'(?:pris\w* en charge|financ\w*|pay\w*|offert\w*)[^.;\n]{0,60}\bpar\s+(?:l[’\x27]|la |le |les )?$', before) or re.match(r'\s*(?:[,;:]\s*)?(?:qui\s+)?(?:prend|prennent|a pris|ont pris|assure|financ\w*)\b', after):
            roles.add('prise_en_charge_mentionnee')
        if re.search(r'(?:partenaires?|sponsors?)\s*(?:prives)?\s*:[^.;\n]*$', before) or re.search(r'(?:en partenariat|en collaboration)\s+avec\s+(?:l[’\x27]|la |le )?$', before):
            roles.add('partenaire_mentionne')
    return {'champ':field,'debut':start,'fin':end,'texte':text[start:end],
            'alias':alias,'extrait':text[max(0,start-100):min(len(text),end+150)], 'roles':sorted(roles)}

COUNTRIES = {
    'Israël': ['Israël'], 'Pologne':['Pologne'], 'Autriche':['Autriche'],
    'Allemagne':['Allemagne'], 'France':['France','Martinique','Guadeloupe','Guyane','Île de la Réunion'], 'Taïwan':['Taïwan','Taiwan','Tawaïn'],
    'Qatar':['Qatar'], 'Royaume-Uni':['Royaume-Uni','Ecosse','Angleterre'], 'Arménie':['Arménie'],
    'États-Unis':['États-Unis','USA','Etats Unis'], 'Maroc':['Maroc'],
    'Danemark':['Danemark'], 'Belgique':['Belgique'], 'Suisse':['Suisse'],
    'Italie':['Italie'], 'Espagne':['Espagne'], 'Liban':['Liban'], 'Azerbaïdjan':['Azerbaïdjan','Azerbadjian'],
    'Côte d’Ivoire':["Côte d'Ivoire"], 'Sénégal':['Sénégal','Séngal (Dakar et Mboro)'], 'Kenya':['Kenya'],
    'Turquie':['Turquie'], 'Estonie':['Estonie'], 'Slovaquie':['Slovaquie'], 'Irlande':['Irlande'],
    'République démocratique du Congo':['République démocratique du Congo','RDC','Congo, Kinshasa','Congo Kinshasa','Kinshasa, Congo'],
    'République du Congo':['Congo Brazzaville'], 'Grèce':['Grèce'], 'Madagascar':['Madagascar'],
    'Costa Rica':['Costa Rica'], 'Ouzbékistan':['Ouzbékistan'], 'Arabie saoudite':['Arabie Saoudite'],
    'Mauritanie':['Mauritanie'], 'Russie':['Russie'], 'Kazakhstan':['Kazakhstan'], 'Géorgie':['Géorgie'],
    'Émirats arabes unis':['Émirats arabes unis'], 'Bénin':['Bénin'], 'Brésil':['Brésil'],
    'Tchéquie':['République tchèque','Tchéquie'], 'Rwanda':['Rwanda'], 'Portugal':['Portugal'],
    'Guinée':['Guinée Conakry'], 'Ukraine':['Ukraine'], 'Éthiopie':['Éthiopie'], 'Suède':['Suède'],
    'Chine':['Chine'], 'Hongrie':['Hongrie'], 'Japon':['Japon'], 'Argentine':['Argentine'], 'Chili':['Chili'],
    'Finlande':['Finlande'], 'Monaco':['Monaco'], 'Algérie':['Algérie'], 'Thaïlande':['Thaïlande'],
    'Inde':['Inde'], 'Soudan':['Soudan'], 'Maurice':['Île Maurice'], 'Syrie':['Syrie'],
    'Colombie':['Colombie'], 'Afrique du Sud':['Afrique du Sud'], 'Nigeria':['Nigeria','Nigéria'],
    'Égypte':['Égypte'], 'Sri Lanka':['Sri Lanka'], 'Laos':['Laos'], 'Équateur':['Équateur'],
    'Jamaïque':['Jamaïque'], 'Bangladesh':['Bangladesh'], 'Tchad':['Tchad'], 'Oman':['Oman'],
    'Philippines':['Philippines'], 'Moldavie':['Moldavie'], 'Canada':['Canada'], 'Norvège':['Norvège'],
    'Mexique':['Mexique'], 'Sierra Leone':['Sierra Leone'], 'Jordanie':['Jordanie'],
}

# Quelques lieux non ambigus présents seuls dans les déclarations ; jamais d'inférence depuis le descriptif.
PLACES = {
    'France':['Cannes','Pau','Toulouse','Saint-Malo','Kourou'],
    'Allemagne':['Berlin','Munich'], 'Pologne':['Cracovie'], 'États-Unis':['Washington'],
    'Royaume-Uni':['Edimbourg','Londres'], 'Suisse':['Genève'], 'Maroc':['Marrakech'],
    'Qatar':['Doha'], 'Liban':['Beyrouth'], 'Belgique':['Bruxelles'], 'Russie':['Moscou'],
    'Sierra Leone':['Freetown'], 'Norvège':['Longyearbyen'],
}

def enrichir(doc):
    registry = json.loads((ROOT/'organisations_referentiel.json').read_text(encoding='utf-8'))
    organisations = []
    for org in registry['organisations']:
        relations, candidates, aliases = [], [], set()
        for voyage in doc['voyages']:
            proofs, uncertain = [], []
            fields = {'financement.texte_declare':voyage['financement']['texte_declare'],'descriptif':voyage['descriptif']}
            for field, text in fields.items():
                aliases_field=org['alias']+(org.get('alias_financement',[]) if field=='financement.texte_declare' else [])
                for start,end,alias in matches(text,aliases_field):
                    proofs.append(evidence(text,start,end,alias,field))
                for start,end,alias in matches(text,org.get('alias_ambigus',[])):
                    uncertain.append(evidence(text,start,end,alias,field))
            if proofs:
                # A distinctive alias in this same declaration resolves the full-name variant.
                proofs += uncertain
                roles = sorted({r for p in proofs for r in p['roles']})
                relation = {'organisation_id':org['id'],'statut':'alias_identifie','roles':roles,'preuves':proofs}
                voyage.setdefault('organisations',[]).append(relation)
                relations.append((voyage,relation))
                aliases.update(p['texte'] for p in proofs)
            elif uncertain:
                relation={'organisation_id':org['id'],'statut':'a_verifier','raison':'Appellation ambiguë sans alias distinctif dans cette déclaration.','preuves':uncertain}
                voyage.setdefault('organisations_a_verifier',[]).append(relation)
                candidates.append(voyage['id'])
        if not relations and not candidates:
            continue
        vs=[v for v,_ in relations]
        by_deputy=Counter(v['depute']['nom_complet'] for v in vs)
        organisations.append({**org,'alias_observes':sorted(aliases),
            'declaration_ids':[v['id'] for v in vs], 'candidats_declaration_ids':candidates,
            'statistiques':{'declarations':len(vs),'deputes_distincts':len(by_deputy),
                'citations_champ_financement':sum('cite_dans_financement' in rel['roles'] for _,rel in relations),
                'par_annee':dict(sorted(Counter(v['periode']['debut'][:4] for v in vs if v['periode']['debut']).items())),
                'par_role':dict(Counter(r for _,rel in relations for r in rel['roles'])),
                'par_depute':[{'nom':n,'declarations':count} for n,count in by_deputy.most_common()]}})

    groups=defaultdict(list)
    for v in doc['voyages']:
        v.setdefault('organisations',[])
        v.setdefault('organisations_a_verifier',[])
        v['regroupements_possibles_ids']=[]
        dest=v['destination']['texte']
        explicit=[name for name,aliases in COUNTRIES.items() if matches(dest,aliases)]
        countries=list(explicit)
        preuves_pays=[]
        for name,aliases in COUNTRIES.items():
            for start,end,alias in matches(dest,aliases):
                preuves_pays.append({'pays':name,'texte':dest[start:end],'type':'pays_ou_territoire','alias':alias})
        for name,aliases in PLACES.items():
            for start,end,alias in matches(dest,aliases):
                if name not in countries: countries.append(name)
                preuves_pays.append({'pays':name,'texte':dest[start:end],'type':'lieu_repertorie','alias':alias})
        v['destination']['pays_reperes']=countries
        v['destination']['pays_preuves']=preuves_pays
        v['destination']['methode_pays']='Noms de pays, territoires français et quelques lieux répertoriés dans le libellé de destination ; les lieux non répertoriés restent non identifiés.'
        if len(explicit)==1 and len(countries)==1 and v['periode']['debut']:
            for rel in v['organisations']:
                if 'cite_dans_financement' in rel['roles']:
                    groups[(rel['organisation_id'],v['periode']['debut'],countries[0])].append(v)
    clusters=[]
    for (org,date,country),vs in sorted(groups.items()):
        if len({v['depute']['nom_complet'] for v in vs})<2: continue
        key='regroupement-'+hashlib.sha256(f'{org}|{date}|{country}'.encode()).hexdigest()[:12]
        cluster={'id':key,'organisation_id':org,'date_depart':date,'pays':country,
                 'statut':'hypothese','critere':'Même organisation citée au financement, même date de départ, même pays explicite. Mission commune non vérifiée.',
                 'declaration_ids':[v['id'] for v in vs], 'deputes':sorted({v['depute']['nom_complet'] for v in vs}),
                 'dates_retour':sorted({v['periode']['fin'] for v in vs if v['periode']['fin']})}
        clusters.append(cluster)
        for v in vs: v['regroupements_possibles_ids'].append(key)

    doc['organisations']=sorted(organisations,key=lambda o:(-o['statistiques']['declarations'],o['id']))
    doc['regroupements_possibles']=clusters
    doc['metadonnees']['schema_version']=2
    doc['metadonnees']['relations']={
        'methode':registry['methode'], 'referentiel':'organisations_referentiel.json',
        'roles':{'cite_dans_financement':'Nom présent dans le champ Tiers financeur, sans certification du paiement ni de son montant.',
                 'mention':'Nom présent dans le descriptif, sans rôle déduit.',
                 'prise_en_charge_mentionnee':'Formulation locale de prise en charge détectée ; consulter la phrase complète.',
                 'organisateur_mentionne':'Formulation locale d’organisation détectée.',
                 'invitant_mentionne':'Formulation locale d’invitation détectée.',
                 'partenaire_mentionne':'Partenaire ou sponsor cité ; le financement peut être indirect.',
                 'financement_exclu':'Négation explicite de financement détectée.'},
        'limites':'Règles lexicales reproductibles, sans recherche externe. Les mentions ne démontrent ni influence ni coordination. Plusieurs organisations peuvent apparaître dans une déclaration ; les comptes ne sont pas additifs. Les alias non reconnus restent dans le texte original.',
        'couverture':{'organisations':len(organisations),'declarations_avec_organisation':sum(bool(v['organisations']) for v in doc['voyages']),
                    'declarations_sans_organisation_reconnue':sum(not v['organisations'] for v in doc['voyages']),
                    'declarations_avec_candidat_ambigu':sum(bool(v['organisations_a_verifier']) for v in doc['voyages'])}}
    return doc
