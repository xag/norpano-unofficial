"""Which of the catalogue's tables are read, as which line, and the boards they say are sold.

`rows(tables)` turns the tables tools/tables.py read into one row per board: a table is read only when
`LINES` names its heading; a row of a table whose rows are species or woods is read only when its first
word is one the table's dict names. What is left out, and why, is in the README.
"""

from __future__ import annotations

import re

URL = "https://www.norpano.fr/brochures/catalogue-general-2026-norpa_1.pdf"
PAGES = (5, 72)  # PDF pages 6 to 72, from 0: panels, decorative panels, synthetic resin
FMT = re.compile(r"(\d{3,4})\s*[xX×]\s*(\d{3,4})")

SPECIES = {"chene": "lamelle-colle-chene", "hetre": "lamelle-colle-hetre", "frene": "lamelle-colle-frene"}
THREE_PLY = {"epicea": "panneau-3-plis", "meleze": "panneau-3-plis", "douglas": "panneau-3-plis"}
LINES = {
    "m.d.f next standard": "mdf",
    "mdf medite clear ecologique": "mdf",
    "m.d.f": "mdf",
    "mediland": "mdf",
    "medium": "mdf",
    "medite": "mdf",
    "m.d.f bouche pore": "mdf",
    "m.d.f ctbh": "mdf-hydrofuge",
    "mediland ctbh": "mdf-hydrofuge",
    "medium ctbh": "mdf-hydrofuge",
    "m.d.f teinte fibracolor noir": "mdf-teinte",
    "m.d.f teinte valchromat noir gris clair gris fonce": "mdf-valchromat",
    "contreplaques peuplier pure gluetm": "contreplaque-peuplier",
    "contreplaques tout peuplier collage interieur": "contreplaque-peuplier",
    "contreplaques peuplier b bb fil travers": "contreplaque-peuplier",
    "contreplaques peuplier face hdf": "contreplaque-peuplier",
    "contreplaques exotiques collage interieur qualite import": "contreplaque",
    # Twin names the wood of the faces, not of the core: read as a plywood of unstated species
    "contreplaques twin okoume pure gluetm": "contreplaque",
    "contreplaques twin okoume collage interieur": "contreplaque",
    "contreplaques twin okoume collage exterieur ctbx": "contreplaque",
    "contreplaques tout pin": "contreplaque-pin",
    "contreplaques tout bouleau s bb": "contreplaque-bouleau",
    "contreplaques bouleau filmes lisses brun clair": "contreplaque-bouleau-filme",
    "contreplaques coffrage filmes lisses": {"bouleau": "contreplaque-bouleau-filme"},
    "contreplaques filme antiderapants": {"bouleau": "contreplaque-bouleau-filme"},
    "panneaux osb3 resineux peuplier": "osb-3",
    "panneaux osb3 resineux pour contreventement": "osb-3",
    "agglomeres standards": "agglomere",
    "agglomeres hydrofuges ctbh": "agglomere-hydrofuge",
    "melamines blancs moyen w908 sm": "melamine",
    "melamines blancs moyen std lisse graine": "melamine",
    "melamines blancs super w980 sm st7": "melamine",
    "melamines blancs super finition pore bois": "melamine",
    "panneau patchwood 4000 x 950mm": SPECIES,
    "panneau prolam 4500 x 1100mm": SPECIES,
    "panneaux massifs pannomass traditionnels 2500 x 1250mm hors sipo et noyer 2650 x 1250mm": SPECIES,
    "panneaux massifs panoplot longueur variable x 950mm": SPECIES,
    "panneaux massifs prolam longueur variable x1220mm": SPECIES,
    "panneaux massifs epicea 5000 x 1220mm et 2500 x 1220mm": {"epicea": "lamelle-colle-epicea"},
    "panneaux massifs 3plis resineux 5000 x 2050mm et 2500 x 2050mm": THREE_PLY,
    "panneaux massifs 3plis fineline": "panneau-3-plis",
}
# Lengths a table lists under it, for a heading that says "longueur variable"
LENGTHS = {
    "panneaux massifs panoplot longueur variable x 950mm": [1400, 1600, 1800, 2000, 2200, 2400],
    # "selon arrivage : 2000 à 3000mm pour multiples de 100mm"
    "panneaux massifs prolam longueur variable x1220mm": list(range(2000, 3001, 100)),
}
# What a table's asterisk says a starred mark is also sold as
STARRED = {
    "panneaux massifs pannomass traditionnels 2500 x 1250mm hors sipo et noyer 2650 x 1250mm":
        [(2000, 1250), (3000, 1250)],
    "panneaux massifs 3plis resineux 5000 x 2050mm et 2500 x 2050mm": [(5000, 1250), (2500, 1250)],
}
# The Pannomass table heads a column "2mm" between 22 and 28 mm, a thickness no solid wood panel is sold
# at: a misprint, whose column is not read.
MISPRINTS = {("panneaux massifs pannomass traditionnels 2500 x 1250mm hors sipo et noyer 2650 x 1250mm", 2.0)}


def plain(text: str) -> str:
    from wood_panels.shops import plain as p
    return p(text)


def rows(tables: list[dict]) -> list[dict]:
    """The boards the tables say are sold, one row each: {id, page, table, row, line, thickness_mm,
    length_mm, width_mm, sold, also}. `sold` is "stock" for a tick and "to order" for "sur commande"; the
    sheet's first dimension, as the catalogue gives it, is along the grain ("Fil travers 1220 x 3050").
    A board two tables list is the first one's row, the later pages in its `also`."""
    out: dict[tuple, dict] = {}
    for n, t in enumerate(tables):
        key = plain(t["heading"])
        spec = LINES.get(key)
        if spec is None:
            continue
        head = [(int(a), int(b)) for a, b in FMT.findall(t["heading"])]
        if key in LENGTHS:
            width = int(re.search(r"x\s*(\d{3,4})", t["heading"]).group(1))
            head = [(length, width) for length in LENGTHS[key]]
        for r, row in enumerate(t["rows"]):
            if isinstance(spec, dict):
                line = spec.get(plain(row["label"]).split(" ")[0]) if row["label"] else None
            else:
                line = spec
            if line is None:
                continue
            sheets = [(int(a), int(b)) for a, b in FMT.findall(row["label"])] or head
            for thickness, mark in row["marks"].items():
                th = float(thickness)
                if not mark.startswith(("tick", "on-order")) or (key, th) in MISPRINTS:
                    continue
                extra = STARRED.get(key, []) if mark.endswith("*") else []
                for length, width in sheets + [s for s in extra if s not in sheets]:
                    k = (line, th, length, width)
                    if k in out:
                        out[k]["also"].append(t["page"])
                        continue
                    out[k] = {"id": f"{t['page']}-{n}-{r}-{thickness.replace('.', '-')}-{length}x{width}",
                              "page": t["page"], "table": t["heading"], "row": row["label"], "line": line,
                              "thickness_mm": th, "length_mm": float(length), "width_mm": float(width),
                              "sold": "to order" if mark == "on-order" else "stock", "also": []}
    return list(out.values())
