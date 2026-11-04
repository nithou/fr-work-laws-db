#!/usr/bin/env python3
"""Convertit les dumps JSON officiels (DILA via SocialGouv) en Markdown découpé pour RAG."""
import json, re, os, sys, html
from markdownify import markdownify as mdify

RAW = "/home/claude/raw"
OUT = "/home/claude/bot-droit-travail"

def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()

def h2md(h):
    if not h:
        return ""
    m = mdify(h, heading_style="ATX", bullets="-")
    m = re.sub(r"\n{3,}", "\n\n", m)
    return m.strip()

def slug(s, n=60):
    s = clean(s).lower()
    s = re.sub(r"[àâä]", "a", s); s = re.sub(r"[éèêë]", "e", s); s = re.sub(r"[îï]", "i", s)
    s = re.sub(r"[ôö]", "o", s); s = re.sub(r"[ùûü]", "u", s); s = s.replace("ç", "c").replace("œ", "oe")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:n].strip("-")

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")

def frontmatter(**kw):
    lines = ["---"]
    for k, v in kw.items():
        v = str(v).replace('"', "'")
        lines.append(f'{k}: "{v}"')
    lines.append("---\n")
    return "\n".join(lines)

# ---------------------------------------------------------------- CODES (LEGI)
def legi_articles(node, path, out, depth=2, nums=None):
    """Accumule le texte des articles sous `node`, avec titres de sections."""
    for c in node.get("children", []):
        d = c["data"]
        if c["type"] == "section":
            t = clean(d.get("title"))
            out.append(f"\n{'#' * min(depth, 5)} {t}\n")
            legi_articles(c, path + [t], out, depth + 1, nums)
        else:
            if d.get("etat") not in (None, "VIGUEUR", "VIGUEUR_DIFF"):
                continue
            num = d.get("num") or ""
            body = h2md(d.get("texteHtml")) or clean(d.get("texte"))
            url = f"https://www.legifrance.gouv.fr/codes/article_lc/{d['id']}"
            diff = " (entrée en vigueur différée)" if d.get("etat") == "VIGUEUR_DIFF" else ""
            if nums is not None: nums.append(num)
            out.append(f"\n###### Article {num}{diff}\n[Légifrance]({url})\n\n{body}\n")
            nota = clean(re.sub('<[^>]+>', ' ', d.get('notaHtml') or d.get('nota') or ''))
            if nota:
                out.append(f"\n> NOTA : {nota}\n")

def count_articles(n):
    return (1 if n["type"] == "article" else 0) + sum(count_articles(c) for c in n.get("children", []))

def export_code(file_id, code_name, outdir, keep_parts=None, filter_fn=None, prefix=""):
    root = json.load(open(f"{RAW}/legi-data/package/data/{file_id}.json"))
    version = root["data"].get("dateDebutVersion")
    files = 0
    for part in root["children"]:
        pt = clean(part["data"]["title"])
        if "ancienne" in pt.lower() or pt.startswith("Annexes"):
            continue
        if keep_parts and not any(k in pt for k in keep_parts):
            continue
        ptag = "L" if "législative" in pt.lower() else "R"
        # découpage : partie > livre > titre  (les sections sans sous-niveau suffisent seules)
        def emit(node, crumbs, level):
            nonlocal files
            t = clean(node["data"]["title"])
            if filter_fn and not filter_fn(crumbs + [t]):
                # on peut quand même descendre
                pass
            kids = node.get("children", [])
            n_art = count_articles(node)
            split = level < 3 and n_art > 120 and any(k["type"] == "section" for k in kids)
            if split:
                for k in kids:
                    if k["type"] == "section":
                        emit(k, crumbs + [t], level + 1)
                return
            if filter_fn and not filter_fn(crumbs + [t]):
                return
            if n_art == 0:
                return
            body = []; nums = []
            legi_articles(node, crumbs + [t], body, 2, nums)
            crumb = " > ".join([code_name] + crumbs + [t])
            text = frontmatter(source=code_name, partie=pt, chemin=crumb,
                               version_au=version, origine="Légifrance / DILA (open data LEGI)")
            text += f"# {crumb}\n\n_Texte officiel en vigueur au {version}. {n_art} articles._\n" + "".join(body)
            files += 1
            rng = f"{nums[0]}_a_{nums[-1]}" if nums else ptag
            fname = f"{prefix}{files:03d}_{rng}_{slug(t, 45)}.md"
            write(os.path.join(outdir, fname), text)
        for k in part["children"]:
            if k["type"] == "section":
                emit(k, [pt], 1)
    return files, version

# ---------------------------------------------------------------- CONVENTIONS (KALI)
def kali_text(node, depth, out, stats):
    for c in node.get("children", []):
        d = c["data"]
        etat = d.get("etat") or "VIGUEUR"
        if not etat.startswith("VIGUEUR"):
            continue
        if c["type"] == "section":
            out.append(f"\n{'#' * min(depth, 5)} {clean(d.get('title'))}\n")
            kali_text(c, depth + 1, out, stats)
        else:
            num = d.get("num") or ""
            sur = clean(d.get("surtitre"))
            url = f"https://www.legifrance.gouv.fr/conv_coll/article/{d['id']}"
            ext = "" if etat == "VIGUEUR_ETEN" else (" — ⚠ non étendu" if etat == "VIGUEUR_NON_ETEN" else "")
            head = f"###### Article {num}" + (f" — {sur}" if sur else "") + ext
            body = h2md(d.get("content")) or ""
            out.append(f"\n{head}\n[Légifrance]({url})\n\n{body}\n")
            nota = clean(re.sub('<[^>]+>', ' ', d.get('nota') or ''))
            if nota:
                out.append(f"\n> NOTA : {nota}\n")
            stats["art"] += 1

