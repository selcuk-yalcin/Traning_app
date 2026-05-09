# Traning_app — Kapsamlı TODO

Çok modelli, ajanik eğitim sunumu motoru. Admin UI [admin_pan](https://github.com/selcuk-yalcin/admin_pan) alt-reposunda; bu liste yalnızca **motor + entegrasyon + export** içindir.

---

## 0 — Repo ve alt-modül

- [ ] GitHub’da `Traning_app` (veya seçilen isim) repo oluştur; yerel `origin` bağla.
- [ ] `git submodule add https://github.com/selcuk-yalcin/admin_pan.git admin_pan` (kök dizinde; `integrations/` altında değil)
- [ ] `.gitignore` (Python, venv, `.env`, IDE, geçici upload klasörleri).
- [ ] Geliştirme için `.env.example` (model anahtarları yok; sadece değişken isimleri).

---

## 1 — Sözleşmeler (şema)

- [ ] **Deck JSON v1** şeması: sunum meta, slayt dizisi, her slayt için bloklar (başlık, gövde, tablo, görü placeholder, grafik verisi).
- [ ] **Ajan olay şeması** (SSE/WebSocket): `stage`, `detail`, `progress`, `slide_index`, `error_code`.
- [ ] **İstek/yanıt API** OpenAPI veya eşdeğeri: `POST /presentations/generate`, `GET /presentations/{id}/events`, `GET /presentations/{id}/deck`.
- [ ] Model katmanı eşlemesi: `tier` → `{provider, model_id, max_tokens}` yapılandırması.

---

## 2 — Ingest (çok modallık)

- [ ] Metin prompt doğrulama ve dil tespiti (veya “Auto”).
- [ ] PDF: metin çıkarımı (pypdf/pdfminer); gerekirse sayfa render + OCR pipeline.
- [ ] Görü: EXIF/strip; boyut sınırı; thumbnail üretimi.
- [ ] Görü “okuma”: VLM ile özet, nesne/sahne etiketleri, **metin için güvenli alan** (basit bounding box veya grid önerisi).
- [ ] Birleşik bağlam belgesi: tüm kaynaklardan tek “context document” (chunk + kaynak atfı).

---

## 3 — Orchestrator (ajan orkestrasyonu)

- [ ] Durum makinesi: `idle` → `planning` → `research` → `generating` → `layout` → `done` / `failed`.
- [ ] “Thinking” alt görevleri: konuyu parçalama, anlatı yapısı, bölüm başlıkları (UI’de timeline ile uyumlu).
- [ ] Slide sayısı politikasını uygula: “Let AI decide” / kısa / orta / uzun.
- [ ] Research aşaması: isteğe bağlı harici arama yoksa yalnızca ingest bağlamı + LLM; varsa tooling ekle (sonraki faz).
- [ ] Hata işleme: kısmi deck kaydı, yeniden deneme, kullanıcıya anlamlı `error_code`.

---

## 4 — Model router (multi-model)

- [ ] Tek arayüz: `complete_text`, `complete_vision` (metin + görü URL veya base64).
- [ ] Sağlayıcı adaptörleri: en az bir LLM + bir VLM (ör. OpenAI uyumlu API ve ikinci sağlayıcı).
- [ ] Tier: Standard / Pro / Ultra → model ve parametre seçimi.
- [ ] Oran sınırlama ve maliyet tahmini (admin_pan kotası ile hizalama).

---

## 5 — İçerik ve slayt üretimi

- [ ] Outline üretimi (numaralı bölümler; referans UI’daki outline ekranı).
- [ ] Slayt başına: başlık, maddeler, tablo, karşılaştırma layout’u için yapılandırılmış çıktı.
- [ ] Eğitim tonu: öğrenme hedefleri, kısa özet, kontrol sorusu (isteğe bağlı slayt türü).
- [ ] “Yeni slayt prompt ile”: tek slayt için dar bağlamla yeniden üretim endpoint’i.

---

## 6 — Layout ve tema

- [ ] Tema token’ları: renk, font ailesi, spacing (JSON).
- [ ] Basit layout motoru: şablon ID → blok bölgeleri; metin taşması için kısaltma kuralları.
- [ ] Şablon kataloğu (Education ağırlıklı) — meta + önizleme görseli yolu.

---

## 7 — Export PPTX

- [ ] Deck JSON → **python-pptx** (veya seçilen kütüphane) ile `.pptx` üretimi.
- [ ] Başlık gövde, tablo, madde işaretleri; görü yerleştirme ve en-boy oranı.
- [ ] İndirme URL’si veya senkron stream; büyük dosyalar için async job.

---

## 8 — Altyapı ve gözlemlenebilirlik

- [ ] Worker kuyruğu (uzun üretim işleri).
- [ ] Yapılandırılmış loglama (run_id, kullanıcı id’si admin_pan’dan).
- [ ] Temel metrikler: süre, token, görü çağrısı sayısı.

---

## 9 — admin_pan entegrasyonu

- [ ] Kimlik doğrulama: paylaşılan secret veya JWT doğrulama sözleşmesi (admin_pan ile netleştir).
- [ ] Proje/kullanıcı başına kota ve API anahtarı yönetiminin admin_pan’da kalması.
- [ ] Bu servisin admin_pan’a **minimal** geri çağrıları: kullanım raporu, hata sayısı (isteğe bağlı).

---

## 10 — Kalite ve güvenlik

- [ ] Prompt injection ve zararlı dosya taraması (tip, boyut, içerik sanity).
- [ ] PII maskeleme gerekiyorsa ingest aşamasında kural seti.
- [ ] Birim testleri: şema validasyonu, router mock, PPTX smoke test.
- [ ] Entegrasyon testi: örnek PDF + görü ile uçtan uca kısa deck.

---

## 11 — İsteğe bağlı sonraki fazlar

- [ ] Harici “research” araçları (web arama) ile kaynak linkleri slayta ekleme.
- [ ] Sunum “Present” modu için statik HTML export.
- [ ] İşbirliği (aynı deck üzerinde): operasyonel olarak admin_pan + ayrı realtime katman.

---

*Dosya adı repoyla aynı kökte: `TODO.md` — tamamlanan maddeleri işaretleyerek ilerleyin.*
