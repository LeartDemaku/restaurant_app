# 🍽️ Restaurant Management System (Python Desktop POS & Web App)

A professional, full-featured restaurant management and Point of Sale (POS) system built in **Python**, designed with high performance, a clean modern interface, and 100% design fidelity to the original Java POS architecture.

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 🌟 Architecture & Highlights

1. **Desktop Application (CustomTkinter)**: Ultra-responsive desktop cashier terminal for high-speed front-desk order processing.
2. **Web Application (FastAPI + HTML5/CSS3/JS)**: Mobile-optimized web portal matching the original Java `GUI.java` layout 1:1, accessible by waiters via tablets/phones and by chefs via Kitchen Display.
3. **Shared SQLite Database**: Instant synchronization between desktop registers, kitchen screens, and mobile devices.
4. **Waiter Sales Tracking**: Waiters can enter their own name when taking orders, with comprehensive revenue tracking per waiter.

---

## 🚀 Key Features

### 1. Point of Sale (POS) - Desktop & Web
- **100% Visual Alignment with Java GUI**:
  - 3-column button grid with solid category colors:
    - 🔵 **Drinks (`#3498DB`)**: Sodas, mineral waters, natural juices, beers, wines, traditional spirits.
    - 🟤 **Coffee (`#8D6E63`)**: Espresso, macchiato, cappuccino, herbal teas, hot chocolates.
    - 🔴 **Food (`#E74C3C`)**: Gyros, doner, kebabs, pljeskavica, steaks, pizzas, burgers, pasta, salads, soups.
    - 🟠 **Desserts (`#E67E22`)**: Trilece, baklava, tiramisu, cheesecake, soufflé, milkshakes.
  - Rectangular buttons with bold white titles and golden-yellow prices (`#F39C12`).
- **Current Order Panel**:
  - Bordered panel with `Total: 0.00€` in prominent green (`#27AE60`, 22px).
  - Clean monospace receipt view (`Consolas`) with fixed-column formatting:
    ```text
    Coca Cola 0.33l                 1.50€
    Espresso Single                 1.00€
    Sufllaqe me Pule                3.00€
    ```
  - **Quick Undo** button (`↶ Undo Last`) to easily revert the last selected item.
  - Action buttons:
    - **Print** (Blue): Generates a printable thermal-style receipt.
    - **Clear** (Red): Clears current order and resets total to 0.00€.
    - **Save Order** (Green): Prompts for waiter name and table number, persisting to SQLite database.

### 2. Orders Management Tab
- Real-time tabular view with columns: `Date`, `Waiter`, `Table`, `Total`, `Status`, `Actions`.
- Live status updates with instant dropdown selection:
  - 🔴 **New**: Order just received.
  - 🟡 **In Preparation**: Kitchen has started preparing.
  - 🟢 **Ready / Completed**: Ready to serve or paid.
- Quick single-order deletion and a master **Clear All Orders** button.

### 3. Kitchen Display System (KDS) (`/kitchen`)
- Live kitchen board displaying active orders in real time.
- Direct status transitions: "Prepare" ➔ "Ready" ➔ "Complete".
- Displays customer notes, preparation timestamps, and table assignments.

### 4. Interactive Table Map (`/tables`)
- Visual overview of all restaurant tables across main hall and terrace:
  - 🟢 **Green (Free)**: Available for new guests; one-click order creation.
  - 🔴 **Red (Occupied)**: Displays waiter in charge and current running bill.
  - 🟡 **Yellow (Reserved)**: Reserved tables.

### 5. Daily Statistics & Reports (`/reports`)
- Monospace ASCII & graphical financial breakdown:
  - Total daily turnover (€).
  - Total order count.
  - Average ticket size.
  - **Sales breakdown by waiter** (orders count, total revenue, average order value).
  - Top 5 best-selling items of the day.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the repository
```bash
git clone https://github.com/LeartDemaku/restaurant_app.git
cd restaurant_app
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

### Method 1: All-in-One Launcher (Recommended)
Launches the Desktop POS application and starts the local Web Server in the background:
```bash
python main.py
```
> **Tip**: The console will display a **QR Code** that staff can scan with a smartphone or tablet to immediately open the Web POS!

### Method 2: Web Server Only
Ideal for running on a local server, Raspberry Pi, or tablet/mobile devices:
```bash
python run_web.py
```
Open your browser at:
- **POS Cashier**: `http://localhost:8000/pos`
- **Kitchen Screen (KDS)**: `http://localhost:8000/kitchen`
- **Table Map**: `http://localhost:8000/tables`
- **Menu Management**: `http://localhost:8000/admin/menu`
- **Financial Reports**: `http://localhost:8000/reports`

### Method 3: Desktop App Only
```bash
python run_desktop.py
```

---

## 📂 Project Directory Structure

```
restaurant_app/
├── database/
│   ├── db.py                 # SQLite database connection & schema definitions
│   ├── models.py             # CRUD data models (orders, menu items, waiters, tables)
│   └── seed_data.py          # Database seeding with authentic menu items
├── core/
│   ├── config.py             # Global configurations, currency (€), and local network IP
│   └── receipt.py            # Monospace text & HTML receipt generators
├── desktop/
│   ├── app_gui.py            # Desktop POS application built with CustomTkinter
│   ├── dialogs.py            # Modal dialogs (Save Order, Payment, Change Calculator)
│   └── theme.py              # Theme palette matching Java GUI colors
├── web/
│   ├── app.py                # FastAPI application & REST API endpoints
│   ├── static/
│   │   ├── css/style.css     # CSS styles matching Java GUI 1:1
│   │   └── js/app.js         # Interactive cart, receipt formatting, and tab logic
│   └── templates/
│       ├── base.html         # Base template with header & main tabs
│       ├── pos.html          # POS page (Orders, Management, Statistics tabs)
│       ├── kitchen.html      # Kitchen Display System (KDS)
│       ├── tables.html       # Visual Table Map
│       ├── admin_menu.html   # Menu item management
│       └── reports.html      # Analytics & reports page
├── main.py                   # Unified launcher (Desktop GUI + Web Server + QR code)
├── run_web.py                # Web server standalone runner
├── run_desktop.py            # Desktop application standalone runner
├── test_api.py               # Automated REST API & endpoint test suite
├── test_system.py            # End-to-end database & receipt test suite
├── requirements.txt          # Python project dependencies
└── README.md                 # Project documentation
```

---

## 🧪 Testing

Run the automated test suites to verify database integrity, API routes, and receipt generation:
```bash
python test_api.py
python test_system.py
```

---

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it for personal and commercial restaurant operations.
