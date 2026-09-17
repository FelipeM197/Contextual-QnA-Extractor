#!/bin/bash
# ==============================================================================
# Disparador Beta del Sistema QnA
# ==============================================================================

# 1. Parámetros Base
ENV_CODE="010"
INPUT_FILE="${1:-Informe Proyecto Bim 1 EDAII.pdf}"
ENCODING="utf-8"

# 2. Parámetros de Negocio
TARGET_PROFILE="${2:-estudiante universitario}"
TOP_N_CONCEPTS="${4:-5}"      # Define el número de conceptos y preguntas

# 3. Parámetros de Formato (Longitud)
QUESTION_LENGTH="concisas y directas, máximo 15 palabras"
ANSWER_LENGTH="detalladas y analíticas, de al menos dos párrafos"

# 4. Parámetros de Inteligencia Artificial
MODEL_NAME="${3:-llama3.1}"
TEMPERATURE="0"
EMBEDDING_MODEL="all-MiniLM-L6-v2"
TOP_K_CHUNKS="3"

# --- FIN DE LA CONFIGURACIÓN ---

echo "============================================="
echo " Iniciando Sistema QnA - Entorno Beta: $ENV_CODE"
echo "============================================="
echo " Archivo Input : $INPUT_FILE"
echo " Perfil        : $TARGET_PROFILE"
echo " Preguntas     : $TOP_N_CONCEPTS ($QUESTION_LENGTH)"
echo " Respuestas    : $ANSWER_LENGTH"
echo " Modelo LLM    : $MODEL_NAME (Temp: $TEMPERATURE)"
echo "============================================="

export PYTHONUNBUFFERED=1

# Ir a la carpeta del motor Python
cd "$(dirname "$0")/../Python" || cd ../Python

# Detectar intérprete Python (priorizando el entorno virtual local .venv)
if [ -f "../.venv/Scripts/python.exe" ]; then
    PYTHON_CMD="../.venv/Scripts/python.exe"
elif [ -f "../.venv/bin/python" ]; then
    PYTHON_CMD="../.venv/bin/python"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
else
    echo "Error: No se encontró intérprete de Python."
    exit 1
fi

"$PYTHON_CMD" main.py \
  --env "$ENV_CODE" \
  --input "$INPUT_FILE" \
  --encoding "$ENCODING" \
  --perfil "$TARGET_PROFILE" \
  --top_n "$TOP_N_CONCEPTS" \
  --q_len "$QUESTION_LENGTH" \
  --a_len "$ANSWER_LENGTH" \
  --modelo "$MODEL_NAME" \
  --temperatura "$TEMPERATURE" \
  --embedding "$EMBEDDING_MODEL" \
  --top_k "$TOP_K_CHUNKS"
