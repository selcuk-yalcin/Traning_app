# Execution roadmap — Traning_app

**Source of tasks:** [`TODO.md`](../../../TODO.md) (under `training_app/`).

**Requirements:** [`SPEC.md`](../../../SPEC.md).

This file tracks **phase goals**, **layer completion**, and the **Create project** UX contract (aligned with [`plan.md`](./plan.md)).

---

<a id="create-project-flow"></a>

## Create project — adım adım ürün akışı (UX)

**Amaç:** `admin_pan` içinde **Create project** (`/create-project`) deneyimini, referans olarak verilen **Presentations.AI** tarzında: kaynak paylaşımı → yapılandırma → canlı işlem adımları → slayt özeti / outline → düzenleyici ve dışa aktarma.

**Motor API:** `training_app` — `POST /presentations/generate`, `GET /presentations/{job_id}/events`, `GET /presentations/{job_id}/events/stream` (SSE), `GET /presentations/{job_id}/deck`, `PUT /presentations/{job_id}/deck`, `GET /presentations/{job_id}/export/pptx`, `GET …/export/html`, `GET …/embed/html`, `GET …/export/mp4` (üretildiyse).  
**Ortam:** `VITE_TRAINING_API_URL` (Vite).

### Adım özeti (ekran sırası)

| # | Ekran (UI adımı) | Referans görsel | Kullanıcı aksiyonu | Motor / veri |
|---|------------------|-----------------|-------------------|--------------|
| **1** | **Kaynak paylaşımı** | Dosya sürükleyip bırakma, “Public URL” (OR); ileride Drive/Notion | PDF seçer ve/veya genel URL girer; **İleri** | Henüz istek yok; dosyalar bellekte, URL string |
| **2** | **Yapılandırma** | Prompt + slayt uzunluğu + model + dil + rol + şablon; TTS / görsel / MP4 seçenekleri | **Sunumu oluştur** | `GeneratePresentationRequest` gövdesi |
| **3** | **İşlem / düşünme** | Dikey stepper + alt görev metni | İzleme (otomatik) | SSE `events/stream` (yedek: `GET …/events` poll); `stage` + `detail` |
| **4** | **Outline / özet** | Numaralı kartlar, etiket (niyet), açılır detay | **Düzenleyiciye geç** | `GET …/deck` → `slides[]` → başlık + `type` etiketi |
| **5** | **Düzenleyici (L5)** | Canvas, tema/ses/paylaş, Kaydet, Sunum, dışa aktarma | **PPTX / HTML / MP4** | `PUT /deck`, `export/*`, `embed/html`, `slides/{i}/image` |

### Adım 1 — Kaynak paylaşımı (Layer 1 UI)

- **Dosya:** Şimdilik **PDF** (motor `pdf_base64`). Genişletme: `.txt`, `.docx` (ayrı ingest).
- **Public URL:** Tek satır input; gönderimde `sources: [{ type: "url", url }]` (motor URL çeker).
- **Google Drive / Notion:** MVP dışı; aynı ekranda gri/disabled kart veya “Yakında” metni kabul edilebilir.

**Doğrulama:** En az biri: dosya **veya** URL **veya** (sonraki adımda) anlamlı prompt — tamamen boş ilerlemeyi engelle.

### Adım 2 — Yapılandırma

- Şablon (`template_id`), `prompt`, `slide_length`, `tier`, `language`, `role`, isteğe bağlı `use_tts`, `use_slide_images`, `use_video`, `tts_provider`.
- **Sunumu oluştur** → `POST /presentations/generate` → dönen `job_id` ile **Adım 3**’e geç.

### Adım 3 — İşlem (stepper + alt metin)

**Canlı akış:** Öncelik `GET /presentations/{job_id}/events/stream` (SSE); bağlantı kopsa kısa aralıkla `GET …/events` poll. Son olayın `stage`, `detail`, `payload` alanları UI’da gösterilir.

**Önerilen eşleme (metinler Türkçe):**

| `stage` (motor) | Stepper durumu | Kısa açıklama |
|-----------------|----------------|---------------|
| `queued` / `planning` | 1 — aktif | “Plan oluşturuluyor…” |
| `research` | 1 — tamam, 2 — aktif | “Kaynaklar birleştiriliyor…” (`detail`) |
| `generating` | 2 — tamam, 3 — aktif | “Slaytlar üretiliyor…” + `detail` alt satır |
| `layout` | 3 — tamam, 4 — aktif | “Tema ve yerleşim…” |
| `tts` | 4 — tamam veya atlanmış | “Ses hazırlığı…” |
| `done` | Hepsi tamam | Otomatik **Adım 4** |
| `failed` | Hata kartı | `error` + yeniden dene |

### Adım 4 — Outline kartları

