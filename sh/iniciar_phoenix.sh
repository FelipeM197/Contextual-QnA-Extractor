#!/bin/bash
# Script para iniciar el servidor de Arize Phoenix de forma automática

# Navegar a la carpeta raíz del proyecto (un nivel arriba de la carpeta sh)
cd "$(dirname "$0")/.." || exit

# Intentar activar el entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "Iniciando servidor Arize Phoenix..."
# Levantar Phoenix en el puerto 6006
px serve || python -m phoenix.server.main serve

