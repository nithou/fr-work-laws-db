# Régénérer le corpus officiel

Prérequis : Node/npm et Python 3 avec `markdownify` (`pip install markdownify`).

1. Télécharger les dumps officiels (DILA via SocialGouv) dans `raw/` :
   - `npm pack @socialgouv/legi-data` (Code du travail, Code de la sécurité sociale)
   - `npm pack @socialgouv/kali-data` (conventions collectives ; la convention IDCC 478 n'y est plus remplie depuis la v3 : utiliser `@socialgouv/kali-data@2.671.0` pour son texte, puis compléter avec Légifrance)
   - `npm pack @socialgouv/fiches-travail-data` et `@socialgouv/fiches-vdd`
   et décompresser chaque archive dans `raw/<nom-du-paquet>/`.
2. Adapter les chemins `RAW` et `OUT` en tête de `convert.py` et `vdd.py`.
3. Lancer `python3 convert.py code css syntec sf fiches` puis `python3 vdd.py`.

Pour une autre convention collective : repérer son identifiant KALICONT dans `raw/kali-data/package/data/index.json` (champ `num` = IDCC) et appeler `export_convention()`.
