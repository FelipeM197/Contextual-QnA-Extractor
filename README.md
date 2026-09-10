# ⚡ Contextual QnA Extractor

Un generador RAG Multi-Agente basado en **Ollama** y **LangGraph**. Este sistema es capaz de ingerir documentos (PDF, Word, Markdown, texto plano, imágenes) y generar de forma autónoma cuestionarios adaptados a diferentes perfiles (universitario, técnico, principiante) preservando el rigor y trazabilidad de las fuentes.

## 🧠 Arquitectura del Proyecto

El proyecto está diseñado de forma modular, separando la orquestación, las herramientas de ingesta, y el cerebro del sistema.

```mermaid
flowchart TD
    classDef ui fill:#3B82F6,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef core fill:#10B981,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef agent fill:#8B5CF6,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef planned fill:#F59E0B,stroke:#fff,stroke-width:2px,color:#fff,stroke-dasharray: 5 5,font-weight:bold
    classDef data fill:#475569,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold

    UI["🖥️ Interfaces de Usuario<br/>(Web, Escritorio, Consola)"]:::ui
    Main["⚙️ Controlador Backend<br/>(Prepara entorno y configuración)"]:::core

    subgraph Data ["🗂️ Almacenamiento y Datos"]
        direction LR
        Inputs[/"📄 Entradas<br/>(PDFs, Documentos)"/]:::data
        VectorDB[("🗄️ DuckDB<br/>(Base Vectorial)")]:::data
        Outputs[/"📝 Salidas<br/>(Cuestionarios y Logs)"/]:::data
    end

    subgraph Agents ["🧠 Cerebro del Sistema (LangGraph)"]
        direction TB
        A1["Agente 1<br/>Analista (Extrae Conceptos)"]:::agent
        A2["Agente 2<br/>Generador (Formula Preguntas)"]:::agent
        A3["Agente 3<br/>Resolutor (Responde con Evidencia)"]:::agent
        A4["Agente 4<br/>Adaptador (Modula Tono Pedagógico)"]:::agent
        
        A5["Agente 5 (Planeado)<br/>Crítico / Auditor (RAG Guardrail)"]:::planned

        A1 --> A2 --> A3
        A3 ==>|Flujo Lineal Actual| A4
        A3 -.->|Flujo Planeado| A5
        A5 -.->|Rechaza (Alucinación)| A2
        A5 -.->|Aprueba (Verificado)| A4
    end

    UI -->|Pasa Parámetros| Main
    Main -->|Ingesta Documentos| Inputs
    Inputs -->|Indexa Chunks| VectorDB
    Main -->|Dispara Grafo| A1
    
    A3 <-->|Recupera Contexto| VectorDB
    A4 -->|Guarda Resultado| Outputs
```

## 📂 Estructura del Repositorio

- `inputs/`: Documentos originales que se procesan.
- `outputs/`: 
  - `processed/`: Textos convertidos a Markdown y la base de datos vectorial (DuckDB).
  - `cuestionarios-logs/`: Entregables finales (Markdown) y logs de ejecución.
- `prompts/`: Instrucciones puras en Markdown que controlan el comportamiento de los Agentes.
- `Python/`: Núcleo de la arquitectura modular (Controlador, esquemas, herramientas RAG, agentes y grafos), e interfaces (gui_app.py y web_app.py).
- `sh/`: Scripts de inicialización por consola (`bash` y `powershell`).
- `docs/`: Documentación del proyecto (planes y guías).

## 📊 Registro de Ejecución (Logs para Entrenamiento)

Con el fin de auditar el sistema y recopilar datos masivos para el futuro entrenamiento (Fine-Tuning) de modelos propios, el sistema captura el "pensamiento" completo de la IA en cada ejecución (prompts exactos, respuestas crudas, contextos y errores). 

Estos datos se guardan centralizados en dos mega-archivos dentro de `outputs/logs/`:
- **`dataset_training.log`**: Un archivo de texto estructurado y legible por humanos. Muestra cada evento separado de forma visual y clara, ideal para revisar manualmente el razonamiento de los Agentes paso a paso.
- **`dataset_training.jsonl`**: Contiene exactamente la misma información pero en formato *JSON Lines*. Este formato es el estándar de la industria para ingestar y entrenar modelos directamente mediante librerías como HuggingFace o la API de OpenAI.

## 🚀 Requisitos Previos

1. **Entorno Python**: Asegúrate de usar el entorno con las dependencias instaladas (ej. `conda activate QAG_System`).
2. **Ollama**: Necesitas tener [Ollama](https://ollama.com/) instalado y corriendo localmente, junto con los modelos necesarios descargados (por ejemplo: `llama3.1`, `gemma2`, `mistral`, `gemma4:e2b`).
3. **Dependencias**: Instalar las librerías desde los archivos de requirements de la raíz.

## ⚙️ Cómo Ejecutar el Sistema

El sistema ofrece tres vías de ejecución según la preferencia del usuario. Todas ellas se ejecutan desde la raíz del proyecto.

### 1. Interfaz Web (Recomendado)
Para interactuar con la aplicación en tu navegador de manera visual e intuitiva:
```bash
streamlit run Python/web_app.py
```
*Te permitirá subir archivos arrastrando y soltando, y visualizar el Cuestionario resultante en pantalla.*

### 2. Interfaz de Escritorio (GUI)
Si prefieres una aplicación de escritorio nativa instalada localmente:
```bash
python Python/gui_app.py
```

### 3. Vía Consola (Scripts y CLI)
Para integraciones rápidas sin interfaz gráfica:
```bash
# Vía shell script:
bash sh/lanzar_beta.sh

# Vía PowerShell:
.\sh\lanzar_beta.ps1
```

O llamando directamente al núcleo de Python pasándole los parámetros deseados:
```bash
python Python/main.py --input "Mi_Documento.pdf" --perfil "estudiante universitario" --modelo "llama3.1" --top_n 5
```

---
> **Nota de Mantenimiento:**  
> Este `README.md` deberá actualizarse progresivamente conforme se integren la nueva arquitectura en transición, los esquemas Pydantic y el 5to Agente Auditor planeado en el grafo principal.
