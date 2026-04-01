import csv
import random
from datetime import date, timedelta

# ==========================
# CONFIGURACIÓN
# ==========================

OUTPUT_FILE = "testing_web_5y.csv"
YEARS = 5
MIN_SALES_PER_DAY = 1
MAX_SALES_PER_DAY = 3

CLIENTS = [
    ("Alpha Capital", "ALPHA"),
    ("Market Flow", "MARKET"),
    ("Inversiones Delta", "DELTA"),
    ("Trade Pro Solutions", "TRADE"),
    ("Neo Traders", "NEO"),
]

PRODUCTS = [
    ("Curso Day Trading Level I", 250),
    ("Curso Day Trading Level II", 325),
    ("Curso Day Trading Avanzado", 395),
]

PRICE_VARIATION = (-20, 20)  # variación aleatoria €

# ==========================
# GENERACIÓN
# ==========================

today = date.today()
start_date = today - timedelta(days=YEARS * 365)

rows = []

current_date = start_date
while current_date <= today:
    sales_today = random.randint(MIN_SALES_PER_DAY, MAX_SALES_PER_DAY)

    for _ in range(sales_today):
        client_name, client_id = random.choice(CLIENTS)
        product_name, base_price = random.choice(PRODUCTS)

        price = base_price + random.randint(*PRICE_VARIATION)

        rows.append({
            "client_name": client_name,
            "client_id": client_id,
            "product_type": product_name,
            "price": round(price, 2),
            "date": current_date.isoformat(),
        })

    current_date += timedelta(days=1)

# ==========================
# ESCRITURA CSV
# ==========================

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["client_name", "client_id", "product_type", "price", "date"]
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ CSV generado correctamente: {OUTPUT_FILE}")
print(f"📊 Total registros: {len(rows)}")
