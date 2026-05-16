# Training engine (`traning-app`)

Agentic multimodal presentation generation: ingest → deck JSON → PPTX/HTML export.

- **Spec:** [`SPEC.md`](SPEC.md)
- **Backlog:** [`TODO.md`](TODO.md)
- **Architecture notes:** [`src/traning_app/specs/`](src/traning_app/specs/)

## Proje haritası (ne nerede?)

| Ne arıyorsun? | Nerede |
|----------------|--------|
| HTTP API, route’lar | `src/traning_app/api/` — giriş `main.py`, sunumlar `routes/presentations.py` |
| Ayarlar / env | `src/traning_app/config/settings.py`, kökte `training_app/.env.example` |
| İş akışı (plan → deck → tema) | `src/traning_app/engine/agents/pipeline.py` (`run_job`) |
| LLM, router, PPTX/HTML, TTS, tema | `src/traning_app/engine/agents/*.py` (düz modüller) |
| Eski import yolları (shim) | `engine/export/`, `engine/layout/`, `engine/providers/` |
| Deck JSON şema, şablonlar, katalog | `src/traning_app/engine/deck/`, paket verisi `src/traning_app/templates/` |
| PDF / URL / birleşik context | `src/traning_app/engine/ingest/` — `context.py`, `intake.py`, `validation.py`, `constants.py`, `pdf.py`, `url.py`, `html_plain.py` |
| Job store, aşamalar, runner sarmalayıcı | `src/traning_app/engine/orchestrator/` |
| SSE olay tipleri | `src/traning_app/engine/events/` |
| Arka plan görev girişi | `src/traning_app/engine/workers/tasks.py` |
| Örnek PPTX üretimi | `src/traning_app/scripts/export_sample_pptx.py` → çıktı `src/traning_app/assets/templates/` |
| API’yi ayağa kaldırma (script) | `src/traning_app/scripts/run_api.sh` |
| Deck JSON örnek şema (dosya) | `src/traning_app/schemas/` |
| Ürün + mimari metin (plan) | `src/traning_app/specs/plan.md` |
| Create project adım akışı (UX) | [`src/traning_app/specs/roadmap.md#create-project-flow`](src/traning_app/specs/roadmap.md#create-project-flow) |
| Gereksinimler, backlog | `SPEC.md`, `TODO.md` (bu klasör kökü) |
| Çalışma zamanı dosya alanı | `storage/incoming/`, `storage/exports/` |
| Testler | `tests/` |
| Admin / React UI | Üst dizinde `../admin_pan/` — Deep Training `/deep-training`, proje oluşturma `/create-project` |

```text
Traning_app/                    # monorepo kökü
├── admin_pan/                  # submodule — panel
├── training_app/               # Python motoru (cd buraya)
│   ├── SPEC.md  TODO.md  pyproject.toml
│   ├── storage/
│   ├── tests/
│   └── src/traning_app/
│       ├── api/
│       ├── config/
│       ├── engine/
│       │   ├── agents/       # L2+L3: pipeline, llm, export, …
│       │   ├── deck/
│       │   ├── ingest/
│       │   ├── orchestrator/
│       │   ├── events/
│       │   ├── workers/
│       │   ├── export|layout|providers/   # ince shim’ler
│       │   └── media/
│       ├── templates/        # decks JSON, themes
│       ├── assets/           # örnek pptx çıktıları (script)
│       ├── schemas/
│       ├── scripts/
│       └── specs/            # plan, roadmap (SPEC’e linkli)
└── README.md
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Run the API (from this directory):

```bash
uvicorn traning_app.api.main:app --reload
```

Sample PPTX export:

```bash
python src/traning_app/scripts/export_sample_pptx.py
```

`admin_pan` içinden motor API’sine bağlanmak için Vite env: **`VITE_TRAINING_API_URL`** (örn. `http://127.0.0.1:8000`).
