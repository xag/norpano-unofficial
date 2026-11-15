# norpano-unofficial

The wood panels Norpano sells, as data for [furniture-design](https://github.com/xag/furniture-design). **Unofficial**: Norpano did not write or endorse it, and nothing here speaks for it.

## What is here

- **The range**: 389 boards read from the thickness × format tables of Norpano's 2026 general catalogue (https://www.norpano.fr/brochures/catalogue-general-2026-norpa_1.pdf, the panel pages), each with its line, thickness and sheet, whether it is sold from stock (a tick) or to order (*sur commande*), and where the catalogue gives it (page, table, row). The sheet's first dimension is along the grain, as the catalogue writes it (*Fil travers 1220 x 3050*). 16 lines: agglomere, agglomere-hydrofuge, contreplaque, contreplaque-bouleau, contreplaque-bouleau-filme, contreplaque-peuplier, contreplaque-pin, lamelle-colle-chene, lamelle-colle-epicea, lamelle-colle-frene, lamelle-colle-hetre, mdf, mdf-hydrofuge, melamine, osb-3, panneau-3-plis. What a given branch has on the day is not in the catalogue.
- **The materials**: one per line and thickness (`materials/norpano-<line>-<thickness>`), two for a board that bends differently along and across. [wood-panels](https://github.com/xag/wood-panels)'s `shops` module gives each line its values: a class's (P2, P3, MDF, OSB/3), a maker's board of the same type, or a species of furniture-design, ungrounded unless the line names the maker; the payload `shop` says what is sold and which board the values are.
- **The cutting service**: `tools/norpano-cutting-service`. Norpano's services page (https://www.norpano.fr/services.html) says its workshop cuts every kind of panel on a numerically controlled beam saw (*scie à plat*) and gives no cut, no blade and no narrowest part, so the tool states no cut and furniture-design's rule refuses a part sawn with it. Its payload's `blade` names [saws](https://github.com/xag/saws)' `tools/usual-panel-sizing-blade` (the widest cut of the beam-saw blades Leitz and CMT both list, 5.2 mm; 4.4 mm for most of them), which a part cut at Norpano links `sawn_with` until the shop states its cut.

Not read: boards whose treatment or build no line of wood-panels reads (fire-retardant M1, anti-slip, water-resistant and fire-retardant melamine, exterior MDF, Tricoya, honeycomb, bendable, light MDF, blockboard, compact), veneered boards, floor slabs, worktops, veneer sheets, woods no line has (ceiba, beech plywood, hévéa, sipo, walnut, oak 3-ply, Baubuche), and the décor melamines, whose formats the catalogue states in prose and not in a table. A Twin okoumé plywood is read as a plywood of unstated species: Twin names the wood of its faces, and the catalogue does not say the core's. The Pannomass table heads one column "2mm", between 22 and 28 mm; that column is not read.

No kinds and no rules of its own: a part that `uses` one of these materials is judged by furniture-design's rules, and its cutting sheet is laid on the sheets listed here.

## Sources

The catalogue was fetched on 2026-11-14. The tables read from it are kept in a private repo with the PDF's sha256, and `tests/test_values.py` checks that the range is what they say and that rows read by eye from the rendered pages are what the reader took: clone that repo beside this one, or set `FURNITURE_REPO`, or those tests fail and say why. `tools/read_catalogue.py <the PDF> <date>` reads it again.

## Using it

```python
from furniture_design.knowledge import knowledge as general, merge
from wood_panels import knowledge as wood_panels
from norpano_unofficial import knowledge as norpano

tree.root.children = merge(general(), wood_panels(), norpano()) + [pieces]
```

## Design ledger

```sh
uv sync
uv run quern brief .
uv run quern check
```

There is no flight-recorder boundary: nothing here touches storage, the network, the clock or randomness at run time.

## Licence

- **The code** (`norpano_unofficial/*.py`, `tools/`, `tests/`, `ledger/`) is licensed under the [GNU Affero General Public License v3.0 or later](LICENSE), copyright 2026 Xavier Grehant.
- **The knowledge base**, the database `norpano_unofficial.knowledge()` returns (range.json and every value on its nodes), is licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0](LICENSE-DATA), database rights included, with one added permission: designing, building and selling furniture with it is allowed. An improvement is published here, through [CONTRIBUTING.md](CONTRIBUTING.md).
- Norpano's product names and sizes are cited from its catalogue, not licensed.

## Tests

`uv run pytest` runs the tests whose code, data or packages changed since they passed, last failures first then the fastest, under a time budget (testplan); `uv run pytest --all` runs them all, once a day. Both stop at the first failure.