- `deck.slides` üzerinden liste: `index + 1`, `title` veya ilk metin alanı, sağda **etiket** = `slide.type` veya sabit eşleme (`title` → “Giriş”, `bullets` → “İçerik” …).
- Accordion: kart genişletildiğinde `bullets` / `notes` / `subtitle` özet metin.
- **Düzenleyiciye geç** → Adım 5.

### Adım 5 — Düzenleyici (L5)

- Sol: slayt listesi, **+** ile yeni slayt; seçili vurgu.
- Orta: **16:9 canvas** (tema renkleri), varsa kapak görseli `GET …/slides/{i}/image`.
- Alt: **inspector** — başlık, alt başlık, madde işaretleri, notlar; çoğalt / sil.
- Üst: **Geri al / Yinele**, **Tema** (hazır paletler), **Ses** (TTS varsa oynatıcı + hız), **Paylaş** (iframe embed), **Sunum** (tam ekran), **Kaydet** → `PUT …/deck`.
- Dışa aktarma: PPTX, HTML, MP4 (üretildiyse); embed: `GET …/embed/html`.

### Tasarım notları (referans UI)

- Tam ekran **gökyüzü / bulut** veya açık degrade arka plan; kartlarda **yarı saydam (glass)** + `backdrop-filter`.
- Üst sol **geri** (önceki adım veya `/deep-training`), üst sağ **kapat** → şablon galerisi veya dashboard.
- Alt durum çubuğu: “Oluşturuluyor…” spinner (Adım 3).

### Uygulama dosyaları (`admin_pan`)

| Parça | Konum |
|-------|--------|
| Sihirbaz sayfası | `admin_pan/Admin/src/pages/CreateProject/CreateProjectPage.jsx` |
| Stiller | `admin_pan/Admin/src/pages/CreateProject/create-project.css` |
| Route | `/create-project` (`routes/index.jsx`) |

Bu bölüm, [`plan.md`](./plan.md) içindeki **L5 / teslim** ve **L1 ingest** ile uyumlu UI sözleşmesidir.

### Uygulama durumu

| Adım | UI | Motor |
|------|-----|--------|
| 1 Kaynak | ✅ `CreateProjectPage` resource | ✅ `pdf_base64`, `url` |
| 2 Yapılandırma | ✅ toolbar + prompt + TTS/görsel/MP4 seçenekleri | ✅ `POST /generate` |
| 3 İşlem | ✅ stepper + SSE (poll yedek) | ✅ `events`, `events/stream`, `stage` |
| 4 Outline | ✅ accordion kartlar | ✅ `GET /deck` |
| 5 Düzenleyici | ✅ canvas + tema/ses/paylaş + Kaydet + Sunum | ✅ `PUT /deck`, `embed/html`, görsel API, export |

