import streamlit as st
import requests
import zipfile
import io
import pandas as pd

# Título de la aplicación
st.title("Análisis de Datos de Centro Agosto 24")

# Descripción
st.write("Este es un ejemplo de cómo descargar un archivo ZIP, extraerlo y visualizar los primeros registros de un archivo CSV dentro del ZIP.")

# URL del archivo ZIP
url = "https://iieg.gob.mx/ns/wp-content/uploads/2024/09/Centro_agosto24.zip"

# Descargar el archivo ZIP desde el enlace
response = requests.get(url)
if response.status_code == 200:
    st.success("Archivo ZIP descargado exitosamente.")

    # Abrir el archivo ZIP en memoria
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Listar los archivos dentro del ZIP
        st.write("Archivos dentro del ZIP:", z.namelist())

        # Tomar el primer archivo CSV dentro del ZIP
        csv_filename = z.namelist()[0]
        st.write(f"Abrir archivo CSV: {csv_filename}")

        # Leer el archivo CSV en un DataFrame de pandas
        with z.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)

        # Mostrar las primeras filas del DataFrame
        st.write("Primeras filas del DataFrame:")
        st.dataframe(df.head())  # Muestra el DataFrame de forma interactiva en la página
else:
    st.error(f"Error al descargar el archivo ZIP: {response.status_code}")
