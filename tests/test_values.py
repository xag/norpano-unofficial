"""The range against the tables it was read from, the reading against the pages, and the data against
furniture-design's rules.

The tables read are kept in the private repo xag/furniture, checked out beside this one (or at
$FURNITURE_REPO), under sources/norpano/. Without them these tests fail, saying where they looked, and
never skip.
"""

import json
import os
import re
from pathlib import Path

from quern import Quern, run_rules

from furniture_design.knowledge import knowledge as general, merge
from furniture_design.package import PACKAGE
from wood_panels import knowledge as wood_panels
from wood_panels.shops import BY_ID
from norpano_unofficial import knowledge, rows
from norpano_unofficial.catalogue import LINES, URL
from norpano_unofficial.catalogue import rows as read_rows

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources" / "norpano" / \
    "catalogue-tables.json"


def _captured() -> dict:
    assert CAPTURE.exists(), (f"the private copy {CAPTURE} is missing: clone xag/furniture beside this repo or "
                              "set FURNITURE_REPO")
    return json.loads(CAPTURE.read_text(encoding="utf-8"))


def _table(captured: dict, page: str, heading: str) -> dict:
    found = [t for t in captured["tables"] if t["page"] == page and t["heading"] == heading]
    assert len(found) == 1, (page, heading, len(found))
    return found[0]


def test_the_range_is_what_the_tables_read_say():
    captured = _captured()
    assert captured["url"] == URL and re.fullmatch(r"[0-9a-f]{64}", captured["sha256"])
    assert read_rows(captured["tables"]) == rows()


# Rows read by eye from the pages as rendered, against what the reader took from the text layer
BY_EYE = [
    ("22", "CONTREPLAQUÉS TOUT BOULEAU S/BB", "1500 x 3000", {t: "tick" for t in ("9", "12", "15", "18", "21", "24", "27")}),
    ("22", "CONTREPLAQUÉS TWIN OKOUMÉ COLLAGE INTÉRIEUR", "3100 x 1830",
     {"3": "none", "5": "tick", "6": "none", "8": "tick", "10": "tick", "12": "none", "15": "tick", "18": "tick",
      "19": "none", "22": "none", "25": "none", "30": "none", "40": "none"}),
    ("12", "M.D.F NEXT® STANDARD", "2800 x 2070",
     {"6": "on-order", "8": "on-order", "10": "tick", "12": "on-order", "16": "tick", "19": "tick", "22": "tick"}),
    ("17", "PANNEAUX OSB3 RÉSINEUX POUR CONTREVENTEMENT", "RESINEUX 2800 x 1196", {"9": "tick", "12": "tick", "13": "none"}),
    ("16", "PANNEAUX MASSIFS 3PLIS RÉSINEUX : 5000 x 2050mm et 2500 x 2050mm", "Mélèze de pays A/B",
     {"13": "tick", "15": "tick", "19": "tick", "22": "none", "26": "tick", "27": "none", "32": "none", "42": "none"}),
    ("60", "PANNEAUX MASSIFS PANNOMASS TRADITIONNELS : 2500 x 1250mm (hors Sipo et Noyer 2650 x 1250mm)",
     "Hêtre étuvé", {"13": "tick", "21": "tick", "22": "none", "2": "tick", "28": "none", "36": "none", "40": "tick"}),
]


def test_rows_read_by_eye_are_what_the_reader_took():
    captured = _captured()
    for page, heading, label, marks in BY_EYE:
        row, = [r for r in _table(captured, page, heading)["rows"] if r["label"] == label]
        assert row["marks"] == marks, (page, heading, label)


def test_every_line_read_is_one_wood_panels_knows():
    lines = {v for s in LINES.values() for v in (s.values() if isinstance(s, dict) else [s])}
    assert lines <= set(BY_ID) and {r["line"] for r in rows()} <= lines


def test_birch_plywood_18_is_sold_in_its_two_sheets():
    mats = {m.id: m for b in knowledge() if b.id == "materials" for m in b.children}
    birch = [m for i, m in mats.items() if i.startswith("norpano-contreplaque-bouleau-18")]
    assert birch and all(m.payload["shop"]["sheets_mm"] == [(1500.0, 3000.0), (2500.0, 1250.0)] for m in birch)


def test_no_two_materials_share_an_id():
    ids = [m.id for b in knowledge() if b.id == "materials" for m in b.children]
    assert len(ids) == len(set(ids))


def test_the_data_passes_furniture_designs_rules():
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(general(), wood_panels(), knowledge())
    assert [(r.rule, r.node, r.verdict) for r in run_rules(tree) if not r.ok] == []


def test_the_cutting_service_is_a_beam_saw_that_prints_no_cut_and_names_the_usual_beam_saw_blade():
    tools = {n.id: n for b in knowledge() if b.id == "tools" for n in b.children}
    service = tools["norpano-cutting-service"]
    assert "kerf" not in (service.params or {}) and "max_kerf" not in (service.params or {})
    assert service.payload["blade"]["usual"] == "tools/usual-panel-sizing-blade"
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = merge(general(), wood_panels(), knowledge())
    assert all(tree.get(p) is not None for p in service.links["per"])
