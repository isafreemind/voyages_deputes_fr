# Observatoire des voyages parlementaires

Application React / TypeScript / Vite, alimentée par le fichier `../voyages_deputes_2020/base_voyages.json`.

```powershell
npm.cmd install
npm.cmd run dev
```

`npm.cmd run build` vérifie TypeScript et produit `dist/`. `npm.cmd run preview` sert ce résultat sur le port 4173.

Le script `sync:data` synchronise les deux copies du JSON avant le lancement et le build. Sur une copie du dépôt hébergé sans le dossier parent, la copie embarquée est utilisée. Pour reconstruire les données et les règles de rapprochement, utiliser les scripts du dossier `voyages_deputes_2020` dans le projet principal.

L'exploration des organisations est accessible avec `#organisation/elnet` et les autres identifiants du référentiel. Les filtres globaux s'appliquent aux comptes du dossier ; les hypothèses de missions peuvent filtrer le registre. Les passages sources et les rapprochements ambigus se consultent dans le détail d'une déclaration.

Les statistiques portent sur les déclarations publiées, pas sur la totalité des voyages. Les fiches regroupent des appellations de recherche ; les co-mentions ne représentent pas nécessairement un lien entre organisations. Les rapprochements ambigus sont exclus des comptes. Aucune mise à jour réseau des données n'a lieu dans le navigateur.
