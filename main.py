import streamlit as st
import requests
import zipfile
import io
import pandas as pd

# Título de la aplicación
st.title("Análisis de Delitos en la ZMG")
st.subheader("Por Miguel Vizcaíno")

#------------------------ INTRODUCCIÓN --------------------------------

# Descripción
st.write("Empezamos descargando el Data Set de la página oficial del IIEE (Instituto de Información Estadística y Geográfica)")
st.write("Fuente: https://iieg.gob.mx/ns/wp-content/uploads/2024/09/Centro_agosto24.zip")
st.write("Se hace una limpieza de los datos, resultando en el siguinte Data Set")

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
        #st.dataframe(df.head())  # Muestra el DataFrame de forma interactiva en la página
else:
    st.error(f"Error al descargar el archivo ZIP: {response.status_code}")

#------------------------ PREPROCESAMIENTO DEL DATASET --------------------------------
# Diccionario de coordenadas por municipio
coordenadas = {
    'Tonalá': (20.6167, -103.233),
    'Tlajomulco de Zúñiga': (20.4667, -103.433),
    'Guadalajara': (20.6767, -103.3475),
    'El Salto': (20.5219, -103.2176),
    'San Pedro Tlaquepaque': (20.6408, -103.2938),
    'Ixtlahuacán de los Membrillos': (20.3636, -103.2167),
    'Zapotlanejo': (20.6189, -103.0816),
    'Zapopan': (20.728, -103.4347),
    'Ixtlahuacán del Río': (20.834, -103.207),
    'Juanacatlán': (20.5167, -103.1667),
    'San Cristobal de la Barranca': (21.0241, -103.4644),
    'Cuquío': (20.7467, -103.0648),
}

# Añadir coordenadas al DataFrame
df['x'] = df['municipio'].map(lambda municipio: coordenadas.get(municipio, (None, None))[0])
df['y'] = df['municipio'].map(lambda municipio: coordenadas.get(municipio, (None, None))[1])

st.dataframe(df.head())  # Muestra el DataFrame de forma interactiva en la página