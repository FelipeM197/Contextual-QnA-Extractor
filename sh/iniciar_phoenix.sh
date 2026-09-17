#!/bin/bash
# Script para iniciar el servidor de Arize Phoenix de forma automática

# Navegar a la carpeta raíz del proyecto (un nivel arriba de la carpeta sh)
cd "$(dirname "$0")/.." || exit

# Intentar activar el entorno virtual si existe
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Directorio y archivo de log para esta ejecución (permite diagnosticar
# fallos de arranque incluso si la terminal se cierra).
LOG_DIR="outputs/phoenix-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/phoenix_$(date +%Y%m%d_%H%M%S).log"

echo "============================================="
echo " Iniciando servidor Arize Phoenix..."
echo " URL : http://127.0.0.1:6006"
echo " Log : $LOG_FILE"
echo "============================================="

# Nota: el comando "px" pertenecía a versiones antiguas de arize-phoenix y ya
# no existe en releases recientes (solo quedan los comandos "phoenix" /
# "arize-phoenix"). Se usa directamente el módulo para evitar el intento fallido.
python -m phoenix.server.main serve 2>&1 | tee "$LOG_FILE"
exit_code=${PIPESTATUS[0]}

if [ "$exit_code" -ne 0 ]; then
    echo ""
    echo "============================================="
    echo " Phoenix terminó con código de error: $exit_code"
    echo " Revisa el log completo en: $LOG_FILE"
    echo "============================================="
    read -n 1 -s -r -p "Presiona cualquier tecla para cerrar..."
fi
