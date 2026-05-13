#!/usr/bin/env python3
"""Write sample .pptx files from bundled JSON deck templates into assets/templates/samples/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from traning_app.deck.loaders import list_builtin_template_ids, load_builtin_deck_template
from traning_app.export.pptx_export import deck_to_pptx


def main() -> None:
    out_dir = ROOT / "assets" / "templates" / "samples"
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
    empty = ROOT / "assets" / "templates" / "empty.pptx"
    empty.parent.mkdir(parents=True, exist_ok=True)
    from pptx import Presentation

    prs = Presentation()
    prs.save(str(empty))
    print(f"Wrote {empty}")


if __name__ == "__main__":
    main()
