# Guia de cambio de rutas en Windows y Linux

El proyecto centraliza las rutas en `Python/config.py`. No es necesario editar los archivos Python para mover las carpetas: basta con definir variables de entorno antes de iniciar la aplicacion.

## 1. Rutas predeterminadas

Si no se define ninguna variable, el proyecto utiliza esta estructura:

```text
Contextual-QnA-Extractor/
|-- inputs/
|-- outputs/
|   |-- processed/
|   `-- cuestionarios-logs/
|-- prompts/
|-- train-v2.0.json
|-- ollama_models/
`-- huggingface_cache/
```

La raiz del proyecto se detecta automaticamente a partir de `Python/config.py`, aunque el comando se ejecute desde la raiz, `Python/` o `sh/`.

## 2. Variables disponibles

| Variable | Funcion | Valor predeterminado |
|---|---|---|
| `CONTEXTUAL_QNA_PROJECT_DIR` | Define otra raiz del proyecto | Raiz detectada automaticamente |
| `CONTEXTUAL_QNA_INPUTS_DIR` | Documentos originales de entrada | `inputs` |
| `CONTEXTUAL_QNA_OUTPUTS_DIR` | Carpeta general de resultados | `outputs` |
| `CONTEXTUAL_QNA_PROCESSED_DIR` | Markdown convertido y bases DuckDB | `outputs/processed` |
| `CONTEXTUAL_QNA_LOGS_DIR` | Cuestionarios y logs | `outputs/cuestionarios-logs` |
| `CONTEXTUAL_QNA_PROMPTS_DIR` | Prompts de los agentes | `prompts` |
| `CONTEXTUAL_QNA_SQUAD_DATASET` | Dataset SQuAD original | `train-v2.0.json` |
| `CONTEXTUAL_QNA_SQUAD_SAMPLES_DIR` | Contextos SQuAD exportados | `inputs/squad_samples` |
| `OLLAMA_MODELS` | Modelos locales de Ollama | `ollama_models` |
| `HF_HOME` | Cache de Hugging Face y embeddings | `huggingface_cache` |

Las rutas relativas se interpretan respecto a `CONTEXTUAL_QNA_PROJECT_DIR`. Se recomienda usar rutas absolutas cuando las carpetas esten fuera del repositorio.

## 3. Windows

### 3.1 Cambio temporal en PowerShell

Este cambio se mantiene mientras la ventana de PowerShell permanezca abierta.

```powershell
cd "D:\Proyectos\Contextual-QnA-Extractor"

$env:CONTEXTUAL_QNA_INPUTS_DIR = "D:\Datos\QnA\entradas"
$env:CONTEXTUAL_QNA_OUTPUTS_DIR = "D:\Datos\QnA\salidas"
$env:CONTEXTUAL_QNA_PROCESSED_DIR = "D:\Datos\QnA\procesados"
$env:CONTEXTUAL_QNA_LOGS_DIR = "D:\Datos\QnA\logs"
$env:CONTEXTUAL_QNA_PROMPTS_DIR = "D:\Proyectos\Contextual-QnA-Extractor\prompts"
$env:CONTEXTUAL_QNA_SQUAD_DATASET = "D:\Datos\QnA\train-v2.0.json"
$env:OLLAMA_MODELS = "D:\Ollama_Modelos"
$env:HF_HOME = "D:\Datos\QnA\huggingface_cache"
```

Despues, inicia Ollama en esa misma configuracion y ejecuta el proyecto:

```powershell
ollama serve
```

En otra ventana de PowerShell, vuelve a definir `OLLAMA_MODELS` si es necesario y ejecuta:

```powershell
cd "D:\Proyectos\Contextual-QnA-Extractor"
python Python\main.py --input "documento.pdf" --perfil "estudiante universitario" --modelo "llama3.1" --top_n 5
```

Tambien puedes iniciar las interfaces:

```powershell
streamlit run Python\web_app.py
python Python\gui_app.py
```

### 3.2 Cambio permanente en Windows

`setx` guarda las variables para futuras terminales, pero no modifica la ventana actual. Ejecuta:

```powershell
setx CONTEXTUAL_QNA_INPUTS_DIR "D:\Datos\QnA\entradas"
setx CONTEXTUAL_QNA_OUTPUTS_DIR "D:\Datos\QnA\salidas"
setx CONTEXTUAL_QNA_PROCESSED_DIR "D:\Datos\QnA\procesados"
setx CONTEXTUAL_QNA_LOGS_DIR "D:\Datos\QnA\logs"
setx OLLAMA_MODELS "D:\Ollama_Modelos"
setx HF_HOME "D:\Datos\QnA\huggingface_cache"
```

Cierra y vuelve a abrir PowerShell antes de ejecutar la aplicacion. Para cambiar una variable solo para la sesion actual, usa la sintaxis `$env:NOMBRE = "valor"`.

