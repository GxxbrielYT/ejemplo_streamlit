import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tablero de Autos",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual limpio
sns.set_theme(style="whitegrid")

# --- CARGA Y TRADUCCIÓN DE DATOS ---
try:
    df = pd.read_csv('car_price_prediction_.csv')
    
    # TRADUCCIÓN DE COLUMNAS (Para que todo se vea en español)
    df.rename(columns={
        'Brand': 'Marca',
        'Year': 'Año',
        'Engine Size': 'Motor (L)',
        'Fuel Type': 'Combustible',
        'Transmission': 'Transmisión',
        'Mileage': 'Kilometraje',
        'Condition': 'Condición',
        'Price': 'Precio',
        'Model': 'Modelo',
        'Car ID': 'ID'
    }, inplace=True)
    
except FileNotFoundError:
    st.error("⚠️ Error: No se encuentra el archivo 'car_price_prediction_.csv'.")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("🔍 Filtros")
st.sidebar.markdown("---")

# 1. Filtro Marca
marcas = sorted(df['Marca'].unique())
sel_marcas = st.sidebar.multiselect("Seleccionar Marca:", marcas, default=marcas[:5])

# 2. Filtro Año
min_year, max_year = int(df['Año'].min()), int(df['Año'].max())
sel_year = st.sidebar.slider("Rango de Años:", min_year, max_year, (2015, max_year))

# 3. Filtro Precio
min_price, max_price = int(df['Precio'].min()), int(df['Precio'].max())
sel_price = st.sidebar.slider("Rango de Precio ($):", min_price, max_price, (min_price, max_price))

# Aplicar filtros
df_filtrado = df[
    (df['Marca'].isin(sel_marcas)) &
    (df['Año'].between(sel_year[0], sel_year[1])) &
    (df['Precio'].between(sel_price[0], sel_price[1]))
]

# --- ESTRUCTURA DE PESTAÑAS ---
st.title("🚗 Análisis de Vehículos")
st.markdown("Explora las tendencias del mercado automotriz.")

tab1, tab2, tab3 = st.tabs(["📊 Resumen", "📈 Análisis Detallado", "📂 Datos"])

# === PESTAÑA 1: RESUMEN ===
with tab1:
    # Métricas grandes
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Autos", len(df_filtrado))
    col2.metric("Precio Promedio", f"${df_filtrado['Precio'].mean():,.0f}")
    col3.metric("Km Promedio", f"{df_filtrado['Kilometraje'].mean():,.0f} km")
    col4.metric("Año Más Reciente", df_filtrado['Año'].max())
    
    st.divider()

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Distribución de Precios")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(df_filtrado['Precio'], kde=True, color="skyblue", ax=ax)
        ax.set_xlabel("Precio ($)")
        ax.set_ylabel("Cantidad de Autos")
        ax.set_title("¿Cuánto cuestan la mayoría de los autos?")
        st.pyplot(fig)
        
    with c2:
        st.subheader("Marcas más Caras")
        top_marcas = df_filtrado.groupby('Marca')['Precio'].mean().sort_values(ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=top_marcas.values, y=top_marcas.index, palette="viridis", ax=ax)
        ax.set_xlabel("Precio Promedio ($)")
        ax.set_ylabel("Marca")
        ax.set_title("Top 5 Marcas por Precio Promedio")
        st.pyplot(fig)

# === PESTAÑA 2: ANÁLISIS DETALLADO ===
with tab2:
    st.header("Relaciones y Tendencias")
    
    c3, c4 = st.columns([2, 1])
    
    with c3:
        st.markdown("#### Precio vs. Kilometraje y Condición")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=df_filtrado, 
            x='Kilometraje', 
            y='Precio', 
            hue='Condición', 
            style='Condición', 
            s=100, 
            alpha=0.7, 
            ax=ax
        )
        ax.set_title("Relación: Kilometraje vs Precio")
        ax.set_xlabel("Kilometraje (km)")
        ax.set_ylabel("Precio ($)")
        # Mover la leyenda para que no estorbe
        sns.move_legend(ax, "upper right")
        st.pyplot(fig)
        
    with c4:
        st.markdown("#### Matriz de Correlación")
        st.caption("Rojo intenso = Fuerte relación positiva. Azul = Relación negativa.")
        # Seleccionar solo columnas numéricas
        cols_numericas = df_filtrado.select_dtypes(include=['float64', 'int64'])
        corr = cols_numericas.corr()
        
        fig, ax = plt.subplots(figsize=(6, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax, cbar=False, annot_kws={"size": 10})
        st.pyplot(fig)

    st.divider()
    
    st.markdown("#### Precios según el Tipo de Combustible")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=df_filtrado, x='Combustible', y='Precio', palette="Set3", ax=ax)
    ax.set_title("Distribución de Precios por Combustible")
    ax.set_xlabel("Tipo de Combustible")
    ax.set_ylabel("Precio ($)")
    st.pyplot(fig)

# === PESTAÑA 3: DATOS ===
with tab3:
    st.header("Base de Datos Filtrada")
    st.write(f"Mostrando {len(df_filtrado)} registros.")
    
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botón de Descarga
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar tabla en Excel (CSV)",
        data=csv,
        file_name='reporte_autos.csv',
        mime='text/csv',
    )
