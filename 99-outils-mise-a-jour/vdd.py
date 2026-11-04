#!/usr/bin/env python3
"""Convertit les fiches service-public.fr (format XML->JSON SocialGouv) en Markdown, filtrées sur le travail."""
import json, os, re, sys
sys.path.insert(0, "/home/claude/scripts")
from convert import slug, write, frontmatter, clean

SRC = "/home/claude/raw/fiches-vdd/package/data"
OUT = "/home/claude/bot-droit-travail/31-fiches-service-public-travail"

SKIP = {"Audience", "Canal", "FilDAriane", "Theme", "DossierPere", "SousDossierPere", "SousThemePere",
        "Avertissement", "Partenaire", "VoirAussi", "QuestionReponse", "InformationComplementaire",
        "Montant", "Abreviation", "Definition", "CommentFaireSi", "Actualite", "Fiche", "SurTitre",
        "OuSAdresser", "PourEnSavoirPlus", "SiteInternetPublic", "LienWeb", "Glossaire", "Image"}

def txt(n):
    if n.get("type") == "text":
        return n.get("text", "")
    return "".join(txt(c) for c in n.get("children", []))

def inline(n):
    """Rendu inline (paragraphes)."""
    out = []
    for c in n.get("children", []):
        if c.get("type") == "text":
            out.append(c.get("text", ""))
            continue
        name = c.get("name")
        if name == "MiseEnEvidence":
            out.append(f"**{clean(inline(c))}**")
        elif name == "Exposant":
            out.append(f"^{inline(c)}")
        elif name in ("LienInterne", "LienExterne", "LienIntra"):
            out.append(inline(c))
        else:
            out.append(inline(c))
    return "".join(out)

def block(n, depth, out):
    for c in n.get("children", []):
        if c.get("type") == "text":
            t = clean(c.get("text"))
            if t:
                out.append(t + "\n")
            continue
        name = c.get("name")
        if name in SKIP or (name or "").startswith("dc:"):
            continue
        if name == "Titre":
            out.append(f"\n{'#' * min(depth, 6)} {clean(inline(c))}\n")
        elif name == "Paragraphe":
            out.append(clean(inline(c)) + "\n")
        elif name == "Liste":
            numbered = c.get("attributes", {}).get("type") == "numero"
            i = 0
            for it in c.get("children", []):
                if it.get("name") == "Item":
                    i += 1
                    sub = []
                    block(it, depth + 1, sub)
                    lines = [l for l in "\n".join(sub).split("\n") if l.strip()]
                    if lines:
                        mark = f"{i}." if numbered else "-"
                        out.append(f"{mark} {lines[0]}")
                        out.extend("  " + l for l in lines[1:])
            out.append("")
        elif name == "Tableau":
            rows = []
            for r in c.get("children", []):
                if r.get("name") == "Rangée":
                    rows.append([clean(txt(cell)).replace("|", "/") for cell in r.get("children", []) if cell.get("name") == "Cellule"])
                elif r.get("name") == "Titre":
                    out.append(f"\n**{clean(txt(r))}**\n")
            if rows:
                w = max(len(r) for r in rows)
                rows = [r + [""] * (w - len(r)) for r in rows]
                out.append("| " + " | ".join(rows[0]) + " |")
                out.append("|" + "---|" * w)
                for r in rows[1:]:
                    out.append("| " + " | ".join(r) + " |")
                out.append("")
        elif name in ("ANoter", "ASavoir", "Attention", "Rappel"):
            label = {"ANoter": "À noter", "ASavoir": "À savoir", "Attention": "Attention", "Rappel": "Rappel"}[name]
            sub = []
            c2 = dict(c); c2["children"] = [x for x in c.get("children", []) if x.get("name") != "Titre"]
            block(c2, depth + 1, sub)
            body = " ".join(l.strip() for l in sub if l.strip() and not l.startswith("#"))
            out.append(f"\n> **{label}** : {body}\n")
        elif name == "Cas":
            out.append(f"\n{'#' * min(depth, 6)} Cas : {clean(txt(next((x for x in c.get('children', []) if x.get('name') == 'Titre'), {})))}\n")
            c2 = dict(c); c2["children"] = [x for x in c.get("children", []) if x.get("name") != "Titre"]
            block(c2, depth + 1, out)
        elif name in ("Chapitre", "SousChapitre"):
            block(c, depth, out)
            out.append("")
        elif name == "ServiceEnLigne":
            t = clean(txt(next((x for x in c.get("children", []) if x.get("name") == "Titre"), {})))
            url = c.get("attributes", {}).get("URL", "")
            if t:
                out.append(f"- Service/formulaire : {t} {url}".rstrip())
        elif name == "Reference":
            pass
        else:
            block(c, depth + 1 if name in ("Chapitre",) else depth, out)

def refs(pub):
    r = []
    for c in pub.get("children", []):
        if c.get("name") == "Reference":
            t = clean(txt(next((x for x in c.get("children", []) if x.get("name") == "Titre"), {})))
            comp = clean(txt(next((x for x in c.get("children", []) if x.get("name") == "Complement"), {})))
            url = c.get("attributes", {}).get("URL", "")
            r.append(f"- {t}{' — ' + comp if comp else ''} {url}".rstrip())
    return r

def meta(pub, key):
    for c in pub.get("children", []):
        if c.get("name") == key:
            return clean(txt(c))
    return ""

KW = re.compile(r"Travail|Ressources humaines|Chômage|Arrêt maladie|Accident du travail|Maladie professionnelle|Congé|Salari|Licenci|Retraite progressive|Prud", re.I)

def main():
    idx = json.load(open(f"{SRC}/index.json"))
    sel = [x for x in idx if x["id"].startswith("F") and x["type"] == "particuliers" and
           (KW.search(x.get("subject") or "") or KW.search(x.get("theme") or ""))
           and not re.search(r"fonction publique|fonctionnaire", x.get("theme") or "", re.I)]
    # Exclure fonction publique pure (le bot vise le secteur privé) : on garde mais on étiquette
    index = []
    for x in sorted(sel, key=lambda y: y["theme"]):
        p = f"{SRC}/particuliers/{x['id']}.json"
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        pub = d["children"][0]
        title = meta(pub, "dc:title")
        url = pub.get("attributes", {}).get("spUrl", "")
        out = []
        block(pub, 2, out)
        body = "\n".join(out)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        if len(body) < 200:
            continue
        theme = x["theme"].replace("Accueil particuliers > ", "")
        fm = frontmatter(source="Service-public.fr (DILA)", id=x["id"], titre=title, theme=theme,
                         date=meta(pub, "dc:date").replace("modified ", ""), url=url)
        r = refs(pub)
        text = fm + f"# {title}\n\n_Fiche service-public.fr {x['id']} — {theme} — mise à jour {meta(pub, 'dc:date').replace('modified ', '')}. {url}_\n\n" \
               + (meta(pub, "dc:description") + "\n\n") + body + ("\n\n## Textes de référence\n\n" + "\n".join(r) if r else "")
        fn = f"{x['id']}_{slug(title, 70)}.md"
        write(os.path.join(OUT, fn), text)
        index.append((theme, title, fn))
    write(os.path.join(OUT, "INDEX.md"), "# Index — fiches service-public.fr (travail)\n\n" +
          "\n".join(f"- {t} — [{ti}]({fn})" for t, ti, fn in index))
    print(len(index), "fiches")

if __name__ == "__main__":
    main()
