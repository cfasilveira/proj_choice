import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Choice Logistics - Performance Dashboard", layout="wide")

# Título
st.title("📊 Operational Performance Dashboard - EMEA & APAC")
st.markdown("**Prova de Conceito (PoC) | Carlos Silveira**")
st.markdown("---")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv('choice_logistics_orders.csv')
    df['Order_Time'] = pd.to_datetime(df['Order_Time'])
    df['Delivery_Time'] = pd.to_datetime(df['Delivery_Time'])
    df['Cycle_Time_Hours'] = (df['Delivery_Time'] - df['Order_Time']).dt.total_seconds() / 3600
    df['Date_Only'] = df['Order_Time'].dt.date 
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File not found. Please run gerar_dados.py first.")
    st.stop()

# ==========================================
# BARRA LATERAL (FILTROS)
# ==========================================
st.sidebar.header("🔍 Filters")

regioes = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regioes)

carriers = ['All'] + sorted(df['Carrier_Partner'].unique().tolist())
selected_carrier = st.sidebar.selectbox("Carrier", carriers)

clientes = ['All'] + sorted(df['Client'].unique().tolist())
selected_client = st.sidebar.selectbox("Client", clientes)

df_filtered = df.copy()
if selected_region != 'All':
    df_filtered = df_filtered[df_filtered['Region'] == selected_region]
if selected_carrier != 'All':
    df_filtered = df_filtered[df_filtered['Carrier_Partner'] == selected_carrier]
if selected_client != 'All':
    df_filtered = df_filtered[df_filtered['Client'] == selected_client]

# ==========================================
# FUNÇÃO PARA CRIAR KPIs COM BORDA (HTML/CSS)
# ==========================================
def kpi_card(title, value, delta=None, delta_color="normal"):
    # Define a cor do delta (verde para positivo, vermelho para negativo)
    color = "green" if (delta_color == "normal" and delta and not delta.startswith("-")) else "red" if delta and delta.startswith("-") else "gray"
    
    # Se o delta for inverso (ex: pior tempo), inverte a lógica de cor
    if delta_color == "inverse" and delta:
        color = "red" if not delta.startswith("-") else "green"

    delta_html = f"<p style='color: {color}; font-size: 14px; margin: 0; font-weight: bold;'>{delta}</p>" if delta else ""

    html = f"""
    <div style="
        border: 1px solid #d3d3d3;
        border-radius: 8px;
        padding: 15px;
        background-color: white;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    ">
        <p style="color: #555; font-size: 14px; margin: 0 0 5px 0;">{title}</p>
        <h2 style="color: #333; margin: 0; font-size: 28px;">{value}</h2>
        {delta_html}
    </div>
    """
    return html

# ==========================================
# KPIs PRINCIPAIS
# ==========================================
st.subheader(f"Operational Summary: {selected_region} | {selected_carrier} | {selected_client}")

total_pedidos = len(df_filtered)
SLA_META = 12

if total_pedidos > 0:
    sla_attainment = (len(df_filtered[df_filtered['SLA_Breach'] == 'No']) / total_pedidos) * 100
    avg_cycle = df_filtered['Cycle_Time_Hours'].mean()
    avg_cost = df_filtered['Cost_USD'].mean()
    
    min_cycle = df_filtered['Cycle_Time_Hours'].min()
    max_cycle = df_filtered['Cycle_Time_Hours'].max()
    
    best_vs_meta = ((min_cycle - SLA_META) / SLA_META) * 100
    worst_vs_meta = ((max_cycle - SLA_META) / SLA_META) * 100
    
    # Linha 1 de KPIs (Cards com Borda)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(kpi_card("Total Orders", f"{total_pedidos}"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("SLA Attainment", f"{sla_attainment:.1f}%"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Average Cycle Time (h)", f"{avg_cycle:.1f}h"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Average Cost (USD)", f"${avg_cost:.2f}"), unsafe_allow_html=True)
    
    # Linha 2 de KPIs (Cards com Borda)
    st.markdown("**Variability Analysis of Cycle Time (vs 12h SLA):**")
    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown(kpi_card("Best Time", f"{min_cycle:.1f}h", f"{best_vs_meta:.1f}% vs Meta", "normal"), unsafe_allow_html=True)
    with col6:
        st.markdown(kpi_card("Worst Time", f"{max_cycle:.1f}h", f"+{worst_vs_meta:.1f}% vs Meta", "inverse"), unsafe_allow_html=True)
    with col7:
        st.markdown(kpi_card("SLA Target", f"{SLA_META}h"), unsafe_allow_html=True)

