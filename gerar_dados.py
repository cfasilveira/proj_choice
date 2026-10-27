import random
from datetime import datetime, timedelta

import pandas as pd

random.seed(42)  # For reproducibility

clients = ['Hospital_Sao_Lucas', 'DataCenter_AWS', 'Telecom_Vivo', 'Hospital_Albert_Einstein', 'DataCenter_Equinix']
regions = ['EMEA', 'APAC']
carriers = ['DHL', 'FedEx', 'UPS', 'GlobalExpress', 'LocalPartner']
statuses = ['Delivered', 'Exception', 'Stock-out']

data = []

base_date = datetime(2026, 10, 1, 8, 0, 0) # Starts at October 1, 2026


for i in range(100):  # Generate 100 rows of data
    order_id = f"ORD-{1000 + i}"
    client = random.choice(clients)
    region = random.choice(regions)
    carrier = random.choice(carriers)

    # Order date for 30 days ago
    order_time = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))

    # Simulando os Gargalos (A "Dor" da Choice)
    # Cenário 1: A transportadora GlobalExpress na APAC é lenta
    # Cenário 2: Stock-out gera atrasos enormes
    is_apac_global = (region == 'APAC' and carrier == 'GlobalExpress')
    is_friday = order_time.weekday() == 4

    # Definir status
    if random.random() < 0.05: # 5% de chance de Stock-out
        status = 'Stock-out'
        delivery_hours = random.randint(48, 72) # Demora muito
    elif is_apac_global and is_friday:
        status = 'Exception'
        delivery_hours = random.randint(24, 36) # Estoura o SLA
    else:
        status = 'Delivered'
        delivery_hours = random.randint(4, 12) # Tempo normal para peças críticas

        # Calcular tempos
    dispatch_time = order_time + timedelta(hours=random.randint(1, 3)) # Tempo para separar a peça
    delivery_time = dispatch_time + timedelta(hours=delivery_hours)

    # SLA padrão da Choice para peças críticas (ex: 12 horas)
    sla_hours = 12
    
    # Calcular se houve SLA Breach
    sla_breach = "Yes" if delivery_hours > sla_hours else "No"
    
    # Simular custo (Stock-out gera frete aéreo de emergência, custo dobra)
    base_cost = random.uniform(100.0, 500.0)
    cost = base_cost * 2.5 if status == 'Stock-out' else base_cost

    data.append({
        'Order_ID': order_id,
        'Client': client,
        'Region': region,
        'Carrier_Partner': carrier,
        'Order_Time': order_time.strftime('%Y-%m-%d %H:%M:%S'),
        'Dispatch_Time': dispatch_time.strftime('%Y-%m-%d %H:%M:%S'),
        'Delivery_Time': delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
        'Delivery_Hours': delivery_hours,
        'SLA_Hours': sla_hours,
        'SLA_Breach': sla_breach,
        'Status': status,
        'Cost_USD': round(cost, 2)
    })

# Criar o DataFrame e salvar em CSV
df = pd.DataFrame(data)
df.to_csv('choice_logistics_orders.csv', index=False)

print("Arquivo 'choice_logistics_orders.csv' gerado com sucesso!")
print(f"Total de pedidos: {len(df)}")
print(df.head())
    
