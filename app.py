import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="Dashboard Pro de Autos",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

sns.set_theme(style="whitegrid")
# Paleta de colores más moderna
COLOR_BARRA = "#2ecc71" # Verde esmeralda para cosas positivas
COLOR_NEGATIVO = "#e74c3c" # Rojo para cosas negativas

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
    st.error("⚠️ Error: Sube el archivo 'car_price_prediction_.csv' a GitHub.")
    st.stop()

# --- 3. BARRA LATERAL (FILTROS) ---
with st.sidebar:
    st.header("🎛️ Filtros Globales")
    marcas = sorted(df['Marca'].unique())
    sel_marcas = st.multiselect("Marca:", marcas, default=marcas[:3])
    
    sel_anio = st.slider("Año:", int(df['Año'].min()), int(df['Año'].max()), (2015, 2023))
    
    if not sel_marcas: sel_marcas = marcas # Si no selecciona nada, selecciona todo

# Aplicar filtros
df_filtrado = df[
    (df['Marca'].isin(sel_marcas)) &
    (df['Año'].between(sel_anio[0], sel_anio[1]))
]

# --- 4. TÍTULO ---
st.title("🏎️ Inteligencia de Mercado Automotriz")
st.markdown(f"Analizando **{len(df_filtrado)}** vehículos de las marcas: *{', '.join(sel_marcas[:5])}*...")
st.markdown("---")

# --- 5. PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["📊 Panorama General", "🧠 Inteligencia de Precios", "💰 Simulador de Valor"])

# === PESTAÑA 1: PANORAMA ===
with tab1:
    # KPIs Estilizados
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Precio Promedio", f"${df_filtrado['Precio'].mean():,.0f}")
    col2.metric("🛣️ Kilometraje Promedio", f"{df_filtrado['Kilometraje'].mean():,.0f} km")
    col3.metric("📅 Antigüedad Promedio", f"{2024 - df_filtrado['Año'].mean():.1f} años")
    col4.metric("🚘 Total Autos", len(df_filtrado))

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribución de Precios")
        fig, ax = plt.subplots(figsize=(10, 6))
        # Histograma con curva de densidad
        sns.histplot(df_filtrado['Precio'], kde=True, color="skyblue", element="step", ax=ax)
        ax.set_title("¿Cuál es el rango de precios más común?")
        ax.set_xlabel("Precio ($)")
        st.pyplot(fig)

    with c2:
        st.subheader("Autos por Condición")
        # Gráfico de Pastel (Donut Chart)
        conteo = df_filtrado['Condición'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(conteo, labels=conteo.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
        # Círculo blanco en el medio para hacerlo dona
        circulo = plt.Circle((0,0), 0.70, fc='white')
        fig.gca().add_artist(circulo)
        st.pyplot(fig)

# === PESTAÑA 2: INTELIGENCIA (EL REEMPLAZO DEL HEATMAP) ===
with tab2:
    st.subheader("¿Qué influye realmente en el precio?")
    st.write("Este gráfico muestra qué características hacen que un auto sea más caro (derecha) o más barato (izquierda).")

    # Calculamos la correlación solo con el Precio
    # Seleccionamos solo columnas numéricas
    cols_numericas = df_filtrado.select_dtypes(include=['number'])
    correlacion = cols_numericas.corr()[['Precio']].sort_values(by='Precio', ascending=False)
    
    # Quitamos la fila de "Precio" porque la correlación con uno mismo siempre es 1
    correlacion = correlacion.drop('Precio')

    # Gráfico de Barras Horizontal
    fig, ax = plt.subplots(figsize=(10, 5))
    # Colores: Verde si es positivo, Rojo si es negativo
    colores = [COLOR_BARRA if x > 0 else COLOR_NEGATIVO for x in correlacion['Precio']]
    
    correlacion['Precio'].plot(kind='barh', color=colores, ax=ax)
    ax.set_title("Correlación con el Precio")
    ax.set_xlabel("Impacto (Negativo < 0 < Positivo)")
    ax.grid(axis='x', linestyle='--')
    
    st.pyplot(fig)
    
    with st.expander("💡 ¿Cómo leer este gráfico?"):
        st.write("""
        - **Barras Verdes (Derecha):** Si estas suben, el precio sube. (Ej: Año, Motor).
        - **Barras Rojas (Izquierda):** Si estas suben, el precio BAJA. (Ej: Kilometraje).
        """)

    st.divider()
    
    st.subheader("Evolución de Precio por Año y Condición")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_filtrado, x='Año', y='Precio', hue='Condición', marker='o', ax=ax)
    ax.set_title("¿Cuánto se deprecia un auto usado vs. uno nuevo?")
    st.pyplot(fig)

# === PESTAÑA 3: SIMULADOR (NUEVO) ===
with tab3:
    st.header("🤖 Calculadora de Precio Estimado")
    st.markdown("Selecciona las características de un vehículo para estimar su valor de mercado basado en nuestros datos.")
    
    col_input1, col_input2, col_input3 = st.columns(3)
    
    with col_input1:
        sim_marca = st.selectbox("Marca", df['Marca'].unique())
    with col_input2:
        # Filtramos modelos según la marca seleccionada
        modelos_marca = df[df['Marca'] == sim_marca]['Modelo'].unique()
        sim_modelo = st.selectbox("Modelo", modelos_marca)
    with col_input3:
        sim_anio = st.number_input("Año", min_value=int(df['Año'].min()), max_value=int(df['Año'].max()), value=2018)

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
        
        st.success(f"### 🏷️ Precio Estimado: ${precio_estimado:,.2f}")
        st.write(f"Basado en {len(autos_similares)} vehículos similares en nuestra base de datos.")
        
        # Barra de progreso visual para ver dónde cae el precio
        st.write("Rango de precios encontrado:")
        st.slider("Rango real en mercado", min_value=int(min_est), max_value=int(max_est), value=(int(min_est), int(max_est)), disabled=True)
    else:
        st.warning("⚠️ No tenemos suficientes datos de este modelo y año exactos para estimar un precio. Prueba con otro año.")
