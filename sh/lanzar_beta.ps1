# ==============================================================================
# Disparador Beta del Sistema QnA (PowerShell nativo para Windows)
# ==============================================================================

$ENV_CODE = "010"
$INPUT_FILE = "Informe Proyecto Bim 1 EDAII.pdf"
$ENCODING = "utf-8"

$TARGET_PROFILE = "estudiante universitario"
$TOP_N_CONCEPTS = 5

$QUESTION_LENGTH = "concisas y directas, máximo 15 palabras"
$ANSWER_LENGTH = "detalladas y analíticas, de al menos dos párrafos"

$MODEL_NAME = "llama3.1"
$TEMPERATURE = 0
$EMBEDDING_MODEL = "all-MiniLM-L6-v2"
$TOP_K_CHUNKS = 3

Write-Host "============================================="
Write-Host " Iniciando Sistema QnA - Entorno Beta: $ENV_CODE"
Write-Host "============================================="
Write-Host " Archivo Input : $INPUT_FILE"
Write-Host " Perfil        : $TARGET_PROFILE"
Write-Host " Preguntas     : $TOP_N_CONCEPTS ($QUESTION_LENGTH)"
Write-Host " Respuestas    : $ANSWER_LENGTH"
Write-Host " Modelo LLM    : $MODEL_NAME (Temp: $TEMPERATURE)"
Write-Host "============================================="

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path "$ScriptDir\..").Path
$PythonDir = Join-Path $ProjectRoot "Python"

$PythonCmd = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonCmd)) {
    $PythonCmd = "python"
}

Push-Location $PythonDir
try {
    & $PythonCmd main.py `
        --env $ENV_CODE `
        --input $INPUT_FILE `
        --encoding $ENCODING `
        --perfil $TARGET_PROFILE `
        --top_n $TOP_N_CONCEPTS `
        --q_len $QUESTION_LENGTH `
        --a_len $ANSWER_LENGTH `
        --modelo $MODEL_NAME `
        --temperatura $TEMPERATURE `
        --embedding $EMBEDDING_MODEL `
        --top_k $TOP_K_CHUNKS
}
finally {
    Pop-Location
}