**İleri:** Remix, S3, PPTX’e gömülü ses; [`plan.md` § HTML slayt fabrikası](./plan.md#html-slide-factory).

**QR ile izleme:** Firebase Hosting + slayt analytics — [`plan.md` § Firebase Hosting & QR](./plan.md#firebase-hosting-qr), aşağı [Phase G](#phase-g-firebase-qr).

---

## Layer completion (motor)

| Layer | Scope | Status |
|-------|--------|--------|
| **L1** | Ingest, unified context, PDF/URL/`pdf_base64`, intake UI fields | Done |
| **L2** | LLM chat, **vision**, **image gen** (OpenRouter chat+image veya DALL·E), **stock** (Unsplash), router (`text` + `vision` + `resolve_image_model`), theme + PPTX/HTML | Done |
| **L3** | TTS (`openrouter` / OpenAI speech, `elevenlabs`), **`manifest_from_deck_notes`**, `use_tts`, `audio-manifest` API | Done |
| **OpenRouter** | Tek `OPENROUTER_API_KEY` → LLM, vision, image, TTS (`openrouter_client.py`) | Done |
| **L4** | Per-slide TTS files, FFmpeg MP4 mux, `export/mp4` | Done (MVP) |
| **L5** | Full slide editor, presenter, theme/voice/share panels, `PUT` deck, embed HTML | Done (`admin_pan` `/create-project` editor + API) |
| **L5+** | Interactive slide player: ticker, animations, accordion, transitions, per-element audio sync, progress, quiz, mobile | Planned — [`plan.md` § Slayt deneyimi](./plan.md#slayt-player-l5) |
| **QR / izleme** | Firebase Hosting’de statik player, `trackSlide()`, QR URL parametreleri (`kullanici`, `firma`) | Planned — [`plan.md` § Firebase Hosting & QR](./plan.md#firebase-hosting-qr) |

---

## Phase A — Foundation

- [x] Submodule `admin_pan`, `.env.example`, repo layout (`training_app/`).
- [x] Deck JSON v1, agent events, OpenAPI via FastAPI (`/presentations/*`).

## Phase B — Ingest and models

- [x] PDF / URL / unified context; structural validation.
- [x] Model router (tier → chat model; **vision** modality → `VISION_MODEL_OPENAI`).
- [x] **VLM path:** `agents/vision.py` (OpenAI multimodal chat).
- [x] **Image gen:** `agents/image_synthetic.py` (OpenRouter `modalities: image` veya DALL·E).
- [x] **OpenRouter:** `openrouter_client.py`, tier + `OPENROUTER_IMAGE_MODEL` / `OPENROUTER_TTS_MODEL`.
- [x] **Stock:** `agents/image_stock.py` (`UNSPLASH_ACCESS_KEY`, optional).

## Phase C — Orchestrator

- [x] State machine + SSE-friendly events; slide-length policy in LLM prompt + intake block.
- [x] Template-backed generation; theme pass on Deck JSON.

## Phase D — Export and hardening

- [x] PPTX/HTML export; async jobs (`BackgroundTasks`).
- [ ] Extended security review, rate limits, integration test matrix in CI.

## Phase E — Integration

- [ ] Contract with `admin_pan` for auth and quotas; usage callbacks as needed.

## Phase F — Slayt player & etkileşim (L5+)

Ayrıntılar: [`plan.md` — Slayt deneyimi](./plan.md#slayt-player-l5).

- [ ] Kayan yazı (ticker) ve erişilebilirlik (`prefers-reduced-motion`).
- [ ] Fade-in / sıralı görünüm animasyonları (blok bazlı).
- [ ] Accordion / tıklanınca açılan metin kutuları.
- [ ] Slayt geçiş efektleri (embed + presenter).
- [ ] Anlatım: element zaman çizelgesi + senkron vurgulama (manifest / timeline genişletmesi).
- [ ] İlerleme: `localStorage` veya oturumlu `progress` API.
- [ ] Quiz slayt tipi ve doğrulama UI.
- [ ] Mobil uyum (dokunma, düzen, tipografi).
- [ ] **HTML slayt fabrikası:** `layout_id` kataloğu (Desk/RCA), `html_export` genişletmesi — [`plan.md` § HTML slayt fabrikası](./plan.md#html-slide-factory).

<a id="phase-g-firebase-qr"></a>

## Phase G — Firebase Hosting & QR ile sunum izleme

Ayrıntılar: [`plan.md` — Firebase Hosting & QR](./plan.md#firebase-hosting-qr).

**Amaç:** Eğitim sunumlarını **QR kod** ile dağıtmak; izleyici kimliği ve kurum bilgisini URL’den almak; **slayt bazında** ne kadar izlendiğini kaydetmek.

### Kurulum (tek seferlik)

- [ ] [Firebase Console](https://console.firebase.google.com) → proje oluştur (Hosting + Analytics açık).
- [ ] [Node.js](https://nodejs.org) kurulu.
- [ ] `npm install -g firebase-tools`
- [ ] `firebase login`

### Hosting projesi

- [ ] Statik player klasörü: export edilen HTML veya `hosting/public/index.html` (motor `embed/html` çıktısı veya özelleştirilmiş viewer).
- [ ] `firebase init hosting` (public klasör, SPA rewrite gerekirse).
- [ ] `firebase deploy` → canlı URL (`https://<proje>.web.app/...`).

### Player & izleme kodu

- [ ] Firebase **config** snippet’i player HTML’e (`firebaseConfig` + SDK).
- [ ] Her slayt geçişinde **`trackSlide(slideIndex, meta)`** — Analytics event veya Firestore/RTDB dokümanı.
- [ ] URL parametreleri: `?kullanici=<ad>&firma=<xyz>&deck=<job_id>` (ve isteğe bağlı `lang`, `slide`).
- [ ] QR üretimi: `admin_pan` **Paylaş** panelinde tam URL + QR görseli (mevcut embed URL’ye parametre ekleme).

### Motor / API (isteğe bağlı, Phase G+)

- [ ] `GET /presentations/{id}/export/hosting-bundle` — tek zip: `index.html` + inline deck JSON veya manifest.
- [ ] Sunucu tarafı özet API (`GET /presentations/{id}/analytics`) — Firebase’den okuma veya motor DB; MVP’de yalnızca Firebase yeterli.

### Doğrulama

- [ ] QR tara → player açılır, `kullanici` / `firma` konsol veya Analytics’te görünür.
- [ ] Slayt ilerlet → her slayt için en az bir `slide_view` (veya eşdeğer) kaydı.
- [ ] Mobil tarayıcıda tam ekran / dokunma ile geçiş.

---

## Layer 3 — API quick reference

- **Manifest (always after successful run):** `GET /presentations/{job_id}/audio-manifest`
- **Job summary:** `GET /presentations/{job_id}` → `has_audio_manifest`
- **Optional TTS probe:** `POST /presentations/generate` with `"use_tts": true`, `"tts_provider": "openai"` or `"elevenlabs"`, optional `"tts_voice_id"`.

Later phases (external web search, richer templates, collaboration) stay **out of MVP** unless promoted in `SPEC.md`.
