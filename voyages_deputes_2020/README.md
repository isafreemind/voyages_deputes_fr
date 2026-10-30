# Base de déclarations et relations

`base_voyages.json` est reconstruit depuis le CSV, sans changer ses textes ni les identifiants des déclarations.

```powershell
python voyages_deputes_2020/construire_base.py
python -m unittest discover -s voyages_deputes_2020 -p test_relations.py
```

## Structure ajoutée (version 2)

- `organisations` : fiches de recherche, variantes, identifiants des déclarations et statistiques distinctes par député, année et rôle.
- Dans chaque voyage, `organisations` : liens identifiés avec rôle et preuves. Chaque preuve comporte le champ d'origine, ses positions `debut`/`fin` (indices de caractères Python), le nom trouvé et un extrait de contexte.
- `organisations_a_verifier` : rapprochements ambigus, exclus des comptes des organisations.
- `regroupements_possibles` : hypothèses de mission commune. Un groupe exige la même organisation citée au financement, la même date de départ, un seul pays explicite commun et au moins deux noms de députés distincts. La date de retour peut varier et reste visible dans le JSON. Deux groupes peuvent partager les mêmes déclarations si plusieurs organisations sont citées.
- `destination.pays_reperes` : pays reconnus par leur nom, par un territoire français ou par un lieu répertorié explicitement dans le libellé de destination. `pays_preuves` indique le texte et la règle employés. Les autres lieux restent non identifiés.
- `metadonnees.relations` : définition des rôles, méthode et couverture.

Le référentiel `organisations_referentiel.json` est éditable. Les alias sont rapprochés sans tenir compte de la casse, des accents et de certains séparateurs. Les appellations de réseaux peuvent réunir plusieurs branches ; ce ne sont pas des identifiants de personnes morales. Les mots courts, les noms de pays seuls, les homonymes et les acteurs non répertoriés ne sont pas automatiquement fusionnés.

ELNET : les variantes `ELNET`, `EL.NET` et les domaines `elnetwork.fr`/`.eu` identifient le réseau. Le nom développé `European Leadership Network` seul reste ambigu ; sa présence avec un alias distinctif dans la même déclaration permet de le résoudre. Le libellé `ELN - European Leadership Network` reste à vérifier.

Les rôles proviennent de règles lexicales conservatrices, non d'une vérification externe. « Cité au financement » signifie présence dans le champ Tiers financeur, sans preuve du montant payé. Les partenaires indirects, invitations, prises en charge et exclusions sont distingués quand la phrase permet de les détecter. Les relations n'établissent aucune causalité, influence ou coordination. Les montants ne sont pas attribués aux organisations ni additionnés.

Le site synchronise sa copie intégrée et son fichier téléchargeable à chaque `npm run dev` ou `npm run build`. La source canonique reste ce dossier.
