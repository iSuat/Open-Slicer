# OpenSlicer Studio — AI-Assisted Development Instructions (`instructions.md`)

Bu belge, **OpenSlicer Studio** projesini gelecekteki oturumlarda yapay zeka (AI) asistanlarıyla geliştirirken bağlam kaybını önlemek, kredi/token tüketimini en aza indirmek ve mevcut mimari kuralları korumak amacıyla hazırlanmıştır.

`./Backup` klasörü kod yedekleri içindir. bu klasörü okumana gerek yok. 

---

## 1. Proje Dosya Yapısı ve Yedekleme Kuralı
* **Ana Uygulama Dosyası:** `d:\Projeler\Open Slicer\SlicerStudio.html`
  * Proje **Single-File Application** (Tek Dosya HTML + CSS + JS) mimarisindedir. Harici bundler (Webpack/Vite) kullanılmaz; doğrudan tarayıcıda çalışır.
  * Bağımlılıklar CDN üzerinden yüklenir:
    * `Three.js r128` (`three.min.js`, `OrbitControls.js`, `TransformControls.js`, `STLLoader.js`, `OBJLoader.js`)
    * `JSZip 3.10.1` (`.3mf` okuma ve `.zip` toplu çıktı üretimi için)
    * `ClipperLib 6.4.2` (`clipper.js` — 2B Boolean birleşim, fark ve paralel ofset işlemleri için)
* **Yedekleme Standardı:**
  * Ana dosyada kapsamlı bir değişiklik yapmadan önce mevcut çalışan sürümü `SlicerStudio-backup-vX.html` (şu an en son `Backup\SlicerStudio-backup-v11.html` mevcuttur; bir sonraki yedek `Backup\SlicerStudio-backup-v12.html` olmalıdır) olarak `./Backup` klasörüne kopyala. Eski `gemini-code-1792174397220-backup.md` dosyası da `./Backup` klasörüne arşivlenmiştir.
* **Sözdizimi Doğrulaması (Syntax Check):**
  * Her kod düzenlemesinden sonra tarayıcıda test etmeden önce mutlaka Node.js ile hızlı sözdizimi kontrolü çalıştır:
    ```powershell
    node -e "const fs = require('fs'); const html = fs.readFileSync('SlicerStudio.html', 'utf8'); const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]; const mainJs = scripts[scripts.length - 1][1]; new Function(mainJs); console.log('JS Syntax OK! Lines:', html.split('\n').length);"
    ```

---

## 2. Kod Haritası (Section Map — `SlicerStudio.html`)
Dosya içinde arama yaparken tüm dosyayı okumak yerine aşağıdaki bölüm başlıklarını (`grep_search` ile) hedefle:

1. **CSS Stilleri (`Lines 15–620`):**
   * Dark / Light tema değişkenleri (`:root`, `body.light-theme`), Sol Akordeon Menü (`#sidebar`), Orta 3B Sahne (`#viewport3d`), Sağ Panel (`#viewport2d`), Tam Ekran Sheet Lightbox (`#sheetLightbox`) ve Sağ-Alt Assembly Step HUD (`#assemblyStepHud`).
2. **HTML İskeleti (`Lines 625–1120`):**
   * Sol Menü Kutuları:
     * `Box 1`: Import / Model & Preset seçimi (`#presetSelect`, `#fileInput`)
     * `Box 2`: Manufacturing Settings (`#unitSelect`, `#sheetW`, `#sheetH`, `#matThick`, `#skipCount`, `#sheetMargin`, `#slotOffset`, `#chkToolDia`, `#toolDia`)
     * `Box 3`: Construction Technique (`#modeSelect` [`stacked` / `waffle`], `#waffleBox` [`#waffleX`, `#waffleY`, `#waffleNotchFactor`, `#waffleReliefType`])
     * `Box 4`: Modify Form / Hollow (`#chkHollow`, `#hollowWall` — *Waffle modunda gizlenir*)
     * `Box 5`: Dowels / Pimler (`#chkDowels`, `#dowelShape`, `#dowelDia`, `#btnAutoDowel`, Dowel Cut Summary — *Waffle modunda gizlenir*)
     * `Box 6`: Slice Direction (`#sliceAngX`, `#sliceAngY`, `#btnToggleSliceGimbal`)
     * `Box 7`: Assembly Steps & Preview (`#assemblySlider`, `#btnStepPrev`, `#btnStepNext`, `#btnStepPlay`, `#chkShowExtrude`)
     * `Box 8`: Export Plans (`#layoutSelect`, `#exportFormatSelect`, `#chkSvgCut`, `#chkSvgGuide`, `#chkSvgLabel`, `#btnExportZip`, `#btnExportSingleMaster`)
