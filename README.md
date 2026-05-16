# Traning_app monorepo

This repository contains:

- **`admin_pan/`** — Git submodule: admin / React shell ([`admin_pan`](https://github.com/selcuk-yalcin/admin_pan)).
- **`training_app/`** — Python presentation engine (FastAPI, ingest, `traning_app` package, tests, `SPEC.md`, `storage/`).

Work on the engine from the nested project root:

```bash
cd training_app
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Keep a local **`.env`** either in this repo root or under `training_app/` (see `training_app/.env.example`).

**Nerede ne var:** Detaylı dizin haritası için [`training_app/README.md`](training_app/README.md) içindeki *Proje haritası* bölümüne bakın.
