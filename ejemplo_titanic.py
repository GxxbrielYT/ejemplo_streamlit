import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carga el archivo CSV "database_titanic.csv" en un DataFrame de pandas.
try:
    df = pd.read_csv("database_titanic.csv")
except FileNotFoundError:
    st.error("Error: El archivo 'database_titanic.csv' no se encontró.")
    st.write("Asegúrate de que 'database_titanic.csv' esté en tu repositorio de GitHub.")
    st.stop() # Detiene la ejecución si no se encuentra el archivo

# Muestra un título y una descripción en la aplicación Streamlit.
st.write("""
# Mi primera aplicación interactiva
## Gráficos usando la base de datos del Titanic
""")

# Usando la notación "with" para crear una barra lateral en la aplicación Streamlit.
with st.sidebar:
    # Título para la sección de opciones en la barra lateral.
    st.write("# Opciones")
    
    # Crea un control deslizante (slider) para el número de bins del histograma
    # Ajustamos el rango para que sea más útil (ej. 5 a 50)
    div = st.slider('Número de bins para Edad:', 5, 50, 10)
    
    # Muestra el valor actual del slider en la barra lateral.
    st.write("Bins=", div)

# --- Creación de los 3 Gráficos ---

# Desplegamos 3 gráficos en una fila (1 fila, 3 columnas)
# Ajustamos el tamaño de la figura (figsize) para que quepan bien
fig, ax = plt.subplots(1, 3, figsize=(18, 5))

# --- Gráfico 1: Histograma de Edades (Gráfico existente) ---
# Usamos ax[0] para el primer gráfico
ax[0].hist(df["Age"], bins=div)
ax[0].set_xlabel("Edad")
ax[0].set_ylabel("Frecuencia")
ax[0].set_title("Histograma de edades")

# --- Gráfico 2: Distribución por Sexo (Gráfico existente) ---
# Usamos ax[1] para el segundo gráfico
df_male = df[df["Sex"] == "male"]
cant_male = len(df_male)
df_female = df[df["Sex"] == "female"]
cant_female = len(df_female)

ax[1].bar(["Masculino", "Femenino"], [cant_male, cant_female], color = "red")
ax[1].set_xlabel("Sexo")
ax[1].set_ylabel("Cantidad")
ax[1].set_title('Distribución de hombres y mujeres')

# --- Gráfico 3: Distribución por Clase (NUEVO GRÁFICO) ---
# Usamos ax[2] para el tercer gráfico
# Verificamos si la columna 'Pclass' existe
if 'Pclass' in df.columns:
    # Contamos cuántas personas hay en cada clase
    pclass_counts = df['Pclass'].value_counts().sort_index()
    
    # Creamos etiquetas personalizadas (ej. "Clase 1", "Clase 2")
    labels = [f'Clase {i}' for i in pclass_counts.index]
    
    # Creamos el gráfico de pastel
    ax[2].pie(pclass_counts.values, 
              labels=labels, 
              autopct='%1.1f%%', # Muestra porcentajes
              startangle=90, # Ángulo de inicio
              colors=['gold', 'lightskyblue', 'lightcoral']) # Colores
    
    ax[2].axis('equal')  # Asegura que el gráfico sea un círculo
    ax[2].set_title('Distribución de Pasajeros por Clase')
else:
    # Si 'Pclass' no existe, muestra un mensaje de error en el gráfico
    ax[2].text(0.5, 0.5, 'Columna "Pclass" no encontrada', 
               horizontalalignment='center', 
               verticalalignment='center', 
               transform=ax[2].transAxes, 
               color='red')
    ax[2].set_title('Error de Datos')


# --- Fin de Gráficos ---

# Desplegamos la figura completa (que ahora contiene los 3 gráficos)
st.pyplot(fig)

st.write("""
## Muestra de datos cargados
""")
# Graficamos una tabla
st.table(df.head())
