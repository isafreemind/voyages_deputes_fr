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

## Partis et groupes parlementaires

`politique_reference.json` est un extrait de l'[historique des députés de l'Assemblée nationale](https://data.assemblee-nationale.fr/acteurs/historique-des-deputes), avec l'URL et l'empreinte SHA-256 de l'archive d'origine. Il contient seulement les acteurs présents dans le CSV et leurs mandats `PARPOL` et `GP`.

Pour chaque déclaration, `politique` conserve le rattachement à un parti ou groupement **au titre du financement de la vie politique** et le groupe parlementaire actifs à la date de début du voyage. Ces deux informations sont distinctes et le rattachement financier n'est pas une preuve d'adhésion. Les noms et prénoms sont rapprochés sans accents ni ponctuation ; une homonymie provoque une erreur lors de l'extraction. Les fins de mandat sont incluses. Un rattachement absent ou contradictoire reste inconnu, sans utilisation d'une affiliation antérieure ou postérieure. Chaque attribution conserve les identifiants et dates des mandats.

`regroupements_politiques.json` documente les rapprochements analytiques de libellés historiques, avec leurs identifiants officiels, explications et sources. Les libellés et dates d'origine restent conservés dans chaque déclaration ; le site propose une vue regroupée et une vue historique. Les groupements de financement et les groupes parlementaires sont traités séparément : le regroupement « Ensemble / Ensemble ! » n'est pas fusionné avec le parti La République en Marche ou avec les autres partis de la coalition. Ces rapprochements ne démontrent pas une identité juridique ni une adhésion individuelle.

Pour actualiser l'extrait, télécharger l'archive ZIP indiquée dans `extraire_politique.py` sous le nom `acteurs_historique_source.zip` dans ce dossier, puis exécuter `python voyages_deputes_2020/extraire_politique.py` et reconstruire la base. L'archive complète est ignorée par Git ; l'extrait est versionné.

ELNET : les variantes `ELNET`, `EL.NET` et les domaines `elnetwork.fr`/`.eu` identifient le réseau. Le nom développé `European Leadership Network` seul reste ambigu ; sa présence avec un alias distinctif dans la même déclaration permet de le résoudre. Le libellé `ELN - European Leadership Network` reste à vérifier.

Les rôles proviennent de règles lexicales conservatrices, non d'une vérification externe. « Cité au financement » signifie présence dans le champ Tiers financeur, sans preuve du montant payé. Les partenaires indirects, invitations, prises en charge et exclusions sont distingués quand la phrase permet de les détecter. Les relations n'établissent aucune causalité, influence ou coordination. Les montants ne sont pas attribués aux organisations ni additionnés.

Le site synchronise sa copie intégrée et son fichier téléchargeable à chaque `npm run dev` ou `npm run build`. La source canonique reste ce dossier.
