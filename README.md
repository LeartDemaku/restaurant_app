# 🍽️ Sistemi i Menaxhimit të Restorantit në Python (Desktop POS & Web App)

Ky projekt është një sistem i plotë dhe profesional për menaxhimin e restorantit, i ndërtuar në **Python**, i cili integron:
1. **Aplikacion Desktop Modern (CustomTkinter)** për arkën qendrore të restorantit.
2. **Aplikacion Web & Mobile (FastAPI + HTML5/CSS)** për kamarierët me telefon/tablet dhe ekranin live të kuzhinës (KDS).
3. **Bazë të Dhënash të Përbashkët (SQLite)** me sinkronizim të menjëhershëm mes arkës, kuzhinës dhe kamarierëve në tavolina.

---

## 🌟 Funksionalitetet Kryesore

### 1. Kasa POS (Point of Sale) - Desktop & Web
- Mbi **70+ artikuj autentikë** me çmime në Euro (€), të ndarë në 4 kategori kryesore me ngjyra përkatëse:
  - 🔵 **Pije**: Pije të gazuara, ujëra, lëngje natyrale, birra, verëra, raki shtëpie.
  - 🟤 **Kafe**: Espresso, macchiato, cappuccino, çajra bimorë, çokollata të ngrohta.
  - 🔴 **Ushqim**: Sufllaqe, doner, qebapa, pleskavica, biftak, pica, burgere, pasta, sallata, supa.
  - 🟠 **Embëlsirë**: Trileçe, bakllavë, tiramisu, cheesecake, soufflé, pulla, milkshake.
- Shportë interaktive me shtim të shpejtë, rritje/zbritje të sasive me `+` dhe `-`.
- Zgjedhje tavoline (1 deri 16) dhe përzgjedhje e kamarierit.
- Llogaritje automatike e totalit të faturës.

### 2. Menaxhimi i Porosive në Kohë Reale
- Ndjekja e statusit të çdo porosie:
  - 🔴 **E Re**: Porosia sapo është regjistruar nga kamarieri.
  - 🟡 **Në Përgatitje**: Kuzhina po e përgatit porosinë.
  - 🟢 **Gati**: Ushqimi/pija është gati për t'u shërbyer në tavolinë.
  - ⚪ **E Përfunduar / Paguar**: Fatura është arkëtuar dhe tavolina lirohet automatikisht.

### 3. Ekrani i Kuzhinës (KDS - Kitchen Display System)
- Faqe ueb e posaçme (`/kitchen`) që përditësohet automatikisht çdo disa sekonda.
- Kuzhinierët shohin kartat e porosive sipas radhës me kohën e porositjes dhe shënimet speciale.
- Me 1 klikim ndryshohet statusi në "Në Përgatitje" dhe "Gati për Shërbim".

### 4. Harta Vizuale e Tavolinave (`/tables`)
- Pamje grafike e 16 tavolinave të sallës kryesore dhe verandës:
  - 🟢 **E Gjelbër (E Lirë)**: Gati për mysafirë të rinj, hapje porosie me 1 klik.
  - 🔴 **E Kuqe (E Zënë)**: Shfaq kamarierin përgjegjës dhe vlerën e faturës aktuale.
  - 🟡 **E Verdhë (E Rezervuar)**.

### 5. Faturimi dhe Printimi
- Gjenerim fature termale (format 80mm/58mm).
- Format fature HTML për printim direkt në çdo printer Windows ose ruajtje PDF.

### 6. Menaxhimi i Menysë & Çmimeve
- Shto artikuj të rinj, ndrysho çmimet, përditëso stokun, ose fshi artikuj pa prekur kodin.

### 7. Statistikat & Raportet Ditore
- Pasqyra e xhiros ditore në Euro (€), numri i porosive, dhe vlera mesatare për faturë.
- Top 5 artikujt më të shitur të ditës.
- Filtrimi i të dhënave sipas çdo date të dëshiruar.

---

## 🚀 Si të Niset Sistemi

### Mënyra 1: Nisja e Integruar (Rekomandohet)
Nis njëkohësisht Desktop App-in në ekran dhe Web Serverin në prapaskenë:
```bash
python main.py
```
> Terminali do të shfaqë gjithashtu adresën lokale dhe një **QR Code** që kamarierët mund ta skanojnë me telefon për të hapur menjëherë sistemin!

### Mënyra 2: Nisja vetëm e Web Serverit
Ideale nëse dëshironi ta përdorni sistemin nga shfletuesi në tablet/telefon:
```bash
python run_web.py
```
Hapni në shfletues:
- **POS / Kasa**: `http://localhost:8000/pos`
- **Ekrani i Kuzhinës**: `http://localhost:8000/kitchen`
- **Harta e Tavolinave**: `http://localhost:8000/tables`
- **Menaxhimi i Menysë**: `http://localhost:8000/admin/menu`
- **Statistikat**: `http://localhost:8000/reports`

### Mënyra 3: Nisja vetëm e Aplikacionit Desktop
```bash
python run_desktop.py
```

---

## 📁 Struktura e Projektit

```
AppRestaurant/
├── database/
│   ├── db.py                 # Lidhja me SQLite dhe skema relacionale
│   ├── models.py             # Funksionet e të dhënave (CRUD, porositë, faturat)
│   └── seed_data.py          # Populimi fillestar i mbi 70 artikujve nga Java GUI
├── core/
│   ├── config.py             # Konfigurimet (titulli, monedha €, IP rrjeti)
│   └── receipt.py            # Gjeneruesi i faturave termale dhe HTML
├── web/
│   ├── app.py                # Serveri kryesor FastAPI dhe REST API
│   ├── static/
│   │   ├── css/style.css     # Stilet moderne responsive
│   │   └── js/app.js         # Ndërveprimi i shportës dhe rifreskimi automatik
│   └── templates/
│       ├── base.html         # Skeleti kryesor
│       ├── pos.html          # Ndërfaqja POS për kamarierët
│       ├── kitchen.html      # Ekrani live i kuzhinës (KDS)
│       ├── tables.html       # Harta e tavolinave
│       ├── admin_menu.html   # Menaxhimi i menusë
│       └── reports.html      # Statistikat me grafikë
├── desktop/
│   ├── app_gui.py            # Aplikacioni kryesor Desktop me CustomTkinter
│   ├── dialogs.py            # Dritaret modale (Ruaj porosi, shiko faturë, shto artikull)
│   └── theme.py              # Temat dhe ngjyrat Dark/Light
├── main.py                   # Nisësi qendror
├── run_web.py                # Nisës vetëm për ueb
├── run_desktop.py            # Nisës vetëm për desktop
├── requirements.txt          # Paketat e nevojshme
└── README.md                 # Ky dokumentacion
```
