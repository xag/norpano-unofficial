"""Read Norpano's range from its general catalogue: python tools/read_catalogue.py <the PDF> <fetched on>.

Reads every thickness x format table of the panel pages (tools/tables.py), keeps the private copy of what
was read in xag/furniture (sources/norpano/catalogue-tables.json, with the PDF's sha256), and writes
norpano_unofficial/range.json from it by `norpano_unofficial.catalogue.rows`, which the tests run again on
the private copy.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]

import tables as reader  # noqa: E402
from norpano_unofficial.catalogue import PAGES, URL, rows  # noqa: E402

PRIVATE = Path(os.environ.get("FURNITURE_REPO", ROOT.parent / "furniture")) / "sources" / "norpano"

pdf_path = Path(sys.argv[1])
raw = reader.read(pdfplumber.open(pdf_path), range(*PAGES))
PRIVATE.mkdir(parents=True, exist_ok=True)
(PRIVATE / "catalogue-tables.json").write_text(json.dumps(
    {"url": URL, "fetched": sys.argv[2], "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
     "pdf_pages": [PAGES[0] + 1, PAGES[1]], "tables": raw}, ensure_ascii=False, indent=0), encoding="utf-8")
got = rows(raw)
(ROOT / "norpano_unofficial" / "range.json").write_text(json.dumps(got, ensure_ascii=False, indent=0),
                                                        encoding="utf-8")
print(len(raw), "tables,", len(got), "boards")
