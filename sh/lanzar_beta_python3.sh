#!/bin/bash
# ==============================================================================
# Disparador Beta del Sistema QnA
# ==============================================================================

# 1. Parámetros Base
ENV_CODE="010"
INPUT_FILE="Informe Proyecto Bim 1 EDAII.pdf"
ENCODING="utf-8"

# 2. Parámetros de Negocio
TARGET_PROFILE="estudiante universitario"
TOP_N_CONCEPTS="5"      # Define el número de conceptos y preguntas

# 3. Parámetros de Formato (Longitud)
QUESTION_LENGTH="concisas y directas, máximo 15 palabras"
ANSWER_LENGTH="detalladas y analíticas, de al menos dos párrafos"

# 4. Parámetros de Inteligencia Artificial
MODEL_NAME="llama3.1"
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

cd ../Python

python main.py \
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