### 3.3 Verificacion en Windows

Desde la raiz del proyecto:

```powershell
python -c "import sys; sys.path.insert(0, 'Python'); from config import load_settings; s=load_settings(); print(s.project_dir); print(s.inputs_dir); print(s.outputs_dir); print(s.ollama_models_dir)"
```

Las rutas mostradas deben coincidir con las carpetas configuradas.

## 4. Linux

### 4.1 Cambio temporal en Bash

Este cambio se mantiene mientras la terminal permanezca abierta.

```bash
cd /home/usuario/proyectos/Contextual-QnA-Extractor

export CONTEXTUAL_QNA_INPUTS_DIR="/mnt/datos/qna/entradas"
export CONTEXTUAL_QNA_OUTPUTS_DIR="/mnt/datos/qna/salidas"
export CONTEXTUAL_QNA_PROCESSED_DIR="/mnt/datos/qna/procesados"
export CONTEXTUAL_QNA_LOGS_DIR="/mnt/datos/qna/logs"
export CONTEXTUAL_QNA_PROMPTS_DIR="/home/usuario/proyectos/Contextual-QnA-Extractor/prompts"
export CONTEXTUAL_QNA_SQUAD_DATASET="/mnt/datos/qna/train-v2.0.json"
export OLLAMA_MODELS="/mnt/datos/ollama/models"
export HF_HOME="/mnt/datos/qna/huggingface_cache"
```

Si se usa Ollama, define `OLLAMA_MODELS` antes de iniciar el servidor:

```bash
ollama serve
```

En otra terminal, exporta las variables nuevamente y ejecuta:

```bash
cd /home/usuario/proyectos/Contextual-QnA-Extractor
python3 Python/main.py --input "documento.pdf" --perfil "estudiante universitario" --modelo "llama3.1" --top_n 5
```

Tambien puedes iniciar las interfaces:

```bash
streamlit run Python/web_app.py
python3 Python/gui_app.py
```

### 4.2 Cambio permanente en Linux

Agrega las variables al archivo de inicio de Bash:

```bash
cat >> ~/.bashrc <<'EOF'
export CONTEXTUAL_QNA_INPUTS_DIR="/mnt/datos/qna/entradas"
export CONTEXTUAL_QNA_OUTPUTS_DIR="/mnt/datos/qna/salidas"
export CONTEXTUAL_QNA_PROCESSED_DIR="/mnt/datos/qna/procesados"
export CONTEXTUAL_QNA_LOGS_DIR="/mnt/datos/qna/logs"
export OLLAMA_MODELS="/mnt/datos/ollama/models"
export HF_HOME="/mnt/datos/qna/huggingface_cache"
EOF
source ~/.bashrc
```

Si la terminal usa Zsh, coloca las mismas lineas en `~/.zshrc` y ejecuta `source ~/.zshrc`.

### 4.3 Verificacion en Linux

```bash
python3 -c "import sys; sys.path.insert(0, 'Python'); from config import load_settings; s=load_settings(); print(s.project_dir); print(s.inputs_dir); print(s.outputs_dir); print(s.ollama_models_dir)"
```

## 5. Cambiar entre Windows y Linux

1. Copia el repositorio en el nuevo sistema operativo.
2. Activa el entorno Python e instala `requirements.txt`.
3. Define las variables usando la sintaxis del sistema operativo.
4. Usa rutas con el formato nativo del sistema: `D:\Datos\...` en Windows y `/mnt/datos/...` o `/home/...` en Linux.
5. Verifica la configuracion con el comando de la seccion correspondiente.
6. Ejecuta la GUI, la web o el CLI normalmente.

No se deben cambiar separadores de ruta dentro de `Python/config.py`; el modulo `pathlib` adapta la separacion de rutas automaticamente.

## 6. Volver a las rutas predeterminadas

En PowerShell, elimina las variables de la sesion:

```powershell
Remove-Item Env:CONTEXTUAL_QNA_INPUTS_DIR, Env:CONTEXTUAL_QNA_OUTPUTS_DIR, Env:CONTEXTUAL_QNA_PROCESSED_DIR, Env:CONTEXTUAL_QNA_LOGS_DIR, Env:OLLAMA_MODELS, Env:HF_HOME
```

En Bash:

```bash
unset CONTEXTUAL_QNA_INPUTS_DIR CONTEXTUAL_QNA_OUTPUTS_DIR CONTEXTUAL_QNA_PROCESSED_DIR CONTEXTUAL_QNA_LOGS_DIR OLLAMA_MODELS HF_HOME
```

Si las variables se guardaron permanentemente en `~/.bashrc`, `~/.zshrc` o mediante `setx`, tambien hay que quitar esas lineas o valores para que no vuelvan a aplicarse en nuevas terminales.
