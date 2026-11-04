# Droit du travail français — base de connaissances

Corpus **Markdown** du droit du travail français (secteur privé), construit pour un assistant LLM au service des **salariés et des élus du CSE** — pas des employeurs. Objectif : un bot capable de citer « article L1235-3 du Code du travail » ou « article 4.5 de la convention Syntec » et de tomber juste, au lieu de paraphraser un résultat de moteur de recherche.

**Instantané :** 28 octobre 2026 · 1 298 fichiers · ~29 Mo · 11 418 articles du Code du travail · 1 944 articles du Code de la sécurité sociale · 2 conventions collectives intégrales · 827 fiches officielles. Inventaire détaillé : [`00-LISEZMOI.md`](00-LISEZMOI.md).

> Ce n'est pas une consultation juridique. C'est de la matière première pour un bot ; la décision revient à un humain.

## Pourquoi un corpus et pas une recherche web

- **Texte stable et citable.** Texte officiel Légifrance, un titre par article : le découpage est déterministe et chaque morceau renvoie à un numéro d'article.
- **Dates dans l'en-tête YAML** (`version_au`, `origine`, `chemin`), donc le bot peut dire de quelle version il parle.
- **Hiérarchie des normes écrite noir sur blanc** (loi d'ordre public → accord d'entreprise → convention de branche → contrat → usage) dans [`02-METHODE-RAISONNEMENT.md`](02-METHODE-RAISONNEMENT.md) : le bot a une règle d'arbitrage au lieu d'une intuition.
- **Conventions collectives intégrales**, texte de base + avenants + grilles de salaires : c'est là que se jouent les vraies réponses, et c'est ce que les bases généralistes n'ont pas.

## Contenu

| Dossier | Fichiers | Contenu | Nature |
|---|---|---|---|
| `01-PROMPT-SYSTEME.md` | 1 | Instructions du bot | Rédigé |
| `02-METHODE-RAISONNEMENT.md` | 1 | Hiérarchie des normes, ordre de vérification, pièges | Rédigé |
| `10-code-du-travail/` | 207 | **Code du travail intégral** (parties législative et réglementaire), 11 418 articles découpés par titre | Officiel |
| `11-code-securite-sociale-extraits/` | 68 | CSS livres III (maladie, maternité, invalidité), IV (AT/MP), IX (protection sociale complémentaire) — 1 944 articles | Officiel |
| `20-convention-syntec-idcc-1486/` | 119 | **Convention Syntec (BETIC) intégrale** : texte de base, avenants et accords en vigueur, grilles de salaires, annexes classification | Officiel |
| `21-convention-societes-financieres-idcc-478/` | 56 | **Convention des sociétés financières intégrale** + mises à jour 2023-2026 | Officiel |
| `30-fiches-ministere-travail/` | 271 | Fiches pratiques du ministère du Travail | Officiel vulgarisé |
| `31-fiches-service-public-travail/` | 556 | Fiches service-public.fr (travail, chômage, arrêts, AT/MP, rupture…) | Officiel vulgarisé |
| `40-fiches-synthese/` | 9 | Fiches côté salarié : rupture, temps de travail, santé, rémunération, prescription, calculs | Rédigé |
| `50-prudhommes/` | 2 | Procédure prud'homale pas à pas, barèmes, préparation du dossier | Rédigé |
| `60-cse/` | 1 | Guide de l'élu CSE : attributions, moyens, consultations, protection | Rédigé |
| `70-jurisprudence/` | 1 | Arrêts de principe classés par thème | Rédigé |
| `80-modeles-courriers/` | 1 | Modèles de lettres (salarié et CSE) | Rédigé |
| `90-chiffres-cles-et-nouveautes-2026.md` | 1 | SMIC, PASS, seuils, nouveautés 2024-2026 | Rédigé |
| `99-outils-mise-a-jour/` | 3 | Scripts de régénération (`convert.py`, `vdd.py`) | Outillage |

## Format des fichiers

Chaque fichier officiel s'ouvre sur un en-tête YAML et un titre par article :

```yaml
---
source: "Code du travail"
partie: "Partie législative"
chemin: "Code du travail > Première partie > Livre II > Titre III : Rupture du contrat de travail à durée indéterminée"
version_au: "2026-10-08"
origine: "Légifrance / DILA (open data LEGI)"
---
```

puis `###### Article L1231-1` avec un lien Légifrance par article. Découper sur `######` ; garder les champs du YAML comme métadonnées interrogeables (filtre par code, livre, date de version).

## Utilisation avec un bot

1. Coller [`01-PROMPT-SYSTEME.md`](01-PROMPT-SYSTEME.md) comme prompt système et [`02-METHODE-RAISONNEMENT.md`](02-METHODE-RAISONNEMENT.md) comme référence de méthode.
2. Indexer dans cet ordre : `10-` et `11-`, puis `20-` et `21-`, puis `30-` et `31-`, puis le reste. Découper au niveau de l'article ; ne jamais séparer un article de son titre.
3. Exiger la citation de l'article et la date de version ; laisser `90-chiffres-cles…` arbitrer les montants.
4. Coupler à un serveur MCP pour tout ce qui est daté — voir ci-dessous.

