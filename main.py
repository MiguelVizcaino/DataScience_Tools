import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import zipfile
import io
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import cm

# Configuración de la página
st.set_page_config(page_title="Análisis de Delitos", layout="wide")

# Título de la aplicación
st.title("Análisis de Delitos en Jalisco")
st.subheader("Por Miguel Vizcaíno")

#------------------------ INTRODUCCIÓN --------------------------------

# Descripción
st.write("Empezamos descargando el Dataset de cada zona de Jalisco de la página oficial del IIEE (Instituto de Información Estadística y Geográfica)")
st.write("Fuente: https://iieg.gob.mx/ns/?page_id=31143")
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

# Diccionario de nombres y URLs correspondientes
urls = {
    "Altos Norte": "https://iieg.gob.mx/ns/wp-content/uploads/2024/06/Altos_Norte_mayo24.zip",
    "Altos Sur": "https://iieg.gob.mx/ns/wp-content/uploads/2024/08/Altos_Sur_junio24.zip",
    "Ciénega": "https://iieg.gob.mx/ns/wp-content/uploads/2024/08/Cienega_julio24.zip",
    "Centro": "https://iieg.gob.mx/ns/wp-content/uploads/2024/09/Centro_agosto24.zip",
    "Costa Sur": "https://iieg.gob.mx/ns/wp-content/uploads/2024/10/Costa_Sur_sep24.zip",
    "Costa-Sierra Occidental": "https://iieg.gob.mx/ns/wp-content/uploads/2024/11/Costa_Sierra_Occidental_oct24.zip",
    "Lagunas": "https://iieg.gob.mx/ns/wp-content/uploads/2024/01/Lagunas_nov23.zip",
    "Norte": "https://iieg.gob.mx/ns/wp-content/uploads/2024/01/Norte_diciembre23.zip",
    "Sierra de Amula": "https://iieg.gob.mx/ns/wp-content/uploads/2024/02/Sierra_Amula_ene24.zip",
    "Sur": "https://iieg.gob.mx/ns/wp-content/uploads/2024/05/Sur_feb24.zip",
    "Sureste": "https://iieg.gob.mx/ns/wp-content/uploads/2024/05/Sureste_mar24.zip",
    "Valles": "https://iieg.gob.mx/ns/wp-content/uploads/2024/05/valles_abr24.zip"
}

# Selección del nombre desde el selectbox
selected_region = st.selectbox("Selecciona una región:", list(urls.keys()), index=3)  # 'Centro' es el valor por defecto

# Obtener el URL correspondiente a la región seleccionada
url = urls[selected_region]

# Descargar el archivo ZIP desde el enlace
response = requests.get(url)
if response.status_code == 200:
    # Abrir el archivo ZIP en memoria
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Tomar el primer archivo CSV dentro del ZIP
        csv_filename = z.namelist()[0]
        
        # Leer el archivo CSV en un DataFrame de pandas
        with z.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file)

        # Mostrar las primeras filas del DataFrame
        #st.dataframe(df.head())  # Muestra el DataFrame de forma interactiva en la página
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
# Se asegura que la columna fecha tenga formato datatime
df_hour['fecha'] = pd.to_datetime(df_hour['fecha'])
# Crear la columna 'weekday' con el nombre del día de la semana
df_hour['weekday'] = df_hour['fecha'].dt.day_name()
# Crear la columna 'hora_interval' extrayendo solo la hora
df_hour['hora_interval'] = df_hour['hora'].str.split(':').str[0].astype(int)

# --- DataFrame - Loc
# Hacemos una copia de df para tener un dataframe con datos limpios de colonia
df_loc = df.copy()
df_loc = df_loc[df_loc['colonia'] != 'NO DISPONIBLE']

# --- DataFrame - Clean
# Hacemos una copia de df_hour para tener un dataframe con datos limpios de hora y colonia
df_clean = df_hour.copy()
df_clean = df_clean[df_clean['colonia'] != 'NO DISPONIBLE']
st.dataframe(df_clean.head())
# -------------------- TIPO DE DELITO ------------------------------
st.subheader("1. Análisis de Tipos de Delitos")
st.write("En esta sección se obtendrá información sobre la distribución de los diferentes tipos de delito en función del municipio que se quiera analizar.")
# Crear una lista de municipios únicos y agregar la opción "Total"
municipios = ["Total"] + sorted(df['municipio'].unique())  # Ordenar alfabéticamente y agregar "Total"
# Crear un menú desplegable para seleccionar el municipio
selected_municipio_delitos = st.selectbox(
    "Selecciona un municipio:",
    municipios,
    key="selectbox_municipio_delitos")
