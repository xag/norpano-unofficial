"""The decisions norpano-unofficial is bound by, as a ledger. Read it with `uv run quern brief .`, never whole.

Vocabulary: ledger@0.8.0 and grounding@1.2.0, pinned in quern.lock.
"""

from __future__ import annotations

import os
from pathlib import Path

import quern.grounding  # noqa: F401
from quern import Node, Quern
from quern.library import consume

OWNER = "Tu feras aussi un Norpaneau unofficial ainsi que pour les autres chaines"


def _alt(id_: str, name: str, why: str) -> Node:
    return Node(id=id_, kind="alternative", name=name, payload={"why": why})


def entries() -> list[Node]:
    return [
        Node(
            id="the-range-is-read-from-the-general-catalogue", kind="decision",
            name="Norpano's range is what the thickness x format tables of its general catalogue tick "
                 "(https://www.norpano.fr/brochures/catalogue-general-2026-norpa_1.pdf, PDF pages 6 to 72), read "
                 "from the PDF's text layer by the position of each mark under its column; a tick is sold from "
                 "stock, 'sur commande' to order. The tables read are kept privately with the PDF's sha256. What "
                 "a given branch has on the day is not in it",
            payload={"decided_on": "2026-11-14",
                     "the_owner": OWNER + " / Ils ont un site avec des catalogues",
                     "why": "The catalogue is the one place Norpano states its boards' sizes: its site's category "
                            "pages name the products without sizes. pdftotext's layout puts a column's marks on "
                            "the wrong line, so the marks are placed by their x position."},
            children=[
                _alt("the-category-pages", "Read the site's category pages",
                     "They name the products (e.g. vente-panneau-interieur-c1.html) and give no size."),
                _alt("the-text-layout", "Read the tables from pdftotext -layout",
                     "It shifts marks to the line above and drops the glyphs of some ticks."),
            ],
        ),
        Node(
            id="a-board-is-read-only-as-a-line-wood-panels-knows", kind="decision",
            name="A table is read only when catalogue.LINES names its heading as one of wood_panels.shops' lines, "
                 "so its material takes that line's values. Left out: boards whose treatment or build no line "
                 "reads (fire-retardant M1, anti-slip, water-resistant melamine, exterior MDF, Tricoya, honeycomb, "
                 "bendable, light MDF, blockboard, compact), veneered boards (the face is not the board), floor "
                 "slabs, worktops, veneer sheets, woods no line has (ceiba, beech plywood, hévéa, sipo, walnut, "
                 "oak 3-ply, Baubuche), and the décor melamines, whose formats are stated in prose, not in a "
                 "table. A Twin okoumé plywood is read as a plywood of unstated species",
            links={"rests_on": ["the-range-is-read-from-the-general-catalogue"]},
            payload={"decided_on": "2026-11-14", "the_owner": OWNER,
                     "why": "Twin names the wood of the faces and the catalogue does not say the core's; the "
                            "stand-in for an unstated species is the less stiff of the French plywoods. A board "
                            "read as a line whose values it may not have would be judged on them."},
            children=[
                _alt("twin-as-okoume", "Read a Twin okoumé as an okoumé plywood",
                     "Its core may be another wood, and an all-okoumé board's values would then overstate it."),
                _alt("every-table", "Read every table, the unknown ones as boards without values",
                     "A material with no values cannot be judged, and the cutting sheet gains nothing from a "
                     "board no rule can check."),
            ],
        ),
    ]


def build() -> Quern:
    root = Path(__file__).resolve().parents[1]
    lib, refs = consume(root, os.environ.get("QUERN_REGISTRY", root.parent / "quern-registry"))
    quern = Quern(packages=list(refs))
    quern = lib.effective(quern)
    quern.root.children = entries()
    return quern