else:
    st.warning("No data found.")
    st.stop()

st.markdown("---")

# ==========================================
# FUNÇÕES AUXILIARES (GRÁFICOS)
# ==========================================
def grafico_barras_com_media(df_agrupado, cor_barras):
    df_plot = df_agrupado.reset_index()
    df_plot.columns = ['Categoria', 'Valor']
    
    media_geral = df_plot['Valor'].mean()
    
    fig = px.bar(
        df_plot, 
        x='Categoria', 
        y='Valor',
        text='Valor',
        color_discrete_sequence=[cor_barras]
    )
    
    fig.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='inside',
        textfont={"color": 'white', "size": 14}
    )
    
    # Linha de média AGORA PRETA
    fig.add_hline(
        y=media_geral, 
        line_dash="dash", 
        line_color="#000000", 
        line_width=2,
        annotation_text=f"Average: {media_geral:.1f}", 
        annotation_position="top right",
        annotation_font={"color": "#000000", "size": 12, "family": "Arial Black"}
    )
    
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        yaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
        xaxis={"tickfont": {"size": 12, "color": 'black'}},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def grafico_linha_tendencia(df_agrupado):
    df_plot = df_agrupado.reset_index()
    df_plot.columns = ['Data', 'Volume']
    df_plot['Data'] = pd.to_datetime(df_plot['Data']).dt.strftime('%Y-%m-%d')
    
    fig = px.line(df_plot, x='Data', y='Volume')
    
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        yaxis={"showgrid": True, "gridcolor": '#eeeeee'},
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(line_color='#1f77b4', line_width=2)
    return fig

# ==========================================
# RENDERIZAÇÃO DOS GRÁFICOS
# ==========================================
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Order Volume (Trend)")
    volume_diario = df_filtered.groupby('Date_Only').size()
    fig_tendencia = grafico_linha_tendencia(volume_diario)
    st.plotly_chart(fig_tendencia, use_container_width=True)

with col_right:
    st.subheader("⚠️ Top Bottlenecks (SLA Breach by Carrier)")
    breach_df = df_filtered[df_filtered['SLA_Breach'] == 'Yes'].groupby('Carrier_Partner').size().sort_values(ascending=False)
    if not breach_df.empty:
        fig_breach = grafico_barras_com_media(breach_df, '#ff4b4b')
        st.plotly_chart(fig_breach, use_container_width=True)
    else:
        st.success("No SLA Breach!")

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🏢 Top 5 Clients (By Volume)")
    top_clientes = df_filtered['Client'].value_counts().head(5)
    fig_clientes = grafico_barras_com_media(top_clientes, '#5dade2')
    st.plotly_chart(fig_clientes, use_container_width=True)

with col_right2:
    st.subheader("🚚  Carrier Usage Frequency")
    freq_carrier = df_filtered['Carrier_Partner'].value_counts()
    fig_carrier = grafico_barras_com_media(freq_carrier, '#2e8b57')
    st.plotly_chart(fig_carrier, use_container_width=True)

# ==========================================
# TABELA DETALHADA
# ==========================================
st.subheader("📋 Failed Orders Detail (Exception / Stock-out)")
failed_orders = df_filtered[df_filtered['Status'].isin(['Exception', 'Stock-out'])][['Order_ID', 'Client', 'Region', 'Carrier_Partner', 'Status', 'Cost_USD']]

if not failed_orders.empty:
    st.dataframe(failed_orders, use_container_width=True)
else:
    st.info("No failed orders.")