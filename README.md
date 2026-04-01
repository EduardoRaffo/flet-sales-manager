# Python Desktop Sales CRM

A desktop CRM application for sales management, client tracking and lead pipeline analysis. Built with Python and Flet (Flutter-based desktop UI framework).

Developed as part of a professional internship project.

---

## ✨ Features

- **Sales dashboard** — KPI cards, trend charts and period comparison
- **Client management** — full CRUD, client profile with sales history
- **Lead pipeline** — funnel chart, source analysis and conversion tracking
- **Marketing analytics** — spend tracking and ROI per channel
- **Period comparison** — side-by-side analysis of any two date ranges
- **HTML report export** — printable reports per client, sales or leads
- **CSV / Excel import** — bulk data import with validation and error logging
- **Dark / light theme** — full theme system with live switching
- **SQLite storage** — local database, no server required

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | [Flet](https://flet.dev) 0.82 (Flutter/Material 3, desktop-only) |
| Data analysis | [Polars](https://pola.rs) 1.35 + Pandas 2.2 |
| Charts | flet-charts + Matplotlib (HTML reports) |
| Database | SQLite 3 (via Python stdlib) |
| File import | openpyxl 3.1 (Excel + CSV) |
| Testing | pytest (~400 tests) |
| Python | 3.13+ |

---

## 🚀 Getting Started

**Requirements:** Python 3.13+

```bash
# 1. Clone the repository
git clone https://github.com/EduardoRaffo/python-desktop-crm.git
cd python-desktop-crm

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## 🧪 Running Tests

```bash
# Full test suite (~400 tests)
pytest tests/ -v

# Single test file
pytest tests/test_sales_analysis.py -v

# Single test case
pytest tests/test_sales_analysis.py::TestGetSalesSummary::test_filter_by_client -v
```

---

## 🏗️ Architecture

The project follows a strict 10-layer architecture where dependencies only flow downward:

```
10. main.py         → App init, Flet page setup
 9. ui/             → Routing and navigation
 8. views/          → Screens: dashboard, sales, clients, leads
 7. components/     → 25+ reusable Flet widgets
 6. controllers/    → Input validation + service coordination
 5. services/       → Complex analysis orchestration
 4. analysis/       → Metric calculations with Polars
 3. domain/         → Pure data models (AnalysisSnapshot, DashboardKPISnapshot)
 2. core/           → DB connection, CSV importer, date utilities
 1. sales.db        → Local SQLite persistence
```

---

## 📁 Project Structure

```
├── main.py                 # Entry point
├── requirements.txt        # Runtime dependencies
├── analysis/               # Polars-based metric calculations
├── assets/                 # App icons
├── components/             # 25+ reusable Flet UI widgets
├── controllers/            # Input validation and service coordination
├── core/                   # DB, importer, date range utilities
├── domain/                 # Pure data models
├── models/                 # Client, lead and marketing managers
├── reports/                # HTML report generation (Matplotlib)
├── services/               # Business logic orchestrators
├── theme/                  # Color system and theme utilities
├── ui/                     # Main router (user_ui.py)
├── utils/                  # Formatting, notifications, file dialogs
└── views/                  # Dashboard, sales, clients, leads screens
```

---

## 📄 License

This project is provided for portfolio and educational purposes.
