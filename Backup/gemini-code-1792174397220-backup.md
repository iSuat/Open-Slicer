# OpenSlicer Studio (123D Make / Slicer for Fusion 360 Clone) — Proje Bağlamı ve Teknik Özellikleri

## Proje Amacı
Eski Autodesk 123D Make / Slicer for Fusion 360 programını modernize ederek, Three.js tabanlı, tarayıcıda çalışan, sıfır maliyetli ve kurulum gerektirmeyen tek dosyalık bir web uygulaması olarak yeniden inşa etmek ("Clean Room" / Bakarak Klonlama yöntemi).

---

## Kullanılan Teknolojiler ve Altyapı
- **Frontend:** HTML5, CSS3 (Dark & Light Mode CSS Değişkenleri), Vanilla JavaScript (Tek dosya mimarisi: `gemini-code-1792173559314.html`)
- **Dil:** Tamamen İngilizce (Orijinal Slicer for Fusion 360 terminolojisiyle birebir uyumlu)
- **3D Motoru & Kontroller:** Three.js (r128), OrbitControls, TransformControls, Çift Kamera (Perspective & Orthographic) ve İkinci WebGL Sahnesi ile 26 Bölgeli (6 Yüzey, 12 Kenar, 8 Köşe) Autodesk ViewCube
- **Dosya Yükleyiciler & Çıktı:** STLLoader, OBJLoader, JSZip (`.3mf` okuma ve çoklu plaka `.ZIP` indirme), 1:1 Milimetre `DXF`, `EPS` ve `SVG` vektör üreticileri

---

## Üst Bar (Header)
- **Sol:** Logo (`SLICER - OPEN STUDIO`) ve `Undo / Redo` butonları.
- **Sağ:** `# Grid` (3D ızgara aç/kapat), `☀️ Light Mode / 🌙 Dark Mode` tema geçişi ve `? Help` kısayol bilgisi.

---

## Sol Panel Mimarisi (Orijinal Slicer Düzeni & Sabit Tema Uyumlu Scrollbar)

### 1. Model
- **Göz İkonu (`👁`):** Varsayılan olarak sahnede yalnızca dilimlenmiş katmanlar görünür; göze tıklandığında orijinal katı/yarı-saydam ham 3D model açılır/kapanır.
- **Model Seçimi & Yükleme:** Hazır modeller veya `.STL`, `.OBJ`, `.3MF` yükleme + `Reset (↻)` butonu.

### 2. Manufacturing Settings
- **Hazır & Kaydedilebilir Plaka Profilleri:** `1000x1000x3mm` vb. hazır profiller ve `✎` butonu ile mevcut ölçüyü `localStorage`'a kalıcı kaydetme.
- **Çark (`⚙`) Çekmecesi:** `Sheet Length`, `Sheet Width`, `Thickness`, `Skip Layers`, `Margin`, `Slot Offset` ve `Tool Diameter` ayarları yalnızca çarka tıklandığında açılır.

### 3. Object Size
- **Units:** `mm`, `cm`, `in`
- **Boyutlar:** `Height (Z)`, `Width (X)`, `Length (Y)` ve dış ok butonları (`▲` / `▼`).
- **Ölçekleme:** `Original Size` butonu ve `Uniform Scale` onay kutusu.

### 4. Construction Technique & Dowels
- **Stacked Slices / Interlocked Slices** seçimi.
- **Dowels (Entegre Alt Panel):**
  - `Dowels` aktif edildiğinde delikler katmanlarda ve kesim planında kalıcı olarak açılır.
  - **Otomatik Gizlenen Çift Mavi Düzlem (`⟱`):** Üst ve alt mavi çalışma düzlemleri yalnızca Dowel düzenleme modundayken görünür; başka bir sekmeye (`Slice Direction`, `Modify Form`, `Assembly Steps`, `Get Plans`) veya sahne aracına geçildiğinde mavi düzlemler otomatik gizlenir, delikler kalır.
  - **Çoklu Blok & Kör Delik Kuralı:** Arada boşluk/girinti olsa bile pimin tam sığdığı tüm katman blokları delinir (örn. 1-6 ve 11-13); yalnızca en son (en üst) geçerli katman kapak olarak bırakılır.
  - **Akıllı `Automatic` Yerleştirme:** Tüm katmanların kesişim haritasını tarayıp en fazla katmanı bağlayan en uygun 2 pim noktasını bulur.
  - `Delete` / `Backspace` tuşu ile seçili pimi silme.