3. **JS Bölüm 1–6 (`Lines 1125–2620`): Three.js Sahne, Gimbal, Transform & OrcaSlicer Lay-on-Face:**
   * `rebuildCustomOrcaSliceGimbal()`: Hem `Slice Direction` (`gimbalMode = 'slice'`) hem de üst menü `Rotate (R)` (`gimbalMode = 'modelRotate'`) için kullanılan sabit beyaz çentikli iletki gimbalı.
   * **Önemli Kural:** Gimbal çemberinin çentikleri sürükleme sırasında **sabit** durur; sadece renkli ok tutamacı (`handleGroup`) ve yarıçap çizgisi (`spokeLine`) döner. Fare çemberin içindeyken (`dist <= radius * 1.15`) **5° snap** yapar, çemberin dışındayken **serbest (`0.1°`)** döner.
   * `buildLayFlatCandidatePlates()` & `layMeshFlatOnNormal()`: 3B Convex Hull (QuickHull) tabanlı OrcaSlicer yüzeye oturtma motoru.
4. **JS Bölüm 7–8 (`Lines 2625–3760`): ClipperLib 2B Boolean, Dilimleme Motoru (`runSlicer`) & Waffle Motoru:**
   * `CLIPPER_SCALE = 1000` (`0.001 mm` tam sayı hassasiyeti).
   * `classifySliceLoopsWithClipper()`: Dış konturları `CCW` (`wantCCW = true`), iç delikleri `CW` (`wantCCW = false`) olarak ayırır.
   * `computeTrueHollowHoles()`: `ClipperLib.ClipperOffset` ile gerçek paralel iç ofset hesaplar.
   * `subtractWaffleSlotsWithClipper()`: Geçmeli ızgara (Waffle) yuvalarını, giriş pahını ve T-Bone/Dog-Bone köşe boşaltmalarını `ClipperLib.ClipType.ctDifference` ile keser.
   * `runSlicer()`: Ana dilimleme fonksiyonu. Dilimleme düzlemi dönüşümünü (`rotMat` / `invRotMat`) her zaman modelin dünya merkezine (`modelWorldCenter`) göre pivotlar.
5. **JS Bölüm 9–12 (`Lines 3765–5060`): Kavela Sistemi, Model Issues, 2B Nesting, DXF/SVG/EPS Export, Sheet Lightbox & Assembly Steps:**
   * `analyzeModelIssues()`: Plaka boyutunu aşan parçaları, ayrık adacıkları ve Waffle modunda fiziksel olarak birbirine geçemeyen (çarpışan) parçaları raporlar.
   * `buildSVGString()`, `buildDXFString()`, `buildEPSString()`: 2B üretim çıktılarını oluşturur.
   * `openSheetLightbox()`: Cut Layout'ta bir plakaya çift tıklayınca 3B sahne üzerinde tam ekran zoom/pan yapılabilen Lightbox açar.
   * `highlightAssemblyStep()` & `updateAssemblyStepAnimationFrame()`: Montaj adımları animasyonu ve sağ-alt HUD kontrolü.

---

## 3. Koordinat Sistemleri ve Matematiksel Kurallar
1. **3B Sahne Koordinat Sistemi (Z-Up):**
   * `X`: Sağ/Sol, `Y`: İleri/Geri (Derinlik), `Z`: Yukarı (Yükseklik). Baskı tablası `Z = 0` düzlemindedir.
2. **Dilimleme Eksenleri ve 2B Projeksiyon (`sliceMeshAtZ(geom, val, axis)`):**
   * **`Z` Ekseni (Stacked Slices):** Kesit düzlemi $Z = z_0$. 2B koordinatlar: $(x = X,\; y = Y)$.
   * **`X` Ekseni (Waffle X Ribs):** Kesit düzlemi $X = x_0$. 2B koordinatlar: $(x = Y,\; y = Z)$. 3B sahneye geri yerleştirilirken `mX` matrisi kullanılır.
   * **`Y` Ekseni (Waffle Y Ribs):** Kesit düzlemi $Y = y_0$. 2B koordinatlar: $(x = X,\; y = Z)$. 3B sahneye geri yerleştirilirken `mY` matrisi kullanılır.
3. **Waffle Fiziksel Montaj Yönü:**
   * **`Y` dilimleri (`Y-1..Y-m`)** masaya ilk konulan taban ızgarasıdır; slotları **üstten aşağıya (`dir: 'top'`, `[zMid, zTop + 2]`)** açılır.
   * **`X` dilimleri (`X-1..X-n`)** üstten (`+Z`) aşağıya doğru `Y` dilimlerinin üzerine indirilir; slotları **alttan yukarıya (`dir: 'bottom'`, `[zBot - 2, zMid]`)** açılır.

---

## 4. Tamamlanan 4. Aşama Özeti ve Sıradaki Geliştirme Planı (`P2+` -> `P1` & `P3`)