# Filtrar los datos según el municipio seleccionado
if selected_municipio_delitos == "Total":
    filtered_df_1 = df  # Usar todos los registros
else:
    filtered_df_1 = df[df['municipio'] == selected_municipio_delitos]
# Calcular el número de semanas entre la primera y última fecha
filtered_df_1['fecha'] = pd.to_datetime(filtered_df_1['fecha'])
num_semanas = ((filtered_df_1['fecha'].max() - filtered_df_1['fecha'].min()).days // 7) + 1
# Agrupar por 'delito' y contar las ocurrencias
delitos_count = filtered_df_1['delito'].value_counts().reset_index()
delitos_count.columns = ['delito', 'count']  # Renombrar columnas para claridad
# Calcular el porcentaje y el conteo semanal
delitos_count['percentage'] = (delitos_count['count'] / delitos_count['count'].sum()) * 100
delitos_count['count_week'] = delitos_count['count'] / num_semanas
# Crear la gráfica de pie con Plotly
fig = px.pie(
    delitos_count,
    values='percentage',
    names='delito',
    title=f"Porcentaje de delitos en {selected_municipio_delitos}",
    labels={'delito': 'Delito', 'percentage': 'Porcentaje'},
    hover_data=['count'],  # Mostrar el conteo al pasar el mouse
)
# Mostrar la gráfica de pie en Streamlit
st.plotly_chart(fig)
# Crear la gráfica de barras horizontales por conteo semanal
barras_fig = px.bar(
    delitos_count.sort_values(by='count_week', ascending=False),
    x='count_week',
    y='delito',
    title=f"Delitos por semana en {selected_municipio_delitos}",
    labels={'count_week': 'Delitos por semana', 'delito': 'Delito'},
    orientation='h',
    color='delito'
)
# Mostrar la gráfica de barras en Streamlit
st.plotly_chart(barras_fig)

#--------------- Animación -------------------

df_rank = filtered_df_1.copy()
df_rank['fecha'] = pd.to_datetime(df_rank['fecha'])  # Convert 'fecha' to datetime
df_rank['mes'] = df_rank['fecha'].dt.month_name()  # Extract the month
df_rank['mes_num'] = df_rank['fecha'].dt.month  # Extract the month as a number

delito_counts = df_rank.groupby(['mes_num', 'delito'])['delito'].count().unstack(fill_value=0)
delito_counts = delito_counts.reset_index()  # Reindex to make 'mes' a regular column

# Ordenar el DataFrame por la columna 'mes'
delito_counts = delito_counts.sort_values('mes_num')

delito_counts_n = delito_counts.copy()
n_inter = 10
delito_counts_n.index = delito_counts_n.index * n_inter
delito_counts_n = delito_counts_n.reindex(range(0, delito_counts_n.index.max() + 1))
delito_counts_n = delito_counts_n.interpolate()

delito_counts_rank = delito_counts.rank(axis=1, ascending=True, method="average")
delito_counts_rank.index = delito_counts_rank.index * n_inter
delito_counts_rank = delito_counts_rank.reindex(range(0, delito_counts_rank.index.max() + 1))
delito_counts_rank = delito_counts_rank.interpolate()

names = delito_counts_rank.columns[1:]
positions = list(range(1, names.size + 1))
x_lim = (0, delito_counts_n[delito_counts_n.mean().idxmax()].max()*1.1)
y_lim = (0, names.size + 2)

fig = plt.figure(figsize=(8, 3))
ax = fig.add_subplot()
ax.set_xlim(x_lim)
ax.set_ylim(y_lim)
ax.set_yticks(positions)


n_frames = len(delito_counts_n)

def animate(i):
    ax.clear()
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    positions = list(range(1, names.size + 1))
    ax.set_yticks(positions)

    values = delito_counts_n.iloc[i]
    positions = delito_counts_rank.iloc[i]

    bars = ax.barh(positions, values, color=colores)

    for bar, value, name in zip(bars, values, names):
        ax.text(bar.get_width() - 5, bar.get_y() + bar.get_height()/2,
                f'{name} - {value:.1f}', va='center', ha='right', fontsize=10, color='white')

    return bars

# Animación con Matplotlib
anim = FuncAnimation(fig, animate, frames=n_frames, interval=100, blit=False)

# Mostrar la animación en Streamlit
st.write("### Animación de los Top 10 Delitos")
st.pyplot(fig)

#--------------- Animación -------------------

# Mostrar la tabla resumida centrada
data_summary = delitos_count[['delito', 'count', 'count_week', 'percentage']]
st.subheader("Datos resumidos")
st.dataframe(data_summary.style.set_properties(**{
    'text-align': 'center'
}).set_table_styles([
    dict(selector='th', props=[('text-align', 'center')])
]))

# -------------------- TIPO DE BIEN AFECTADO ------------------------------
st.subheader("2. Análisis de Tipos de Bien Afectado")
st.write("En esta sección se obtendrá información sobre la distribución de los diferentes bienes que son afectados por cada delito en función del municipio que se quiera analizar.")
# Crear una lista de municipios únicos y agregar la opción "Total"
municipios = ["Total"] + sorted(df['municipio'].unique())  # Ordenar alfabéticamente y agregar "Total"
# Crear un menú desplegable para seleccionar el municipio
selected_municipio_bien = st.selectbox(
    "Selecciona un municipio:",
    municipios,
    key="selectbox_municipio_bienes"
)
# Filtrar los datos según el municipio seleccionado
if selected_municipio_bien == "Total":
    filtered_df_2 = df  # Usar todos los registros
else:
    filtered_df_2 = df[df['municipio'] == selected_municipio_bien]
# Calcular el número de semanas entre la primera y última fecha
filtered_df_2['fecha'] = pd.to_datetime(filtered_df_2['fecha'])
num_semanas = ((filtered_df_2['fecha'].max() - filtered_df_2['fecha'].min()).days // 7) + 1
# Agrupar por 'bien_afectado' y contar las ocurrencias
bienes_count = filtered_df_2['bien_afectado'].value_counts().reset_index()
bienes_count.columns = ['bien_afectado', 'count']  # Renombrar columnas para claridad
# Calcular el porcentaje y el conteo semanal
bienes_count['percentage'] = (bienes_count['count'] / bienes_count['count'].sum()) * 100
bienes_count['count_week'] = bienes_count['count'] / num_semanas
# Crear la gráfica de pie con Plotly
fig = px.pie(
    bienes_count,
    values='percentage',
    names='bien_afectado',
    title=f"Porcentaje de bienes afectados en {selected_municipio_bien}",
    labels={'bien_afectado': 'Bien Afectado', 'percentage': 'Porcentaje'},
    hover_data=['count'],  # Mostrar el conteo al pasar el mouse
)
# Mostrar la gráfica de pie en Streamlit
st.plotly_chart(fig)
# Crear la gráfica de barras horizontales por conteo semanal
barras_fig = px.bar(
    bienes_count.sort_values(by='count_week', ascending=False),
    x='count_week',
    y='bien_afectado',
    title=f"Bienes afectados por semana en {selected_municipio_bien}",
    labels={'count_week': 'Bienes afectados por semana', 'bien_afectado': 'Bien Afectado'},
    orientation='h',
    color='bien_afectado'
)
# Mostrar la gráfica de barras en Streamlit
st.plotly_chart(barras_fig)
# Mostrar la tabla resumida centrada
data_summary = bienes_count[['bien_afectado', 'count', 'count_week', 'percentage']]
st.subheader("Datos resumidos")
st.dataframe(data_summary.style.set_properties(**{
    'text-align': 'center'
}).set_table_styles([
    dict(selector='th', props=[('text-align', 'center')])
]))

# --------------------------- TIEMPO -----------------------------------
st.subheader("3. Análisis de Delitos en el Tiempo")
st.write("En esta sección se obtendrá información sobre la distribución por día de la semana y hora de la cantidad de delitos cometidos del delito seleccionado.")
# Crear una lista de delitos y agregar la opción "Total"
delitos = ["Total"] + sorted(df['delito'].unique())  # Ordenar alfabéticamente y agregar "Total"
# Crear un menú desplegable para seleccionar el delito
selected_delitos_heatmap = st.selectbox(
    "Selecciona un delito:",
    delitos,
    key="delitos_heatmap"
)
# Filtrar los datos según el delito seleccionado
if selected_delitos_heatmap == "Total":
    filtered_df_3 = df_hour  # Usar todos los registros
else:
    filtered_df_3 = df_hour[df_hour['delito'] == selected_delitos_heatmap]
# Agrupar los datos por 'weekday' y 'hora_interval' y contar la cantidad de delitos
heatmap_data = filtered_df_3.groupby(['weekday', 'hora_interval']).size().reset_index(name='conteo')
# Crear el heatmap usando Plotly Express
fig = px.density_heatmap(heatmap_data,
                         x="weekday", 
                         y="hora_interval",
                         nbinsy=12,
                         z="conteo", 
                         color_continuous_scale="reds",  # Paleta de colores rojos
                         title=f"Distribución de delitos semanal: {selected_delitos_heatmap}",
                         labels={"conteo": "Número de Delitos", "hora_interval": "Hora", "weekday": "Día de la Semana"})
# Ajustar el orden de los días de la semana
fig.update_layout(
    yaxis={'title': 'Hora del Día', 'dtick': 2},  # Usar tick cada hora
    xaxis={
        'title': 'Día de la Semana',
        'tickmode': 'array',
        'tickvals': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'ticktext': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
        'categoryorder': 'array',  # Forzar el orden específico
        'categoryarray': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']  # Orden de los días
    }
)
# Mostrar el gráfico interactivo en Streamlit
st.plotly_chart(fig)

# ------------------------- UBICACION -------------------------------
st.subheader("4. Análisis de Tipo de Delito por Ubicación")
st.write("En esta sección se obtendrá información sobre la distribución geográfica por colonias de la cantidad de delitos cometidos del delito seleccionado.")
# Crear lista de delitos únicos y agregar la opción "Todos"
delitos = ["Todos"] + sorted(df_loc['delito'].unique())
# Crear un menú desplegable para seleccionar el tipo de delito
selected_delito = st.selectbox(
    "Selecciona un tipo de delito:",
    delitos,
    key="selectbox_tipo_delito"
)
# Filtrar los datos según el delito seleccionado
if selected_delito == "Todos":
    filtered_df_2 = df_loc
else:
    filtered_df_2 = df_loc[df_loc['delito'] == selected_delito]
# Agrupar por colonia y contar los delitos
colonias_count = filtered_df_2['colonia'].value_counts().reset_index()
colonias_count.columns = ['colonia', 'count']  # Renombrar columnas
# Tomar las primeras 10 colonias con más delitos
top_colonias = colonias_count.head(10)
# Crear la gráfica de barras horizontales
bar_fig = px.bar(
    top_colonias.sort_values(by='count', ascending=True),
    x='count',
    y='colonia',
    title=f"Top 10 colonias con más delitos: {selected_delito}",
    labels={'count': 'Número de delitos', 'colonia': 'Colonia'},
    orientation='h',
    color='count',
    color_continuous_scale='Reds'
)
# Mostrar la gráfica de barras
st.plotly_chart(bar_fig)
# Datos resumidos
st.subheader("Datos resumidos")
st.dataframe(top_colonias.style.set_properties(**{
    'text-align': 'center'
}).set_table_styles([
    dict(selector='th', props=[('text-align', 'center')])
]))
# Mapa de Jalisco
st.subheader("Mapa de las 10 principales colonias con más delitos")
# Filtrar las 10 colonias principales con sus coordenadas
map_data = df_loc[df_loc['colonia'].isin(top_colonias['colonia'])]
map_data = map_data.drop_duplicates(subset=['colonia'])  # Evitar duplicados
# Crear un mapa centrado en Jalisco
m = folium.Map(location=[20.6667, -103.3500], zoom_start=10)
# Agregar marcadores para las colonias principales
marker_cluster = MarkerCluster().add_to(m)
for _, row in map_data.iterrows():
    folium.Marker(
        location=[row['y'], row['x']],
        popup=f"{row['colonia']}<br>Delitos: {top_colonias[top_colonias['colonia'] == row['colonia']]['count'].values[0]}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(marker_cluster)
# Mostrar el mapa en Streamlit
st_map = st_folium(m, width=700, height=500)

# Agregar sección para mostrar/ocultar código fuente
with st.expander("Mostrar código fuente"):
    with open("main.py", "r") as file:
        code = file.read()
    st.code(code, language="python")