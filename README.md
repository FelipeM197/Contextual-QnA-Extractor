# RAG Multi-Agent

Sistema RAG multi-agente con LangGraph, Raghilda, DuckDB y Ollama. Convierte documentos a Markdown, recupera contexto, genera preguntas, responde con evidencia y exporta un cuestionario.

## Estructura

- `notebooks/RAG.ipynb`: flujo principal ejecutable.
- `data/input/`: documentos fuente.
- `data/processed/`: Markdown convertido.
- `data/vectorstore/`: bases DuckDB generadas.
- `outputs/`: cuestionarios exportados.
- `docs/GUIA_USO.md`: guía completa de uso.
- `docs/Plan.md`: plan de implementación.
- `requeriments.txt`: dependencias Python fijadas.

## Inicio rápido

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\Activate.ps1
```

Abre `notebooks/RAG.ipynb`, selecciona el kernel `.venv (Python 3.11.9)` y ejecuta las celdas en orden.

Para habilitar el modelo local, configura Ollama con almacenamiento en `D:` antes de iniciarlo:

```powershell
$env:OLLAMA_MODELS="D:\Ollama_Modelos"
ollama serve
```

Consulta [docs/GUIA_USO.md](docs/GUIA_USO.md) para cambiar documentos, reconstruir el entorno y revisar los resultados.
