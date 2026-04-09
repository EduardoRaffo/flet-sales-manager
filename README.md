# FDT Sales Manager 📊

**Desktop CRM application for sales pipeline management, client tracking, and lead analysis — built with Python + Flet**

![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square)
![Flet](https://img.shields.io/badge/Flet-0.82.0+-purple?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-3-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## 🚀 What this project demonstrates

- Data processing & analytics with Polars
- Clean architecture (modular, scalable design)
- ~400 automated tests with pytest
- Real-world data handling (10K+ records)
- Focus on performance and maintainability

## 🎯 Problem Statement

Sales teams waste hours managing spreadsheets, tracking pipeline progress manually, and losing visibility into client relationships. **FDT Sales Manager** centralizes all sales data—clients, leads, sales history, and performance metrics—in a single, interactive desktop application with real-time analytics.

---

## 💡 Why This Project Matters

Building a full desktop CRM from scratch in Python required solving real software engineering challenges: clean layered architecture, reactive UI state, Polars-powered analytics at scale, and a comprehensive test suite (~400 pytest tests). This project demonstrates practical **Python backend development** skills applied to a real business domain.

---

## ✨ Key Features

- **Dashboard with KPIs**: Real-time metrics—total sales, conversion rates, client count, average deal size
- **Sales Pipeline Management**: Track deals by status, source, and client with visual funnels
- **Client Database**: Complete client profiles with contact info, purchase history, and lifecycle tracking
- **Lead Management**: Organize leads by source (ads, referrals, direct), status, and conversion probability
- **Data Import**: Bulk import sales, clients, and leads from Excel/CSV files
- **Advanced Filtering**: Filter by date range, client, product, source, and custom fields
- **Performance Reports**: HTML-embedded charts and period-over-period analysis
- **Multi-period Comparison**: Compare sales metrics across different time periods
- **Dark/Light Theme**: Professional theme support for extended use

## 🏗️ Architecture

```
10-Layer Clean Architecture
├── Layer 10: main.py (initialization)
├── Layer 9: ui/ (routing & navigation)
├── Layer 8: views/ (dashboard, sales, clients, leads)
├── Layer 7: components/ (25+ reusable Flet widgets)
├── Layer 6: controllers/ (input validation, service coordination)
├── Layer 5: services/ (analysis orchestration)
├── Layer 4: analysis/ (Polars-based metrics calculation)
├── Layer 3: domain/ (pure data models)
├── Layer 2: core/ (database, import, utilities)
└── Layer 1: sales.db (SQLite persistence)
```

**Key principle**: Zero upward dependencies. Layering enforces clean separation of concerns.

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------| 
| **Framework** | Flet (Flutter Desktop) | 0.82.0 |
| **Language** | Python | 3.13+ |
| **Database** | SQLite3 | Built-in |
| **Data Analysis** | Polars + Pandas | 1.35.2 + 2.2.3 |
| **Charts** | flet-charts | 0.82.0 |
| **Excel/CSV Import** | openpyxl | 3.1.5 |
| **HTML Reports** | Matplotlib | 3.10.8 |
| **Testing** | pytest | ~400 tests |

## 🚀 Quick Start

```bash
git clone https://github.com/EduardoRaffo/flet-sales-manager
cd flet-sales-manager
pip install -r requirements.txt
python main.py
```

### First Run

1. Application creates `sales.db` automatically on first launch
2. Use **Import** to load sample data from CSV/Excel
3. Navigate dashboard → sales → clients → leads tabs
4. Set date filters to analyze specific periods

## 📊 Dashboard

- **KPI Cards**: Total sales (YTD), number of clients, active leads, conversion rate
- **Sales Trend Chart**: Monthly sales evolution with comparison period overlay
- **Sales Funnel**: Lead-to-deal conversion visualization by source
- **Top Clients**: Client contribution to total sales

## 📋 Sales View

- **Sales Table**: All deals with client, product, amount, date, status
- **Advanced Filters**: Filter by date, client, product, deal status
- **Period Comparison**: Compare same period previous year or custom ranges

## 👥 Clients View

- **Client List**: All clients with contact info and lifetime value
- **Segmentation**: Group by industry, status, revenue tier
- **Growth Analysis**: Which clients are growing, at risk, or inactive

## 🎯 Leads View

- **Lead Funnel**: Visual progression from awareness → consideration → proposal → closed
- **Source Analysis**: ROI by lead source (ads, referrals, direct, etc.)

## 📈 Future Roadmap

- [ ] Team Collaboration: Multi-user support with role-based access
- [ ] Forecasting: Predictive analytics for pipeline forecast
- [ ] Mobile App: Companion app for iOS/Android
- [ ] API: RESTful API for third-party integrations (Slack, Zapier)
- [ ] Reporting Automation: Scheduled email reports

## 🧪 Testing

```bash
# Run all tests (~400 tests)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=.
```

Tests cover: analysis layer calculations (Polars), service orchestration, import validation, date range filtering.

## 🏆 Project Highlights

✅ **Clean Architecture**: 10-layer separation with zero upward dependencies
✅ **Comprehensive Testing**: ~400 pytest tests covering all business logic
✅ **Professional UI**: Desktop-first design with theme support
✅ **Real-time Analytics**: Polars-powered metrics recalculation on filter change
✅ **Scalable**: Handles 10K+ sales records with sub-second response times

## 📝 Project Structure

```
flet-sales-manager/
├── main.py             # Application entry point
├── requirements.txt    # Dependencies
├── sales.db            # SQLite database (auto-created)
├── analysis/           # Metrics calculation (Polars)
├── components/         # 25+ Flet widgets
├── controllers/        # Input validation & coordination
├── core/               # Database, import, utilities
├── domain/             # Pure data models
├── services/           # Analysis orchestration
├── theme/              # Color system & theming
├── ui/                 # Navigation & routing
├── views/              # Dashboard, sales, clients, leads
├── reports/            # HTML report generation
└── tests/              # ~400 pytest tests
```

## 📄 License

MIT License - free for personal and commercial use.

## 👤 Author

**Eduardo Raffo** - Python Developer
- GitHub: [github.com/EduardoRaffo](https://github.com/EduardoRaffo)
- LinkedIn: [linkedin.com/in/eduardo-raffo-benitez](https://linkedin.com/in/eduardo-raffo-benitez)

---

*Made with ❤️ for sales teams who want to work smarter*
