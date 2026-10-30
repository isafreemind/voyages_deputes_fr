# Voyages des députés français

Tableau de bord des déclarations de déplacements publiées par l'Assemblée nationale : députés, organisations citées et pays de destination. Il s'agit d'un instantané des déclarations disponibles dans le registre, et non de tous les voyages des députés.

## Lancer localement

```sh
cd dashboard-voyages
npm ci
npm run dev
```

Le fichier canonique est `voyages_deputes_2020/base_voyages.json`. Avant chaque lancement ou construction du site, le script `sync:data` génère automatiquement les copies nécessaires à l'application et au téléchargement ; ces copies ne sont pas versionnées.

Pour reconstruire la base depuis le CSV et vérifier les rapprochements :

```sh
python voyages_deputes_2020/construire_base.py
python -m unittest discover -s voyages_deputes_2020 -p test_relations.py
```

La collecte à partir du registre est disponible dans `collect_voyages.py` et nécessite `requests` et `beautifulsoup4`. La méthode, les limites et les règles de rapprochement sont détaillées dans `voyages_deputes_2020/README.md`.

## GitHub Pages

Le workflow `.github/workflows/pages.yml` construit le site sur chaque mise à jour de `main` et le publie avec GitHub Actions. Dans les paramètres du dépôt, sélectionner **Settings → Pages → Build and deployment → Source → GitHub Actions**. L'URL attendue est `https://isafreemind.github.io/voyages_deputes_fr/` après activation et réussite du workflow.

Les données proviennent des déclarations accessibles sur le site de l'Assemblée nationale. Une organisation citée n'a pas nécessairement financé l'intégralité du déplacement. Les montants, les associations et les groupes possibles de voyages doivent être vérifiés dans les déclarations sources.
