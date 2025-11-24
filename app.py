import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Profesional de Autos",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo profesional para gráficos
sns.set_theme(style="whitegrid")

# --- CARGA DE DATOS ---
try:
    df = pd.read_csv('car_price_prediction_.csv')
except FileNotFoundError:
    st.error("⚠️ Error Crítico: No se encuentra el archivo 'car_price_prediction_.csv'.")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3774/3774278.png", width=100)
st.sidebar.title("Filtros Avanzados")
st.sidebar.markdown("---")

# 1. Filtro Marcas
marcas = sorted(df['Brand'].unique())
sel_marcas = st.sidebar.multiselect("Seleccionar Marca:", marcas, default=marcas[:5])

# 2. Filtro Año
min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
sel_year = st.sidebar.slider("Rango de Años:", min_year, max_year, (2010, max_year))

# 3. Filtro Precio
min_price, max_price = int(df['Price'].min()), int(df['Price'].max())
sel_price = st.sidebar.slider("Rango de Precio ($):", min_price, max_price, (min_price, max_price))

# Aplicar filtros
df_filtered = df[
    (df['Brand'].isin(sel_marcas)) &
    (df['Year'].between(sel_year[0], sel_year[1])) &
    (df['Price'].between(sel_price[0], sel_price[1]))
]

# --- ESTRUCTURA DE PESTAÑAS ---
st.title("🏎️ Análisis Estratégico de Vehículos")
st.markdown("Dashboard interactivo para la toma de decisiones basada en datos.")

tab1, tab2, tab3 = st.tabs(["📊 Visión General", "📈 Análisis Avanzado", "📂 Datos y Descarga"])

# === PESTAÑA 1: VISIÓN GENERAL ===
with tab1:
    # KPIs
    st.markdown("### Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Vehículos", len(df_filtered))
    col2.metric("Precio Promedio", f"${df_filtered['Price'].mean():,.0f}")
    col3.metric("Kilometraje Promedio", f"{df_filtered['Mileage'].mean():,.0f} km")
    col4.metric("Modelo más Reciente", df_filtered['Year'].max())
    
    st.divider()

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Distribución de Precios")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(df_filtered['Price'], kde=True, color="skyblue", ax=ax)
        ax.set_title("Histograma de Precios")
        st.pyplot(fig)
        
    with c2:
        st.subheader("Top 5 Marcas más Caras (Promedio)")
        top_marcas = df_filtered.groupby('Brand')['Price'].mean().sort_values(ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top_marcas.values, y=top_marcas.index, palette="viridis", ax=ax)
        ax.set_xlabel("Precio Promedio ($)")
        st.pyplot(fig)

# === PESTAÑA 2: ANÁLISIS AVANZADO ===
with tab2:
    st.header("Análisis Estadístico y Correlaciones")
    
    c3, c4 = st.columns([2, 1])
    
    with c3:
        st.markdown("#### Relación: Precio vs Kilometraje vs Condición")
        # Scatterplot avanzado con Seaborn
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df_filtered, x='Kilometraje', y='Precio', hue='Condicion', style='Condicion', s=100, alpha=0.7, ax=ax)
        ax.set_title("Impacto del Uso en el Precio")
        st.pyplot(fig)
        
    with c4:
        st.markdown("#### Matriz de Correlación")
        st.caption("¿Qué variables están conectadas? (Rojo = Alta conexión)")
        # Seleccionar solo columnas numéricas para correlación
        numeric_df = df_filtered.select_dtypes(include=['float64', 'int64'])
        corr = numeric_df.corr()
        
        fig, ax = plt.subplots(figsize=(5, 5))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax, cbar=False)
        st.pyplot(fig)

    st.divider()
    
    st.markdown("#### Comparativa de Precios por Tipo de Combustible (Boxplot)")
    st.caption("La línea dentro de la caja es la mediana. Los puntos son valores atípicos.")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=df_filtered, x='Tipo de Combustible', y='Precio', palette="Set3", ax=ax)
    st.pyplot(fig)

# === PESTAÑA 3: DATOS Y DESCARGA ===
with tab3:
    st.header("Base de Datos Filtrada")
    st.write(f"Mostrando {len(df_filtered)} registros según tus filtros.")
    
    # Mostrar tabla
    st.dataframe(df_filtered, use_container_width=True)
    
    # Botón de Descarga
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados en CSV",
        data=csv,
        file_name='reporte_autos_filtrado.csv',
        mime='text/csv',
    )
