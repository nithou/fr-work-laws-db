---
type: "index général"
version_corpus: "28 octobre 2026"
---

# Base de connaissances — Bot droit du travail français (salariés et élus CSE)

Corpus préparé le 28 octobre 2026 pour alimenter un bot (projet Claude, RAG, index vectoriel). Tous les fichiers sont en Markdown UTF-8, avec un en-tête YAML (source, date, chemin) et un titre par article pour faciliter le découpage.

## Organisation

| Dossier | Contenu | Nature | Fraîcheur |
|---|---|---|---|
| `01-PROMPT-SYSTEME.md` | Instructions à donner au bot | Rédigé | 10/2026 |
| `02-METHODE-RAISONNEMENT.md` | Hiérarchie des normes, ordre de vérification, pièges | Rédigé | 10/2026 |
| `10-code-du-travail/` | **Code du travail intégral** (parties législative et réglementaire), 207 fichiers découpés par titre, ~11 600 articles | Texte officiel | Légifrance, version du 08/10/2026 |
| `11-code-securite-sociale-extraits/` | Code de la sécurité sociale, livres III (maladie, maternité, invalidité), IV (AT/MP) et IX (protection sociale complémentaire) | Texte officiel | 10/2026 |
| `20-convention-syntec-idcc-1486/` | **Convention Syntec (BETIC) intégrale** : texte de base, tous les avenants et accords en vigueur, grilles de salaires | Texte officiel | KALI, 23/10/2026 |
| `21-convention-societes-financieres-idcc-478/` | **Convention des sociétés financières intégrale** + fichier de mises à jour 2023-2026 | Texte officiel | KALI 11/2023 + mises à jour jusqu'au 05/2026 |
| `30-fiches-ministere-travail/` | 270 fiches pratiques du ministère du Travail | Officiel, vulgarisé | 10/2026 |
| `31-fiches-service-public-travail/` | 555 fiches service-public.fr (travail, chômage, arrêts, AT/MP, rupture…) | Officiel, vulgarisé | 10/2026 |
| `40-fiches-synthese/` | Fiches pratiques côté salarié : rupture, temps de travail, santé, rémunération, prescription, calculs | Rédigé | 10/2026 |
| `50-prudhommes/` | Procédure prud'homale pas à pas, barèmes, préparation du dossier | Rédigé | 10/2026 |
| `60-cse/` | Guide de l'élu CSE : attributions, moyens, consultations, protection | Rédigé | 10/2026 |
| `70-jurisprudence/` | Arrêts de principe classés par thème | Rédigé | 10/2026 |
| `80-modeles-courriers/` | Modèles de lettres (salarié et CSE) | Rédigé | 10/2026 |
| `90-chiffres-cles-et-nouveautes-2026.md` | SMIC, PASS, seuils, nouveautés 2024-2026 | Rédigé | 10/2026 |

## Ordre de priorité des sources pour le bot

1. Textes officiels (`10-`, `11-`, `20-`, `21-`) : ils font foi.
2. Fiches officielles (`30-`, `31-`) : bonne vulgarisation, mises à jour par l'administration.
3. Fiches de synthèse et jurisprudence (`40-` à `90-`) : rédigées pour ce corpus, elles orientent et donnent la méthode ; en cas de contradiction avec un texte officiel, le texte officiel l'emporte.

## Origine et licence des données

- Code du travail, Code de la sécurité sociale, conventions collectives : base LEGI et KALI de la DILA (Légifrance), diffusées sous Licence Ouverte Etalab 2.0, via les dumps open data de la Fabrique numérique des ministères sociaux (paquets `@socialgouv/legi-data`, `@socialgouv/kali-data`).
- Fiches ministère du Travail : `@socialgouv/fiches-travail-data` (travail-emploi.gouv.fr).
- Fiches service-public.fr : `@socialgouv/fiches-vdd` (DILA, Licence Ouverte).

## Limites connues

- **Convention des sociétés financières** : le dernier export officiel complet date de novembre 2023. Les accords postérieurs (période d'essai 2023, article 42 en 2024, salaires 2026…) sont résumés dans `21-…/MISES-A-JOUR-2023-2026.md`.
- **Jurisprudence** : il ne s'agit pas d'une base exhaustive (Judilibre en compte des centaines de milliers d'arrêts). Le dossier `70-` couvre les arrêts de principe. Pour aller plus loin : API Judilibre (https://www.courdecassation.fr/acces-rapide-judilibre) en connectant un outil au bot.
- **Accords d'entreprise** : non inclus. Ils peuvent primer sur la convention de branche dans de nombreux domaines (voir `02-METHODE-RAISONNEMENT.md`). Le salarié doit les demander (affichage, intranet, ou base Légifrance « accords d'entreprise »).
- Les montants (SMIC, PASS, minima) changent régulièrement : voir `90-chiffres-cles-et-nouveautes-2026.md` et vérifier pour toute date postérieure.

## Mettre à jour le corpus

Les scripts de conversion fournis à part (`convert.py`, `vdd.py`) régénèrent les dossiers 10, 11, 20, 21, 30 et 31 à partir des dernières versions des paquets npm `@socialgouv/*`. Une mise à jour trimestrielle suffit.
