import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA (ESTILO PROFESIONAL) ---
st.set_page_config(
    page_title="Dashboard de Vehículos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo de gráficos más bonito
plt.style.use('ggplot')

# --- CARGA DE DATOS ---
try:
    df = pd.read_csv('car_price_prediction_.csv')
except FileNotFoundError:
    st.error("⚠️ No encuentro el archivo 'car_price_prediction_.csv'.")
    st.stop()

# --- TÍTULO Y DESCRIPCIÓN ---
st.title('🚗 Tablero de Control de Mercado Automotriz')
st.markdown("""
Bienvenido al panel de análisis. Aquí puedes explorar cómo influyen el **kilometraje**, 
la **condición** y la **marca** en el precio final de los vehículos.
""")

st.divider()

# --- BARRA LATERAL (FILTROS INTELIGENTES) ---
st.sidebar.header('🔍 Filtros de Búsqueda')

# 1. Filtro de Marca
todas_marcas = sorted(df['Brand'].unique())
marcas_sel = st.sidebar.multiselect('Selecciona Marcas:', todas_marcas, default=todas_marcas[:3])

# 2. Filtro de Año (Slider doble)
min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
year_range = st.sidebar.slider('Rango de Años:', min_year, max_year, (min_year, max_year))

# 3. Filtro de Condición
condiciones = df['Condition'].unique()
condicion_sel = st.sidebar.multiselect('Condición del auto:', condiciones, default=condiciones)

# --- APLICAR FILTROS ---
df_filtered = df[
    (df['Brand'].isin(marcas_sel)) &
    (df['Year'].between(year_range[0], year_range[1])) &
    (df['Condition'].isin(condicion_sel))
]

# --- SECCIÓN 1: KPIs (INDICADORES CLAVE) ---
# Esto le da contexto inmediato al usuario
st.subheader("📊 Resumen General")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Autos", f"{len(df_filtered)}")
with col2:
    # Formato de dinero con comas
    promedio = df_filtered['Price'].mean()
    st.metric("Precio Promedio", f"${promedio:,.0f}")
with col3:
    # Auto más barato en la selección
    min_price = df_filtered['Price'].min()
    st.metric("Precio Mínimo", f"${min_price:,.0f}")
with col4:
    # Auto más caro
    max_price = df_filtered['Price'].max()
    st.metric("Precio Máximo", f"${max_price:,.0f}")

st.divider()

# --- SECCIÓN 2: ANÁLISIS DE PRECIOS Y DEPRECIACIÓN ---
col_izq, col_der = st.columns([2, 1]) # La columna izquierda es más ancha

with col_izq:
    st.subheader("📉 ¿Cómo afecta el kilometraje al precio?")
    st.caption("Cada punto es un auto. El color indica el año del modelo.")
    
    # Gráfico de Dispersión AVANZADO (Con color por año)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # Scatter plot: X=Millas, Y=Precio, Color=Año
    scatter = ax1.scatter(
        df_filtered['Mileage'], 
        df_filtered['Price'], 
        c=df_filtered['Year'], 
        cmap='viridis', # Mapa de color moderno
        alpha=0.6,      # Transparencia para ver puntos superpuestos
        edgecolors='w'
    )
    
    ax1.set_xlabel('Kilometraje (Millas)')
    ax1.set_ylabel('Precio ($)')
    ax1.set_title('Relación Kilometraje vs. Precio')
    plt.colorbar(scatter, label='Año del Modelo') # Barra de color lateral
    st.pyplot(fig1)

with col_der:
    st.subheader("⛽ Distribución por Combustible")
    st.caption("¿Qué tipo de motor domina tu selección?")
    
    # Conteo por tipo de combustible
    fuel_counts = df_filtered['Fuel Type'].value_counts()
    
    # Gráfico de DONA (Donut Chart)
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.pie(
        fuel_counts, 
        labels=fuel_counts.index, 
        autopct='%1.1f%%', 
        startangle=90,
        wedgeprops={'width': 0.4, 'edgecolor': 'white'} # Esto lo hace dona
    )
    ax2.set_title('Tipos de Combustible')
    st.pyplot(fig2)

st.divider()

# --- SECCIÓN 3: COMPARATIVA DE MARCAS ---
st.subheader("🏆 Comparativa de Precios por Marca")
st.caption("Promedio de precio para las marcas seleccionadas.")

# Agrupar por marca y calcular promedio
avg_price_brand = df_filtered.groupby('Brand')['Price'].mean().sort_values()

fig3, ax3 = plt.subplots(figsize=(12, 5))
# Gráfico de barras horizontales
barras = ax3.barh(avg_price_brand.index, avg_price_brand.values, color='cornflowerblue')

ax3.set_xlabel('Precio Promedio ($)')
ax3.set_title('Precio Promedio por Marca')

# Agregar el precio al final de cada barra (Detalle pro)
for index, value in enumerate(avg_price_brand.values):
    ax3.text(value, index, f' ${value:,.0f}', va='center')

st.pyplot(fig3)

# --- FIN ---
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y Matplotlib")
