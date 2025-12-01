import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="Análisis de Mercado Automotor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

sns.set_theme(style="whitegrid")
# Paleta de colores ajustada
COLOR_BARRA = "#2ecc71"
COLOR_NEGATIVO = "#e74c3c"

# --- 2. CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv('car_price_prediction_.csv')
        df.rename(columns={
            'Brand': 'Marca', 'Year': 'Año', 'Engine Size': 'Motor (L)',
            'Fuel Type': 'Combustible', 'Transmission': 'Transmisión',
            'Mileage': 'Kilometraje', 'Condition': 'Condición',
            'Price': 'Precio', 'Model': 'Modelo'
        }, inplace=True)
        return df
    except FileNotFoundError:
        return None

df = cargar_datos()

if df is None:
    st.error("¡Ups! No pude encontrar el archivo 'car_price_prediction_.csv'. Por favor, asegúrate de subirlo a tu repositorio de GitHub para que todo funcione.")
    st.stop()

# --- 3. BARRA LATERAL (FILTROS) ---
with st.sidebar:
    st.header("🎛️ Configura tu vista")
    st.write("Selecciona qué tipo de vehículos quieres analizar:")
    marcas = sorted(df['Marca'].unique())
    sel_marcas = st.multiselect("Seleccionar Marca(s):", marcas, default=marcas[:3])
    
    sel_anio = st.slider("Rango de Años:", int(df['Año'].min()), int(df['Año'].max()), (2015, 2023))
    
    if not sel_marcas: sel_marcas = marcas # Si no selecciona nada, selecciona todo

# Aplicar filtros
df_filtrado = df[
    (df['Marca'].isin(sel_marcas)) &
    (df['Año'].between(sel_anio[0], sel_anio[1]))
]

# --- 4. TÍTULO ---
st.title("🚗 Análisis de Tendencias en el Mercado Automotriz")
st.markdown(f"A continuación, presentamos un informe interactivo basado en **{len(df_filtrado)}** vehículos de las marcas: *{', '.join(sel_marcas[:5])}*.")
st.markdown("---")

# --- 5. PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 Resumen General", "🧠 Análisis de Factores", "💰 Estimador de Valor"])

# === PESTAÑA 1: PANORAMA ===
with tab1:
    st.subheader("Indicadores Clave de Desempeño (KPIs)")
    # KPIs Estilizados
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio Promedio de Mercado", f"${df_filtrado['Precio'].mean():,.0f}")
    col2.metric("Kilometraje Medio", f"{df_filtrado['Kilometraje'].mean():,.0f} km")
    col3.metric("Antigüedad Promedio", f"{2024 - df_filtrado['Año'].mean():.1f} años")
    col4.metric("Vehículos Disponibles", len(df_filtrado))

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Análisis de Precios")
        fig, ax = plt.subplots(figsize=(10, 6))
        # Histograma
        sns.histplot(df_filtrado['Precio'], kde=True, color="skyblue", element="step", ax=ax)
        ax.set_title("Distribución de Precios en el Mercado Actual")
        ax.set_xlabel("Precio de Venta ($)")
        ax.set_ylabel("Frecuencia (Cantidad de Autos)")
        st.pyplot(fig)

    with c2:
        st.subheader("Composición por Estado del Vehículo")
        # Gráfico de Pastel
        conteo = df_filtrado['Condición'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(conteo, labels=conteo.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        circulo = plt.Circle((0,0), 0.70, fc='white')
        fig.gca().add_artist(circulo)
        st.pyplot(fig)

# === PESTAÑA 2: INTELIGENCIA ===
with tab2:
    st.subheader("¿Qué factores determinan el precio?")
    st.markdown("En esta sección analizamos cómo influyen las distintas características técnicas en el valor final del vehículo.")

    # Calculamos correlación
    cols_numericas = df_filtrado.select_dtypes(include=['number'])
    correlacion = cols_numericas.corr()[['Precio']].sort_values(by='Precio', ascending=False)
    correlacion = correlacion.drop('Precio')

    # Gráfico de Barras Horizontal
    fig, ax = plt.subplots(figsize=(10, 5))
    colores = [COLOR_BARRA if x > 0 else COLOR_NEGATIVO for x in correlacion['Precio']]
    
    correlacion['Precio'].plot(kind='barh', color=colores, ax=ax)
    ax.set_title("Impacto de cada Variable en el Precio")
    ax.set_xlabel("Impacto Negativo (Baja Precio) <---> Impacto Positivo (Sube Precio)")
    ax.grid(axis='x', linestyle='--')
    
    st.pyplot(fig)
    
    with st.expander("💡 Ayuda para interpretar este gráfico"):
        st.write("""
        - **Barras Verdes:** Indican características que, al aumentar, suelen elevar el precio del auto (como el Año o el tamaño del Motor).
        - **Barras Rojas:** Indican factores que deprecian el valor. Por ejemplo, a mayor Kilometraje, la barra va hacia la izquierda, indicando menor precio.
        """)

    st.divider()
    
    st.subheader("Depreciación según Uso y Antigüedad")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_filtrado, x='Año', y='Precio', hue='Condición', marker='o', ax=ax)
    ax.set_title("Evolución del Precio según el Año de Fabricación")
    ax.set_ylabel("Precio Estimado ($)")
    st.pyplot(fig)

# === PESTAÑA 3: SIMULADOR ===
with tab3:
    st.header("🤖 Herramienta de Tasación")
    st.markdown("Utiliza nuestra base de datos para estimar el valor justo de un vehículo específico.")
    
    col_input1, col_input2, col_input3 = st.columns(3)
    
    with col_input1:
        sim_marca = st.selectbox("Selecciona la Marca", df['Marca'].unique())
    with col_input2:
        modelos_marca = df[df['Marca'] == sim_marca]['Modelo'].unique()
        sim_modelo = st.selectbox("Selecciona el Modelo", modelos_marca)
    with col_input3:
        sim_anio = st.number_input("Año del Vehículo", min_value=int(df['Año'].min()), max_value=int(df['Año'].max()), value=2018)

    # Buscar autos similares
    autos_similares = df[
        (df['Marca'] == sim_marca) & 
        (df['Modelo'] == sim_modelo) & 
        (df['Año'] == sim_anio)
    ]
    
    st.markdown("---")
    
    if not autos_similares.empty:
        precio_estimado = autos_similares['Precio'].mean()
        min_est = autos_similares['Precio'].min()
        max_est = autos_similares['Precio'].max()
        
        st.success(f"### 🏷️ Valor de Mercado Estimado: ${precio_estimado:,.2f}")
        st.write(f"Este cálculo se basa en el análisis de **{len(autos_similares)}** unidades similares encontradas en nuestros registros.")
        
        st.write("Rango de precios observado:")
        st.slider("Variación de mercado", min_value=int(min_est), max_value=int(max_est), value=(int(min_est), int(max_est)), disabled=True)
    else:
        st.warning("⚠️ Lo sentimos, no tenemos suficientes datos históricos para este modelo y año específicos. Te sugerimos probar con un año cercano.")
