"""Read the thickness x format tables of Norpano's catalogue from the PDF's text layer.

A table is a dark bar with the product's name in white, a header row (`Épaisseur`, or
`Essence/Épaisseur`, then one column per thickness) and rows that start with a sheet size or a species,
one mark per thickness: a tick (a Wingdings glyph) where the size is stocked, `-` where it is not, `sur
commande` where it is sold to order. Only the catalogue's table fonts are read (FuturaLT, Wingdings):
some pages carry, under their pictures, the text of another document in other fonts.
"""

from __future__ import annotations

import re

TABLE_FONTS = ("FuturaLT", "Wingdings")
NUMCOL = re.compile(r"^(\d+(?:[.,]\d+)?)(?:mm)?$")
HEADER = re.compile(r"[ÉE]pais")


def _lines(page) -> list[tuple[float, list[dict]]]:
    ws = [w for w in page.extract_words(extra_attrs=["fontname", "non_stroking_color"])
          if any(f in w["fontname"] for f in TABLE_FONTS)]
    ws.sort(key=lambda w: (w["top"], w["x0"]))
    out: list[list] = []
    for w in ws:
        if out and abs(out[-1][0] - w["top"]) <= 3.5:
            out[-1][1].append(w)
        else:
            out.append([w["top"], [w]])
    return [(top, sorted(row, key=lambda w: w["x0"])) for top, row in out]


def _mark(ws: list[dict]) -> str:
    text = " ".join(w["text"] for w in ws).strip()
    if any("Wingdings" in w["fontname"] for w in ws):
        return "tick" + ("*" if "*" in text else "")
    if re.fullmatch(r"[-–]+", text):
        return "none"
    if "commande" in text or text == "sur":
        return "on-order"
    return "?" + text


def _is_mark(w: dict) -> bool:
    return "Wingdings" in w["fontname"] or w["text"] in ("-", "–", "sur", "commande")


def _printed(page, lines) -> str:
    return next((w["text"] for top, ws in lines for w in ws
                 if top > page.height * 0.92 and w["text"].isdigit() and len(w["text"]) <= 3), "?")


def read(pdf, pages) -> list[dict]:
    """Every table on the given page indices: {index, page, heading, thicknesses, rows: [{label, marks}]}."""
    tables = []
    for i in pages:
        page = pdf.pages[i]
        lines = _lines(page)
        printed = _printed(page, lines)
        for li, (top, ws) in enumerate(lines):
            labels = [w for w in ws if HEADER.search(w["text"])]
            for k, lab in enumerate(labels):
                x0 = lab["x0"]
                x1 = labels[k + 1]["x0"] if k + 1 < len(labels) else page.width
                cols = []
                for w in ws:
                    m = NUMCOL.match(w["text"])
                    if x0 < w["x0"] < x1 and m and w["x0"] > lab["x1"]:
                        cols.append((float(m.group(1).replace(",", ".")), (w["x0"] + w["x1"]) / 2))
                if not cols:
                    continue
                heading = ""
                for top2, ws2 in reversed(lines[:li]):
                    seg = [w for w in ws2 if x0 - 25 <= w["x0"] < x1]
                    if top - top2 > 30:
                        break
                    if seg:
                        heading = " ".join(w["text"] for w in seg)
                        break
                gap = (cols[-1][1] - cols[0][1]) / (len(cols) - 1) if len(cols) > 1 else 60.0
                rows, last = [], top
                for top2, ws2 in lines[li + 1:]:
                    seg = [w for w in ws2 if x0 - 5 <= w["x0"] < x1]
                    if not seg:
                        continue
                    if top2 - last > 28 or any(HEADER.search(w["text"]) for w in seg) \
                            or any(w["non_stroking_color"] == (0.0, 0.0, 0.0, 0.0) for w in seg):
                        break
                    label, cells, in_label = [], {}, True
                    for w in seg:
                        centre = (w["x0"] + w["x1"]) / 2
                        if in_label and not _is_mark(w) and centre < cols[0][1] - gap / 2 + 25:
                            label.append(w)
                            continue
                        in_label = False
                        col = min(cols, key=lambda c: abs(c[1] - centre))
                        cells.setdefault(col[0], []).append(w)
                    text = " ".join(w["text"] for w in label)
                    if not text and rows:
                        for c, v in cells.items():
                            rows[-1][1].setdefault(c, []).extend(v)
                    else:
                        rows.append((text, cells))
                    last = top2
                tables.append({"index": i, "page": printed, "heading": heading,
                               "thicknesses": [c[0] for c in cols],
                               "rows": [{"label": t, "marks": {f"{c:g}": _mark(v) for c, v in sorted(cells.items())}}
                                        for t, cells in rows]})
    return tables