## Serveurs MCP

Le corpus est un instantané figé. Le droit, non. Un serveur MCP local couvre l'écart au moment de la réponse :

| Serveur | Fournisseur | Transport | Ce qu'il apporte |
|---|---|---|---|
| `droitfrancais` | [jmtanguy/droit-francais-mcp](https://github.com/jmtanguy/droit-francais-mcp) (MIT, v1.2.1) | stdio (Python) | Légifrance (codes, lois, JORF, conventions collectives) et Judilibre (jurisprudence) en direct, via les API PISTE |

### Outils exposés

**Légifrance**
- `rechercher_legifrance()` — recherche multi-critères (fonds `ALL`, `CODE_ETAT`, `LODA_ETAT`, `JORF`, `JURI`, `KALI`…)
- `consulter_legifrance()` — texte intégral d'un article ou d'un texte, avec métadonnées

**Judilibre**
- `rechercher_jurisprudence_judilibre()` — décisions avec filtres juridiction, chambre, thème, solution, dates
- `consulter_decision_judilibre()` — texte intégral d'une décision
- `obtenir_taxonomie_judilibre()` — listes de valeurs valides (chambres, juridictions, thèmes, solutions)

Le serveur expose aussi des ressources de documentation (`legifrance://documentation/fonds`, `judilibre://documentation/themes`…) pour éviter de deviner les codes de paramètres.

### Répartition des rôles

| Question | Réponse fournie par |
|---|---|
| « Que dit l'article L1231-1 ? » | corpus — rapide, sans quota, déjà découpé |
| « Ce texte était-il en vigueur au 3 février 2026 ? » | `consulter_legifrance` (version historisée) |
| « Y a-t-il un arrêt récent sur ce point ? » | `rechercher_jurisprudence_judilibre` |
| « Quel est le dernier avenant Syntec ? » | `20-…/`, puis `rechercher_legifrance` fonds `KALI` |
| « Quel est le SMIC 2026 ? » | `90-chiffres-cles…`, vérifié sur service-public.fr |

### Configuration

Prérequis : identifiants **PISTE** (`PISTE_CLIENT_ID`, `PISTE_CLIENT_SECRET`) dans le `.env` du serveur MCP.

Claude Desktop (serveur local stdio) :

```json
{
  "mcpServers": {
    "droit-francais": {
      "command": "/chemin/absolu/vers/droit-francais-mcp/.venv/bin/python3",
      "args": ["/chemin/absolu/vers/droit-francais-mcp/droit_francais_MCP.py"]
    }
  }
}
```

Hermes Agent (`~/.hermes/config.yaml`) :

```yaml
mcp_servers:
  droitfrancais:
    command: /chemin/absolu/vers/droit-francais-mcp/.venv/bin/python
    args:
      - /chemin/absolu/vers/droit-francais-mcp/droit_francais_MCP.py
    timeout: 180
    connect_timeout: 60
```

## Limites connues

- **Convention des sociétés financières** : dernier export officiel complet de novembre 2023 ; les accords postérieurs sont résumés dans `21-…/MISES-A-JOUR-2023-2026.md`. La convention n'est pas étendue — vérifier que l'employeur y est soumis.
- **Jurisprudence** : `70-` ne contient que les arrêts de principe. Pour une recherche exhaustive, c'est Judilibre via le MCP (des centaines de milliers de décisions).
- **Accords d'entreprise** : non inclus. Ils peuvent primer sur la convention de branche dans de nombreux domaines (voir `02-METHODE-RAISONNEMENT.md`) ; les demander au salarié (affichage, intranet, base Légifrance).
- **Montants** (SMIC, PASS, minima conventionnels) : changent régulièrement ; vérifier pour toute date postérieure au corpus.
- **Syntec** : toujours distinguer ETAM et IC, et vérifier la modalité de temps de travail (1 standard 35 h, 2 missions, 3 forfait jours).

## Mise à jour

`99-outils-mise-a-jour/` régénère les dossiers 10, 11, 20, 21, 30 et 31 à partir des dumps open data `@socialgouv/*` (LEGI, KALI, fiches travail, fiches VDD). Une passe trimestrielle suffit ; repasser en urgence après chaque loi ou avenant majeur.

## Licence et attribution

Deux couches, détaillées dans [`LICENSE.md`](LICENSE.md). Version courte :

- Code du travail, Code de la sécurité sociale, conventions collectives : base LEGI et KALI de la DILA (Légifrance), [Licence Ouverte Etalab 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/), via les paquets `@socialgouv/legi-data` et `@socialgouv/kali-data`.
- Fiches ministère du Travail : `@socialgouv/fiches-travail-data` (travail-emploi.gouv.fr).
- Fiches service-public.fr : `@socialgouv/fiches-vdd` (DILA, Licence Ouverte).
- Fiches de synthèse (`40-` à `90-`) : originales, publiées ici sous la même Licence Ouverte.
- Le serveur MCP est un projet tiers (MIT) ; ce dépôt se contente de documenter son branchement.

Corpus assemblé pour alimenter un assistant privé (« Staline ») ; extrait ici pour réutilisation. Corrections bienvenues en issue — avec la source.
