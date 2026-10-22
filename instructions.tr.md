# OpenSlicer Studio — AI-Assisted Development Instructions (`instructions.tr.md`)

[English Version](instructions.md) | **Türkçe Sürüm**

Bu belge, **OpenSlicer Studio** projesini gelecekteki oturumlarda yapay zeka (AI) asistanlarıyla geliştirirken bağlam kaybını önlemek, kredi/token tüketimini en aza indirmek ve mevcut mimari kuralları korumak amacıyla hazırlanmıştır.

`./Backup` klasörü kod yedekleri içindir; bu klasörü okumana gerek yoktur.

---

## 1. Proje Dosya Yapısı ve Kurallar
* **Ana Uygulama Dosyası:** [index.html](file:///d:/Projeler/Open%20Slicer/index.html) (`6,843` satır)
  * Proje **Single-File Application** (Tek Dosya HTML + CSS + JS) mimarisindedir. Harici derleyici/bundler (Webpack, Vite) kullanılmaz; doğrudan modern tarayıcılarda çalışır ve GitHub Pages ile tam uyumludur.
  * Bağımlılıklar CDN üzerinden yüklenir:
    * `Three.js r128` (`three.min.js`, `OrbitControls.js`, `TransformControls.js`, `STLLoader.js`, `OBJLoader.js`)
    * `JSZip 3.10.1` (`.3mf` okuma ve `.zip` toplu çıktı üretimi için)
    * `ClipperLib 6.4.2` (`clipper.js` — 2B Boolean birleşim, fark ve paralel ofset işlemleri için)
* **Lisans:**
  * Proje resmi olarak **GNU General Public License v3.0 (GPLv3)** lisansıyla lisanslanmıştır ([LICENSE](file:///d:/Projeler/Open%20Slicer/LICENSE)).
* **Sürümleme Kuralı (Strict Versioning Rule):**
  * Üst barda gösterilen sürüm `beta 1.2` olarak ayarlanmıştır (`.app-version-badge`).
  * **Önemli:** Sürüm numarası her geliştirme/sohbette otomatik arttırılmaz. Versiyon arttırımı **yalnızca kullanıcı açıkça 'publish ediyoruz / yeni versiyon yayınlayalım' dediğinde** kullanıcının belirlediği numaraya güncellenir.
* **Destek ve Bağış Butonları:**
  * Üst barda `☀️ Light Mode` ile `? Help` arasında `Buy Me a Coffee` butonu yer alır (`https://www.buymeacoffee.com/iSuat`).
  * İleride GitHub Sponsors onayı geldiğinde yanına GitHub Sponsors butonu da eklenecektir.
* **CAD Entegrasyonu & Eklenti Dosyaları:**
  * [OpenSlicerBridge.py](file:///d:/Projeler/Open%20Slicer/Fusion360_Plugin/OpenSlicerBridge/OpenSlicerBridge.py): Autodesk Fusion 360 Add-in scripti (Kullanıcının seçtiği klasöre `[Proje]-[Gövde].stl` adlandırmasıyla otomatik STL export).
  * [OpenSlicerBridge.manifest](file:///d:/Projeler/Open%20Slicer/Fusion360_Plugin/OpenSlicerBridge/OpenSlicerBridge.manifest): Fusion 360 eklenti manifesti.
  * [Install_OpenSlicerBridge.bat](file:///d:/Projeler/Open%20Slicer/Fusion360_Plugin/Install_OpenSlicerBridge.bat): Eklentiyi `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\` dizinine yükleyen 1-tık kurulum betiği.
* **Yedekleme Standardı (Zorunlu Kural):**
  * Ana dosyada (`index.html`) kapsamlı bir değişiklik yapmadan önce mevcut çalışan sürümü `SlicerStudio-backup-vX.html` (veya `index-backup-vX.html`) olarak `./Backup` klasörüne kopyala (Şu an en son [SlicerStudio-backup-v14.html](file:///d:/Projeler/Open%20Slicer/Backup/SlicerStudio-backup-v14.html) mevcuttur; bir sonraki yedek `Backup/SlicerStudio-backup-v15.html` olmalıdır).
  * **Kural:** Kullanıcı aksini söylemediği sürece her kod düzenlemesinden önce mutlaka bu yedekleme adımı uygulanır.
* **Sözdizimi Doğrulaması (Syntax Check):**
  * Her kod düzenlemesinden sonra tarayıcıda test etmeden önce mutlaka Node.js ile hızlı sözdizimi kontrolü çalıştır:
    ```powershell
    node -e "const fs = require('fs'); const html = fs.readFileSync('index.html', 'utf8'); const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]; const mainJs = scripts[scripts.length - 1][1]; new Function(mainJs); console.log('JS Syntax OK! Lines:', html.split('\n').length);"
    ```

---

## 2. Kod Haritası (Section Map — `index.html`)
Dosya içinde arama yaparken tüm dosyayı okumak yerine aşağıdaki bölüm başlıklarını hedefle:

1. **CSS Stilleri (`Lines 6–510`):**
   * Dark / Light tema değişkenleri (`:root`, `body.light-theme`), Sol Akordeon Menü (`#sidebar`), Orta 3B Sahne (`#viewport3d`), Sağ Panel (`#viewport2d`), Tam Ekran Sheet Lightbox (`#sheetLightbox`), Sağ-Alt Assembly Step HUD (`#assemblyStepHud`), `.app-version-badge` ve `.bmc-link`.
2. **HTML İskeleti (`Lines 515–1160`):**
   * Üst Menü (`#topbar`): Marka logosu, `.app-version-badge` (`beta 1.2`), Undo/Redo butonları, Grid Toggle, Light/Dark Toggle, Buy Me a Coffee Linki (`.bmc-link`) ve Help butonu.
   * Sol Menü Kutuları:
     * `Box 1`: Import, Presets & Universal Live Watch (`#presetSelect`, `#fileInput`, `#btnLiveWatchFile`, `#lblLiveWatchStatus`)
     * `Box 2`: Manufacturing Settings (`#unitSelect`, `#sheetW`, `#sheetH`, `#matThick`, `#skipCount`, `#sheetMargin`, `#slotOffset`, `#chkToolDia`, `#toolDia`)
     * `Box 3`: Construction Technique (`#modeSelect` [`stacked` / `waffle` / `radial`], `#waffleBox`, `#radialBox` [`#radialCount`, `#radialRings`, `#radialCoreRadius`, `#radialCenterX`, `#radialCenterY`])
     * `Box 4`: Modify Form / Hollow (`#chkHollow`, `#hollowWall` — *Waffle ve Radial modlarında gizlenir*)
     * `Box 5`: Dowels / Pimler (`#chkDowels`, `#dowelShape`, `#dowelDia`, `#btnAutoDowel` — *Waffle ve Radial modlarında gizlenir*)
     * `Box 6`: Slice Direction (`#sliceAngX`, `#sliceAngY`, `#btnToggleSliceGimbal`)
     * `Box 7`: Assembly Steps & Preview (`#assemblySlider`, `#btnStepPrev`, `#btnStepNext`, `#btnStepPlay`, `#chkShowExtrude`)
     * `Box 8`: Export Plans (`#layoutSelect`, `#exportFormatSelect`, `#chkSvgCut`, `#chkSvgGuide`, `#chkSvgLabel`, `#labelFontSize`, `#btnExportZip`, `#btnExportSingleMaster`)
   * Orta Viewport (`#viewport3d`): Üst Toolbar (`Move/Rotate/Scale/Lay-Flat/Measure`), Kamera/ViewCube Canvas (`#viewCubeCanvas`), Navigasyon Butonları (`#navBtnZoom`, `#navBtnPan`, `#navBtnFit`).
   * Sağ Panel (`#viewport2d`): Model Sorunları (`#issuesCard`) ve Parça Dizilimi (`#cutLayoutContainer`).
3. **JS Bölüm 1–2 (`Lines 1160–1580`): UI Ayarları, Presets & 3B Sahne / Devasa CNC Ölçekleme:**
   * `updateDynamicGridAndFloorDimensions()`: 5m–10m+ CNC projelerinde sahne boyutuna (`sceneSpan`) göre grid hücrelerini (50/100/200/500mm), kamera `near`/`far` sınırlarını (`near = sceneSpan / 2800`, `far = sceneSpan * 14`) ve taban ölçülendirme çizgilerini dinamik ölçekler.
   * Magnifying glass zoom damping (`orbit.zoomSpeed = 0.18`).
4. **JS Bölüm 3–4 (`Lines 1585–2160`): OrcaSlicer Sabit Çentikli İletki Gimbalı & Flicker-Free ViewCube:**
   * `rebuildCustomOrcaSliceGimbal()`: Dış çember sabit durur, fare çember içindeyken 5° snap, dışındayken 0.1° serbest dönüş yapar.
   * `drawViewCube()`: 6 yüz ($[-0.505, 0.505]$), 12 pah kenarı ve 8 köşe ($[0.51, 0.81]$) geometrik olarak ayrıştırılmış ve `polygonOffset` eklenerek Z-fighting / gri titreme tamamen giderilmiştir.
5. **JS Bölüm 5–7 (`Lines 2165–2730`): Dowels, Model Yükleme & OrcaSlicer Lay-on-Face:**
   * `buildLayFlatCandidatePlates()` & `layMeshFlatOnNormal()`: QuickHull 3B dışbükey zarf ile yüzeye oturtma.
   * Göz simgesi (`👁️`): Dilimleri gizleyip orijinal ham modeli opak (`ghostMesh`) gösterir.
6. **JS Bölüm 8 (`Lines 2735–2825`): Evrensel Tarayıcı Dosya İzleme (Universal Live File Watcher):**
   * File System Access API (`window.showOpenFilePicker`) ile seçilen herhangi bir STL/OBJ dosyasının disk üzerindeki değişimini 850ms periyotla izler; dosya değiştiğinde kamera açısını, dönüşümleri ve dilimleme parametrelerini sıfırlamadan modeli anında günceller.
7. **JS Bölüm 9–10 (`Lines 2830–4780`): ClipperLib Boolean, Dilimleme Motoru (`runSlicer`), Waffle & Radial Slices:**
   * `sliceMeshAtZ(geom, val, axis)`: 'z', 'x', 'y' ve polar 'radial' (`{ type: 'radial', cx, cy, cos, sin }`) kesitleri alır.
   * **Radial Slices (`RS`):** Dikey ışınsal kanatlar (`R-1..R-n`) Clipper yarı-düzlem kesimi $[r_{\text{core}}, R_{\text{max}}]$ ile sınırlandırılır; `getAutoRadialCoreRadius` ile merkez fin çakışması trigonometrik olarak otomatik önlenir. Açıdan bağımsız halving joint'ler, T-Bone/Dog-Bone ve Notch Factor giriş pahları uygulanır.
8. **JS Bölüm 11–13 (`Lines 4785–5765`): Dowels, Issues, 2B Nesting, DXF/SVG/EPS Export & Lightbox:**
   * `updateSliceColors()`: Cut Layout üzerinden gizlenen parçanın görünürlüğünü (`grp.visible = !excludedSliceIds.has(id)`) anında geri getiren koşul yapısı.
   * Çok katmanlı AutoCAD R12 (`AC1009`) uyumlu saf DXF (`POLYLINE` + `VERTEX`), orantılı Single-Line CNC Font (`SINGLE_LINE_FONT`).
   * `getSheetLabelFontSizes()` ve parça içi otomatik sığdırma (Auto-Fit Clamping).
9. **JS Bölüm 14–16 (`Lines 5770–6843`): Assembly Steps, 3B Etkileşim & Event Loop:**
   * Kesintisiz slider, macenta çarpışma vurgusu ve Radial dilimler için $(\cos\theta_i, \sin\theta_i, 0)$ doğrultusunda radyal içeri kayma montaj animasyonu.

---

## 3. Koordinat Sistemleri ve Matematiksel Kurallar
1. **3B Sahne Koordinat Sistemi (Z-Up):**
   * `X`: Sağ/Sol, `Y`: İleri/Geri (Derinlik), `Z`: Yukarı (Yükseklik). Baskı tablası `Z = 0` düzlemindedir.
2. **Dilimleme Eksenleri ve 2B Projeksiyon (`sliceMeshAtZ(geom, val, axis)`):**
   * **`Z` Ekseni (Stacked Slices):** Kesit düzlemi $Z = z_0$. 2B koordinatlar: $(x = X,\; y = Y)$.
   * **`X` Ekseni (Waffle X Ribs):** Kesit düzlemi $X = x_0$. 2B koordinatlar: $(x = Y,\; y = Z)$.
   * **`Y` Ekseni (Waffle Y Ribs):** Kesit düzlemi $Y = y_0$. 2B koordinatlar: $(x = X,\; y = Z)$.
   * **`Radial` Ekseni (Radial Fins):** Düşey düzlem normali $(\sin\theta_i, -\cos\theta_i, 0)$. 2B koordinatlar: $(x = \text{radial\_dist},\; y = Z)$.
3. **Geçme ve Yuva Kuralları:**
   * **Waffle:** `Y` dilimleri taban ızgarasıdır (üstten aşağıya yuva); `X` dilimleri üstten indirilir (alttan yukarıya yuva).
   * **Radial Slices:** Dairesel halkalar (`Z-1..Z-m`) dış çevreden merkeze doğru radyal yuvalar alır; radyal kanatlar (`R-1..R-n`) ise göbekten dışa doğru yatay yuvalar alır.

---

## 4. Tamamlanan Son Geliştirmeler (v1.2 Beta)

1. **`P2+` Radial Slices (`RS` - Polar / Işınsal 3B Dilimleme):**
   * Arayüze `Radial Slices` üretim modu eklendi.
   * `R-1..R-n` dikey radyal kanatlar + `Z-1..Z-m` yatay halkalar ile kilitli montaj yapısı oluşturuldu.
   * `getAutoRadialCoreRadius` ile merkez çakışmasını trigonometrik olarak otomatik önleyen dinamik yarıçap motoru eklendi.
2. **Geniş Ölçekli CNC (5m–10m+ / 5000–10000mm+) Sahne & Grid Desteği:**
   * Sahne gridi, kamera near/far sınırları ve zemin ölçü çizgileri dinamik boyutlandırıldı; devasa modellerde Z-fighting önlendi.
3. **ViewCube Titreme (Z-Fighting) Düzeltmesi:**
   * Yüz, kenar ve köşe geometrik sınırları birbirinden tamamen ayrıştırılarak dönüş esnasındaki kırpışmalar giderildi.
4. **Navigasyon Büyüteç Hız Sönümlemesi (Zoom Damping):**
   * Büyüteç aktifken zoom hızı hassas kontrol için `0.18` seviyesine çekildi.
5. **Cut Layout Gizleme/Gösterme Bugfix:**
   * Gizlenen parçaların Cut Layout'tan tekrar açıldığında 3B sahnede anında görünür olması sağlandı.
6. **Evrensel Canlı Dosya İzleyici (Universal Live File Watcher):**
   * Tarayıcı üzerinden doğrudan diskteki STL/OBJ modelini izleyerek harici CAD programlarından aktarımı sıfır kurulumla canlı hale getirdi.
7. **Kişisel Autodesk Fusion 360 Eklentisi (`OpenSlicerBridge`):**
   * Fusion 360'tan seçilen klasöre tek tıkla `[Proje]-[Gövde].stl` adıyla otomatik dışa aktarım sağlayan eklenti hazırlandı.
8. **Yazı Boyutları Düzeltmesi & Box 8 Label Size Kontrolü:**
   * Plakaya orantılı devasa yazı hatası giderildi; gerçek imalat milimetrik yazı boyutuna (4.0mm) ve parça içi otomatik sınırlamaya (Auto-Fit Clamping) geçildi.
   * Dairesel halka yuva yazılarına ışınsal açı desteği eklendi.
9. **Klavye Gezintisi (TAB Tuşu):**
   * Artırma/azaltma ve sıfırlama butonlarına `tabindex="-1"` atanarak form alanları arasında kesintisiz TAB geçişi sağlandı.
10. **GitHub Pages ve index.html Geçişi:**
    * Ana dosya `index.html` olarak adlandırıldı; GitHub Pages ve web sunucularında doğrudan yayına hazır hale getirildi.

---

## 5. Sıradaki Aşama ve Yol Haritası
* **`P2+` Devamı:**
  * **Curve Slices (`CS`):** Kullanıcı tanımlı eğri/omurga boyunca dilimleme.
  * **Folded Panels / Pepakura (`FP`):** Sac ve karton katlama açınımı.
* **Son Aşamalar:**
  * **`P1` — Tam Kapsamlı `.3MF` Proje Kaydet / Yükle:** Model, dilimleme ayarları, pimler ve parça durumlarının eksiksiz saklanması.
  * **`P3` — Gelişmiş Nesting & Web Worker:** True-polygon nesting ve arka plan iş parçacığı optimizasyonu.

---

## 6. İletişim ve Çalışma Prensipleri
* Kullanıcıyla her zaman **Türkçe**, net ve özlü iletişim kur.
* Dosya ve sembol referanslarında tıklanabilir markdown linkleri (`[dosya.uzanti](file:///...)`) kullan.
* Kullanıcı *"kod yazma, önce konuşalım"* dediğinde hiçbir dosya düzenleme aracı çağırma; tasarımı ve mimariyi netleştir, kullanıcı onay verdiğinde toplu geçişle uygula.
* **Sürüm numarasını** yalnızca kullanıcı açıkça talep ettiğinde arttır.
* **Yedekleme Kuralı:** Kullanıcı aksini belirtmediği sürece ana dosyada (`index.html`) yapılacak her önemli düzenlemeden önce `./Backup` klasörüne çalışan son sürüm yedeklenir.