def export_convention(path, outdir, label, idcc, extra_note=""):
    root = json.load(open(path))
    meta = root["data"]
    stats = {"art": 0, "files": 0}
    index = []
    for group in root["children"]:
        gtitle = clean(group["data"].get("title"))
        is_base = gtitle.lower().startswith("texte de base")
        texts = [group] if is_base else group.get("children", [])
        for t in texts:
            d = t["data"]
            etat = d.get("etat") or "VIGUEUR"
            if not etat.startswith("VIGUEUR"):
                continue
            title = clean(d.get("title"))
            out = []
            before = stats["art"]
            kali_text(t, 2, out, stats)
            if stats["art"] == before:
                continue
            stats["files"] += 1
            cat = "00-texte-de-base" if is_base else ("salaires" if "salaire" in gtitle.lower() else "textes-attaches")
            fname = f"{cat}/{stats['files']:03d}-{slug(title, 70)}.md"
            ext = {"VIGUEUR_ETEN": "en vigueur, étendu", "VIGUEUR_NON_ETEN": "en vigueur, NON étendu (ne s'applique qu'aux entreprises adhérentes à une organisation signataire)", "VIGUEUR": "en vigueur"}.get(etat, etat)
            fm = frontmatter(source=f"Convention collective {label}", idcc=idcc, texte=title,
                             etat=ext, date_modif=d.get("modifDate", ""), kali_id=d.get("id", ""),
                             origine="Légifrance / DILA (open data KALI)")
            url = f"https://www.legifrance.gouv.fr/conv_coll/id/{d.get('id')}"
            body = fm + f"# {label} (IDCC {idcc}) — {title}\n\n_Statut : {ext}. Source : [Légifrance]({url}). {extra_note}_\n" + "".join(out)
            write(os.path.join(outdir, fname), body)
            index.append((cat, fname, title, ext, d.get("modifDate", "")))
    # index
    lines = [frontmatter(source=f"Convention collective {label}", idcc=idcc, type="index"),
             f"# Index — {meta.get('title')} (IDCC {idcc})\n", extra_note + "\n",
             "| Catégorie | Fichier | Texte | Statut | Dernière modif. |", "|---|---|---|---|---|"]
    for cat, f, t, e, m in index:
        lines.append(f"| {cat} | `{f}` | {t} | {e.split(' (')[0]} | {m} |")
    write(os.path.join(outdir, "INDEX.md"), "\n".join(lines))
    return stats

# ---------------------------------------------------------------- FICHES MINISTÈRE
def export_fiches_travail(outdir):
    F = json.load(open(f"{RAW}/fiches-travail-data/package/data/fiches-travail.json"))
    idx = []
    for i, f in enumerate(sorted(F, key=lambda x: x["title"])):
        parts = [frontmatter(source="Ministère du Travail — fiches pratiques", titre=f["title"],
                             date_maj=f.get("date", ""), url=f.get("url", "")),
                 f"# {clean(f['title'])}\n", f"_Fiche pratique officielle du ministère du Travail, mise à jour le {f.get('date','')}. Source : {f.get('url','')}_\n",
                 h2md(f.get("intro")) + "\n"]
        for s in f.get("sections", []):
            st = clean(s.get("title"))
            if st:
                parts.append(f"\n## {st}\n")
            parts.append(h2md(s.get("html")) + "\n")
            refs = s.get("references") or {}
            reflist = []
            if isinstance(refs, dict):
                for k, v in refs.items():
                    for a in (v.get("articles") if isinstance(v, dict) else v) or []:
                        if isinstance(a, dict) and a.get("text"):
                            reflist.append(a["text"])
            if reflist:
                parts.append("\n_Références : " + ", ".join(dict.fromkeys(reflist)) + "_\n")
        fname = f"{slug(f['title'], 70)}_{f.get('pubId', i)}.md"
        write(os.path.join(outdir, fname), "\n".join(parts))
        idx.append((f["title"], fname))
    write(os.path.join(outdir, "INDEX.md"), "# Index des fiches pratiques du ministère du Travail\n\n" +
          "\n".join(f"- [{t}]({fn})" for t, fn in idx))
    return len(F)

if __name__ == "__main__":
    what = sys.argv[1:]
    if "code" in what:
        n, v = export_code("LEGITEXT000006072050", "Code du travail", f"{OUT}/10-code-du-travail")
        print("Code du travail:", n, "fichiers, version", v)
    if "css" in what:
        # Sécurité sociale : seulement ce qui intéresse le salarié (AT/MP, IJ maladie/maternité, invalidité)
        keep = lambda crumbs: any(re.match(r"Livre (III|IV|IX) ", c) for c in crumbs)
        n, v = export_code("LEGITEXT000006073189", "Code de la sécurité sociale", f"{OUT}/11-code-securite-sociale-extraits", filter_fn=keep)
        print("CSS:", n, "fichiers")
    if "syntec" in what:
        s = export_convention(f"{RAW}/kali-data/package/data/KALICONT000005635173.json",
                              f"{OUT}/20-convention-syntec-idcc-1486", "Syntec (BETIC)", "1486",
                              "Données KALI à jour au 23/10/2026.")
        print("Syntec:", s)
    if "sf" in what:
        s = export_convention(f"{RAW}/old/package/data/KALICONT000005635810.json",
                              f"{OUT}/21-convention-societes-financieres-idcc-478", "Sociétés financières", "478",
                              "ATTENTION : extraction KALI datée de novembre 2023 ; voir MISES-A-JOUR-2023-2026.md pour les accords postérieurs.")
        print("SF:", s)
    if "fiches" in what:
        print("Fiches ministère:", export_fiches_travail(f"{OUT}/30-fiches-ministere-travail"))
