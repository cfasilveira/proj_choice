import os

import pandas as pd


def carregar_dados(caminho_csv):
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo {caminho_csv} não encontrado. Rode o gerar_dados.py primeiro.")
    return pd.read_csv(caminho_csv)

def calcular_kpis(df):
    print("="*50)
    print(" RELATÓRIO DE PERFORMANCE - CHOICE LOGISTICS (PoC)")
    print("="*50)
    
    # 1. Order Cycle Time (Tempo Médio de Ciclo do Pedido)
    # Convertemos as colunas de data para o formato datetime para calcular a diferença
    df['Order_Time'] = pd.to_datetime(df['Order_Time'])
    df['Delivery_Time'] = pd.to_datetime(df['Delivery_Time'])
    
    # Calculando a diferença em horas
    df['Cycle_Time_Hours'] = (df['Delivery_Time'] - df['Order_Time']).dt.total_seconds() / 3600
    
    avg_cycle_time = df['Cycle_Time_Hours'].mean()
    print(f"\n[1] Order Cycle Time Médio: {avg_cycle_time:.2f} horas")
    
    # 2. SLA Attainment (Aderência ao SLA)
    total_pedidos = len(df)
    sla_breaches = len(df[df['SLA_Breach'] == 'Yes'])
    sla_attainment = ((total_pedidos - sla_breaches) / total_pedidos) * 100
    
    print(f"[2] SLA Attainment: {sla_attainment:.2f}% ({total_pedidos - sla_breaches} de {total_pedidos} pedidos dentro do prazo)")
    
    # 3. Exception & Stock-out Rate
    exceptions = len(df[df['Status'] == 'Exception'])
    stockouts = len(df[df['Status'] == 'Stock-out'])
    
    print(f"[3] Taxa de Exceções: {(exceptions/total_pedidos)*100:.2f}% ({exceptions} pedidos)")
    print(f"    Taxa de Stock-out: {(stockouts/total_pedidos)*100:.2f}% ({stockouts} pedidos)")
    
    # 4. Cost-to-Serve (Custo Médio por Região e Transportadora)
    print("\n[4] Cost-to-Serve (Custo Médio por Pedido em USD):")
    custo_por_regiao = df.groupby('Region')['Cost_USD'].mean().round(2)
    for regiao, custo in custo_por_regiao.items():
        print(f"    - {regiao}: ${custo}")
        
    # 5. Identificando o Gargalo (Root Cause Analysis)
    print("\n[5] Análise de Gargalos (Top 3 Transportadoras com mais SLA Breach):")
    # Filtrando apenas os que deram breach, agrupando por transportadora e contando
    gargalos = df[df['SLA_Breach'] == 'Yes'].groupby('Carrier_Partner').size().sort_values(ascending=False).head(3)
    for carrier, qtd in gargalos.items():
        print(f"    - {carrier}: {qtd} falhas")
        
    print("\n" + "="*50)

if __name__ == "__main__":
    # Carrega os dados
    caminho = 'choice_logistics_orders.csv'
    df = carregar_dados('/home/carlos/Projetos/proj_choice/choice_logistics_orders.csv')
    
    # Calcula e exibe os KPIs
    calcular_kpis(df)