### 5. Alt Açılır Araç Sekmeleri (Tıklandığında Açılan Modeller)
- **Slice Direction (`⫯`):** `Tilt X (°)` ve `Rotate Y (°)` açıları + sıfırlama butonları.
- **Modify Form (`🐚`):** Parametrik 2D `Hollow` (İç Boşaltma) ve `Wall Thickness`.
- **Assembly Steps (`🧱`):** Adım sürgüsü, `◀ Prev` / `▶ Play` / `Next ▶` animasyonlu montaj oynatıcısı (aktif üst katmanı vurgu rengiyle boyar).
- **Get Plans (`📄`):** `Nested` (Hole-in-Hole akıllı cep yerleşimi) / `Grid`, **File Type (`DXF`, `EPS`, `SVG`)**, **`Download All (.ZIP)`** ve **`Download Combined File`**.

---

## Orta Panel: 3D Sahne, Autodesk ViewCube ve Dikey Kamera Çubuğu
- **Zemin Gölgesi (Contact Shadow):** Modelin taban izine göre ölçeklenen yumuşak dairesel zemin gölgesi.
- **Üst Araç Çubuğu:** `Select` | `Move (T)` | `Rotate (R)` | `Scale (S)` | `Lay Flat (F)` | `Drop to Bed`
- **26 Bölgeli 3D ViewCube:** Sağ üstte 6 ana yüzey (`TOP`, `BOTTOM`, `FRONT`, `BACK`, `LEFT`, `RIGHT`), 12 pahlı kenar ve 8 izometrik köşesi ayrı ayrı parlayan ve tıklanabilen 3D küp + `🏠` Home butonu.
- **Dikey 5'li Kamera Navigasyon Çubuğu (SVG/PNG Değiştirilebilir Slotlu):**
  1. `Orbit` (Sol tık döndür)
  2. `Pan` (Sol tık kaydır)
  3. `Zoom` (Sol tık yakınlaş/uzaklaş)
  4. `Fit to View` (Modele sığdır)
  5. `Ortho / Perspective` (Paralel / Perspektif izdüşüm geçişi)

---

## Sağ Panel: Gizlenebilir `Cut Layout` & `Model Issues`
- **Gizle / Göster (`⇥` / `⇤`):** Sağ üstteki butonla sağ panel tamamen kapatılıp 3D sahne genişletilebilir.
- **Sekme 1 — `Cut Layout`:**
  - Üstte büyük `Sheets` ve `Parts` sayaçları + 1/2 sütun görünüm geçişi (`⊞`).
  - Her plaka kartının üzerinde o plakayı tek başına seçili formatta (`⬇ DXF` / `⬇ EPS` / `⬇ SVG`) indirme butonu.
  - **2D ↔ 3D Cross-Highlighting:** Plaka üzerindeki herhangi bir parçaya tıklandığında 3D sahnede ilgili katman parlak renkle vurgulanır.
- **Sekme 2 — `Model Issues`:**
  - Plakaya sığmayan parçaları (`Part Exceeds Sheet Size`), tek katmanda kopuk adaları (`Multiple Separate Islands`), çok küçük parçaları (`Fragile Small Part`) ve pimsiz kalan katmanları (`Unpinned Layer`) otomatik tespit eder; tıklanınca 3D sahnede o katmanı vurgular.