### ✅ Tamamlanan Son Geliştirmeler (v11):
1. **AutoCAD R12 (`AC1009`) DXF & Dosya Adlandırma (`getSanitizedExportBaseName`):** `LWPOLYLINE` yerine `LTYPE` tablosu ve saf R12 `POLYLINE` + `VERTEX` + `SEQEND` yapısına geçildi; `_SS` / `_IS` üretim tekniği kodu eklendi.
2. **`Dog Bone`, `T-Bone` ve `Notch Factor` (Gerçek 2B Vektör Köşe Chamfer):**
   * **Dog Bone:** Daire merkezleri slotun içine doğru $\left(x_{\text{min}} + \frac{R}{\sqrt{2}},\; z_{\text{mid}} \pm \frac{R}{\sqrt{2}}\right)$ ve $\left(x_{\text{max}} - \frac{R}{\sqrt{2}},\; z_{\text{mid}} \pm \frac{R}{\sqrt{2}}\right)$ noktalarına yerleştirildi (3 noktadan teğet/kesişim).
   * **T-Bone:** Daire merkezleri dikey duvar üzerinde $\left(x_{\text{min}},\; z_{\text{mid}} \pm R\right)$ ve $\left(x_{\text{max}},\; z_{\text{mid}} \pm R\right)$ noktalarına yerleştirildi.
   * **Notch Factor (`applyVectorSlotMouthChamfers`):** Pah işlemi kesen dikdörtgene değil, kesilen parçanın **nihai 2B vektör poligonu (`outerLoops`)** üzerindeki slot ağzı köşelerine (`IN` ve `OUT` köşeleri) doğrudan vektör chamfer olarak uygulanır; köşe noktasından dikey slot duvarı boyunca ve parçanın kendi dış konturu boyunca `chamfer` kadar yürünerek basamaksız düz pah çizgisi oluşturulur.
3. **Ana Ekranda Anında Çarpışma Vurgusu & `Assembly Steps`:**
   * `syncDefaultCollidingSliceIds()` ile model dilimlendiği anda (`Assembly Steps` beklenmeden) fiziksel olarak birbirine geçemeyen parçalar ana 3B ekranda **parlak macenta (`0xd946ef`)** rengiyle vurgulanır.
   * `#assemblySlider` (`step="0.02"`) kesintisiz çalışır; ortada bırakıldığında parça havada asılı kalır. `Prev`/`Next` butonlarında ise ayrılan parça `hoverSeparatedIdx` ile bir sonraki adıma kadar yukarıda bekler.
4. **Linear Slide Komşu Parça Sınırı (`getWaffleRibOffsetBounds` & `clampWaffleRibOffset`):**
   * `X` ve `Y` dilimleri kaydırılırken komşu dilimlere en fazla `matThick` mesafesine kadar yaklaşabilir, komşunun üstünden geçemez.
5. **Lightbox İnce Çizgi, Orantılı Single-Line Vektör Font (`getSheetLabelFontSizes`) & Akıllı Etiket Konumu (`findSmartSliceLabelPosition`):**
   * Parça etiketleri (`X-4`) yerleştirilirken slot etiketlerine (`Y-1..Y-5`) olan mesafe de hesaba katılır ve üst/alt kubbe seviyeleri taranarak çakışma önlenir.
   * SVG, DXF ve EPS çıktılarında yazı boyutları plaka boyutuna orantılı (`min(sheetW, sheetH) / 38`) ve tek çizgi (`SINGLE_LINE_FONT`) olarak üretilir.
6. **Boş Sahne Açılışı & Yeni Presetler:**
   * Hazır modeller kaldırıldı; uygulama boş tabla ile açılır. `300x300x3mm`, `86x54x0.4mm` ve `210x297x0.1mm` (`min="0.05"` mm kalınlık desteği) presetleri eklendi.

---

### 🎯 Sıradaki Aşama: `P2+` (Yeni Üretim / Dilimleme Teknikleri)
Kullanıcı kararı doğrultusunda `P1` (`.3mf` proje yedekleme) ve `P3` (performans, gelişmiş nesting, özel test modeli, gizmolar) **en son aşamalarda** ele alınacaktır. Sıradaki odak noktası **`P2+` Yeni Dilimleme Teknikleri**dir:
1. **Radial Slices (`RS` - Işınsal / Dairesel Dilimleme):**
   * Modelin merkez ekseni (veya kullanıcı tarafından kaydırılabilir merkez noktası) etrafında açılı ışınsal kanatlar (`R-1..R-n`) ve yatay dairesel halkalar (`Z-1..Z-m`) ile dilimlenmesi.
   * Mevcut `subtractWaffleSlotsWithClipper`, `Dog Bone / T-Bone`, `applyVectorSlotMouthChamfers` ve `slotLabels` altyapısının Radial Slices için de ortak kullanılması.
2. **Diğer `P2+` Modları (İsteğe Bağlı Sırayla):**
   * **Curve Slices (`CS`)** ve **Folded Panels / Pepakura (`FP`)**.

---

## 5. İletişim ve Çalışma Prensipleri
* Kullanıcıyla her zaman **Türkçe**, net ve özlü iletişim kur.
* Kullanıcı *"kod yazma, önce konuşalım"* dediğinde hiçbir dosya düzenleme aracı çağırma; önce tasarımı ve matematiksel yaklaşımı netleştir, kullanıcı *"başla"* dediğinde tek bir toplu geçişte (minimum kredi/token harcayarak) uygula.
