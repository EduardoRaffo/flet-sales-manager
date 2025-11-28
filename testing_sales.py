import pandas as pd
import random
from datetime import datetime, timedelta

n = 100
clientes = ["Sistemas Iberia", "TechNova", "Soluciones Ágiles", "Informática Madrid", "RedConect",
            "SoftIngenia", "Digitools", "NexTech", "GlobalTech", "Datacom"]
productos = ["Software", "Hardware", "Consultoría", "Licencia", "Mantenimiento"]

data = []
client_ids = set()

for i in range(n):
    # Generar IDs únicos
    while True:
        client_id = f"{random.choice('XYZ')}{random.randint(1000, 9999)}"
        if client_id not in client_ids:
            client_ids.add(client_id)
            break
    
    client_name = random.choice(clientes)
    product_type = random.choice(productos)
    price = round(random.uniform(500, 5000), 2)
    # Fechas más recientes (últimos 30 días)
    date = (datetime.today() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
    data.append([client_name, client_id, product_type, price, date])

df = pd.DataFrame(data, columns=["client_name", "client_id", "product_type", "price", "date"])
df.to_csv("testing_ventas.csv", index=False, encoding='utf-8')

print("✅ CSV generado correctamente")
print(f"Total registros: {len(df)}")
print(f"Primeras filas:\n{df.head()}")
