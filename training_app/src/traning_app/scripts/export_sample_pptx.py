#!/usr/bin/env python3
"""Write sample .pptx files from bundled JSON deck templates into assets/templates/samples/."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_SRC_ROOT = _SCRIPT.parents[2]  # .../training_app/src
_PKG_ROOT = _SCRIPT.parents[1]  # .../traning_app (importable package tree)
sys.path.insert(0, str(_SRC_ROOT))

from traning_app.engine.deck.loaders import list_builtin_template_ids, load_builtin_deck_template
from traning_app.engine.agents.pptx_export import deck_to_pptx


def main() -> None:
    out_dir = _PKG_ROOT / "assets" / "templates" / "samples"
    out_dir.mkdir(parents=True, exist_ok=True)
    ids = list_builtin_template_ids()
    if not ids:
        print("No bundled JSON templates found under traning_app/templates/decks/", file=sys.stderr)
        sys.exit(1)
    for tid in ids:
        deck = load_builtin_deck_template(tid)
        dest = out_dir / f"{tid}.pptx"
        deck_to_pptx(deck, str(dest))
        print(f"Wrote {dest}")
    empty = _PKG_ROOT / "assets" / "templates" / "empty.pptx"
    empty.parent.mkdir(parents=True, exist_ok=True)
    from pptx import Presentation

    prs = Presentation()
    prs.save(str(empty))
    print(f"Wrote {empty}")


if __name__ == "__main__":
    main()
