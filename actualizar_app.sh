#!/bin/bash

# Paso 1: Verificar el estado de Git y agregar todos los cambios
echo "Verificando el estado de los cambios..."
git status

echo "Agregando los cambios al área de preparación..."
git add .

# Paso 2: Hacer commit con un mensaje
echo "Realizando el commit..."
git commit -m "Actualización de la aplicación"

# Paso 3: Subir los cambios a GitHub
echo "Subiendo los cambios a GitHub..."
git push origin master  # O usa tu rama, por ejemplo, git push origin main

# Paso 4: Notificar al usuario
echo "Los cambios se han subido correctamente a GitHub."

# Paso 5: Fin
echo "¡Listo! La aplicación debería actualizarse en Streamlit Cloud en pocos minutos."
