import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import zipfile
import io

# Configuración de la página
st.set_page_config(page_title="Análisis de Delitos", layout="wide")

# Título de la aplicación
st.title("Análisis de Delitos en la ZMG")
st.subheader("Por Miguel Vizcaíno")

#------------------------ INTRODUCCIÓN --------------------------------

# Descripción
st.write("Empezamos descargando el Data Set de la página oficial del IIEE (Instituto de Información Estadística y Geográfica)")
st.write("Fuente: https://iieg.gob.mx/ns/wp-content/uploads/2024/09/Centro_agosto24.zip")
st.write("El Data Set seleccionado presenta los siguientes problemas:")
st.write("  - No todas las colonias de cada delito están registradas")
st.write("  - No todas las ubicaciones de cada delito están registradas")
st.write("  - No todos los registros de la hora están registrados o se encuentrean escritos correctamente")
st.write("Para poder trabajar con los datos se obtuvieron 4 dataframes distintos. En todos se descartaron datos que no son reelevantes para nuestro análisis, como el ID de cada municipio, y la zona geográfica dentro del Estado ")
st.write("  - df: Dataframe de la tabla original con todos los registros")
st.write("  - df_hour: Dataframe con todos los registros que tienen hora correcta")
st.write("  - df_loc: Dataframe con todos los registros que tienen ubicación registrada")
st.write("  - df_clean: Dataframe con todos los registros con hora y ubicación correctas")
st.write("A continuación se presenta el head del Dataframe limpio (df_clean)")

# URL del archivo ZIP
url = "https://iieg.gob.mx/ns/wp-content/uploads/2024/09/Centro_agosto24.zip"

# Descargar el archivo ZIP desde el enlace
response = requests.get(url)
if response.status_code == 200:
    #st.success("Archivo ZIP descargado exitosamente.")

    # Abrir el archivo ZIP en memoria
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Listar los archivos dentro del ZIP
        #st.write("Archivos dentro del ZIP:", z.namelist())

        # Tomar el primer archivo CSV dentro del ZIP
        csv_filename = z.namelist()[0]
        #st.write(f"Abrir archivo CSV: {csv_filename}")

        # Leer el archivo CSV en un DataFrame de pandas
        with z.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)

        # Mostrar las primeras filas del DataFrame
        st.dataframe(df.head())  # Muestra el DataFrame de forma interactiva en la página
else:
    st.error(f"Error al descargar el archivo ZIP: {response.status_code}")

#------------------------ PREPROCESAMIENTO DEL DATASET --------------------------------
# --- Se eliminan los campos que no aportan información relevante
df = df.drop(columns = ['clave_mun', 'zona_geografica'])

# --- DataFrame - Hora
# Hacemos una copia de df para tener un dataframe con datos limpios de hora
df_hour = df.copy()
# Filtrar las filas donde el formato de la columna 'hora' sea compatible con '%H:%M'
df_hour['hora_valida'] = pd.to_datetime(df_hour['hora'], format='%H:%M', errors='coerce').notna()
# Cuenta los registros True y False
counts = df_hour['hora_valida'].value_counts()
# Mantener solo las filas válidas y eliminar la columna auxiliar
df_hour = df_hour[df_hour['hora_valida']].drop(columns=['hora_valida'])

# --- DataFrame - Loc
# Hacemos una copia de df para tener un dataframe con datos limpios de colonia
df_loc = df.copy()
df_loc = df_loc[df_loc['colonia'] != 'NO DISPONIBLE']

# --- DataFrame - Clean
# Hacemos una copia de df_hour para tener un dataframe con datos limpios de hora y colonia
df_clean = df_hour.copy()
df_clean = df_clean[df_clean['colonia'] != 'NO DISPONIBLE']

# -------------------- TIPO DE DELITO ------------------------------
st.title("1. Análisis de Tipos de Delitos")
st.subheader("1.1 Distribución de los tipos de delito")
# Agrupar por 'delito' y contar las ocurrencias
delitos_count = df['delito'].value_counts().reset_index()
delitos_count.columns = ['delito', 'count']  # Renombrar columnas para claridad

# Calcular el porcentaje de cada delito
delitos_count['percentage'] = (delitos_count['count'] / delitos_count['count'].sum()) * 100

# Crear la gráfica de pie con Plotly
fig = px.pie(
    delitos_count,
    values='percentage',
    names='delito',
    title='Porcentaje de cada Delito',
    labels={'delito': 'Delito', 'percentage': 'Porcentaje'},
    hover_data=['count'],  # Mostrar el conteo al pasar el mouse
)

# Mostrar la gráfica en Streamlit
import streamlit as st
st.plotly_chart(fig)

# Mostrar los datos en una tabla interactiva
st.subheader("Datos resumidos")
st.dataframe(delitos_count, use_container_width=True)