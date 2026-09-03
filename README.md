# Sistema RAG modular

## Estructura

- `inputs/`: documentos originales que se procesan.
- `prompts/`: instrucciones Markdown para preguntas y respuestas.
- `python/`: configuracion, ingesta, herramientas RAG, agentes, grafo y entrada principal.
- `outputs/`: Markdown convertido, base DuckDB y cuestionario final.
- `RAG.ipynb`: version interactiva y documentacion del flujo.

## Ejecucion

Desde la raiz del proyecto:

```bash
conda activate QAG_System
python -m python.main
```

El PDF de entrada esperado es `inputs/Manchester United Profile.pdf`. Los parametros principales se encuentran en `python/config.py`.
