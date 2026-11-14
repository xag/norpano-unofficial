"""The wood panels Norpano lists in its general catalogue, as data on furniture-design's kinds (source,
clause, material), each line read as a board of wood-panels. Unofficial: Norpano neither wrote nor
endorsed it.

What the shop sells comes from the thickness x format tables of its 2026 general catalogue (range.json,
read by tools/read_catalogue.py): every board a table ticks, its line, thickness and sheet. Each is a
clause under sources/norpano-catalogue-2026, located by its page, table and row. wood_panels.shops makes
the materials: one per line and thickness, `norpano-<line>-<thickness>`, its payload `shop` saying what is
sold and which board its values are.

    from furniture_design.knowledge import knowledge as general, merge
    from wood_panels import knowledge as wood_panels
    from norpano_unofficial import knowledge as norpano
    tree.root.children = merge(general(), wood_panels(), norpano()) + [pieces]
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from quern.provenance import Quantity
from quern.tree import Node
from wood_panels import shops

from .catalogue import URL

HERE = Path(__file__).parent
SHOP = "Norpano"
PREFIX = "norpano"
SOURCE = "norpano-catalogue-2026"
FETCHED = "2026-11-14"


@lru_cache(maxsize=1)
def rows() -> list[dict]:
    return json.loads((HERE / "range.json").read_text(encoding="utf-8"))


def _q(value: float, where: str) -> Quantity:
    return Quantity(value=float(value), unit="mm", provenance="published", grounded=True, source=where,
                    note="as the catalogue's table gives it")


def catalogue(rows: list[dict]) -> Node:
    """The catalogue as a source, one clause per board its tables say is sold. A clause's payload `ref` is
    empty: the catalogue gives no product number, and a cutting sheet prints none."""
    clauses = [Node(id=f"p-{r['id']}", kind="clause",
                    payload={"locator": f"p. {r['page']}, table '{r['table']}', row '{r['row']}', "
                                        f"column {r['thickness_mm']:g} mm",
                             "also_on_pages": r["also"], "line": r["line"], "sold": r["sold"], "ref": ""},
                    params={"thickness": _q(r["thickness_mm"], "the table's column"),
                            "length": _q(r["length_mm"], "the table's row or heading"),
                            "width": _q(r["width_mm"], "the table's row or heading")})
               for r in rows]
    return Node(id=SOURCE, kind="source", name="Norpano, Catalogue général 2026",
                payload={"publisher": SHOP, "year": 2026, "url": URL, "fetched": FETCHED,
                         "licence": "copyrighted",
                         "capture": "private copy of the tables read, with the PDF's sha256",
                         "in_our_words": "what the shop sells, ticked in stock or sold to order; not what a "
                                         "given branch has on the day"},
                children=clauses)


def knowledge() -> list[Node]:
    """The branches to merge beside furniture-design's and wood-panels's: the source, the materials."""
    return [Node(id="sources", kind="", children=[catalogue(rows())]),
            Node(id="materials", kind="", children=shops.materials(PREFIX, SHOP, f"sources/{SOURCE}", rows()))]
