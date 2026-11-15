"""The wood panels Norpano lists in its general catalogue, as data on furniture-design's kinds (source,
clause, material), each line read as a board of wood-panels. Unofficial: Norpano neither wrote nor
endorsed it.

What the shop sells comes from the thickness x format tables of its 2026 general catalogue (range.json,
read by tools/read_catalogue.py): every board a table ticks, its line, thickness and sheet. Each is a
clause under sources/norpano-catalogue-2026, located by its page, table and row. wood_panels.shops makes
the materials: one per line and thickness, `norpano-<line>-<thickness>`, its payload `shop` saying what is
sold and which board its values are.

Its cutting service is a tool, tools/norpano-cutting-service: its services page says it cuts on a beam saw
(scie à plat) and prints no cut, so its payload's blade names saws' usual beam-saw blade, the tool a design
cut at Norpano is sawn with until the shop gives its cut.

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
from furniture_design.knowledge import with_authority
from wood_panels import shops

from .catalogue import URL

HERE = Path(__file__).parent
SHOP = "Norpano"
PREFIX = "norpano"
SOURCE = "norpano-catalogue-2026"
FETCHED = "2026-11-14"
SERVICES = "norpano-services-page"
SERVICES_URL = "https://www.norpano.fr/services.html"
USUAL_BLADE = "tools/usual-panel-sizing-blade"  # in the saws package


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


def services() -> Node:
    """The page where Norpano describes its workshop: what it says of its cutting, by locator, in our words."""
    return Node(id=SERVICES, kind="source", name=f"Norpano, its services ({SERVICES_URL})",
                payload={"publisher": SHOP, "year": 2026, "url": SERVICES_URL, "fetched": "2026-11-15",
                         "licence": "copyrighted",
                         "capture": "private copy, sha256 422aa5e61886625c998fd8bb9cad13d207c380e36a9dd2d0f72889922d20aa2e"},
                children=[Node(id="panel-cutting", kind="clause",
                               payload={"locator": "L'atelier de transformation de panneaux, its first item",
                                        "in_our_words": "the workshop cuts every kind of raw, melamine-faced, "
                                                        "veneered and compact panel on a numerically controlled "
                                                        "beam saw (scie à plat); the page gives no cut, no blade "
                                                        "and no narrowest part"})])


def cutting_service() -> Node:
    """Norpano's cutting service as a tool a part links sawn_with: a beam saw, its cut unstated, so the cut rule
    refuses it; its payload's blade names the usual beam-saw blade a design is sawn with instead."""
    return Node(id="norpano-cutting-service", kind="tool", name="Norpano's cutting service",
                payload={"maker": SHOP, "saw_kind": "panel saw",
                         "does": "cuts the panels it sells to the customer's sizes on a beam saw (scie à plat)",
                         "blade": {"usual": USUAL_BLADE, "per": f"sources/{SERVICES}/panel-cutting"}},
                links={"per": [f"sources/{SERVICES}/panel-cutting"]})


# Who stands behind each source (furniture-design's AUTHORITIES).
AUTHORITY = {
    "norpano-catalogue-2026": "maker",
    "norpano-services-page": "maker",
}


def knowledge() -> list[Node]:
    """The branches to merge beside furniture-design's and wood-panels's: the sources, the materials and the
    cutting service as a tool."""
    return [Node(id="sources", kind="", children=with_authority([catalogue(rows()), services()], AUTHORITY)),
            Node(id="materials", kind="", children=shops.materials(PREFIX, SHOP, f"sources/{SOURCE}", rows())),
            Node(id="tools", kind="", children=[cutting_service()])]
