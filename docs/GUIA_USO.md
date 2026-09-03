# Guía de uso del sistema RAG multi-agente

## 1. ¿Qué hace el sistema?

`RAG.ipynb` procesa un documento, lo convierte a Markdown, recupera información relevante desde una base vectorial y ejecuta cuatro agentes:

1. Extrae conceptos importantes con TF-IDF.
2. Genera cinco preguntas sobre esos conceptos.
3. Responde las preguntas usando únicamente el contexto recuperado por Raghilda.
4. Adapta las respuestas al perfil objetivo y crea un cuestionario Markdown.

Los resultados se guardan en `cuestionario_final.md`.

## 2. Preparar el entorno

Abre PowerShell en:

```powershell
cd ruta\al\proyecto
```

Activa el entorno existente:

```powershell
.\.venv\Scripts\Activate.ps1
```

El notebook ya está configurado para usar `.venv (Python 3.11.9)`. Si se necesita reconstruir el entorno, instala las dependencias con:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requeriments.txt
```

No es necesario ejecutar las instalaciones comentadas dentro del notebook.

## 3. Modelo local opcional

Ollama permite que los agentes 2, 3 y 4 usen un LLM local. El notebook usa `llama3.1`.

El modelo ya está almacenado en `D:\Ollama_Modelos`, por lo que **no ejecutes `ollama pull` si los blobs ya existen**. El servidor debe iniciarse apuntando a esa carpeta, porque cambiar la variable en una terminal no cambia un servidor que ya estaba ejecutándose.

Para usar la instalación existente en `D:`:

```powershell
# Cierra Ollama desde el icono de la bandeja de Windows y cancela cualquier pull con Ctrl+C.
$env:OLLAMA_MODELS="D:\Ollama_Modelos"
ollama serve
```

Deja esa terminal abierta y, en otra terminal, verifica sin descargar nada:

```powershell
$env:OLLAMA_MODELS="D:\Ollama_Modelos"
ollama list
```

Debe aparecer `llama3.1`. Si aparece, ejecuta el notebook. No es necesario ejecutar `ollama serve` otra vez.

El notebook usa las siguientes carpetas del disco `D:`:

- Modelos de Ollama: `d:\Ollama_Modelos`
- Cache de Hugging Face: `d:\labADA\huggingface_cache`

Si el modelo no está descargado, el sistema no se detiene: usa un fallback determinista basado en los chunks recuperados.

## 4. Archivos de entrada aceptados

Se pueden usar documentos que contengan texto explicativo, técnico o educativo:

- `.pdf`: manuales, artículos, presentaciones o guías.
- `.md`: documentación Markdown con títulos y secciones.
- `.txt`: transcripciones, notas de clase o guiones.
- `.docx`: documentos de Word.

Para una prueba, se recomienda un archivo de entre 1 y 20 páginas con información relacionada y varias secciones. Ejemplos adecuados:

- Un manual de uso de una biblioteca Python.
- Una transcripción de una clase.
- Una guía técnica de una API.
- Un artículo sobre inteligencia artificial.
- Un documento de requisitos de software.

## 5. Cómo pasar un archivo nuevo

1. Copia el archivo en `data\input`.
2. Abre `notebooks\RAG.ipynb`.
3. En la celda de ingesta, cambia esta línea por el nombre del archivo:

```python
pdf_path = PROJECT_DIR / "mi_documento.pdf"
```

Aunque la variable se llama `pdf_path`, MarkItDown también puede convertir formatos compatibles como `.docx` y `.txt`.

4. Si el archivo es una fuente nueva, usa una base nueva en `data\vectorstore` para evitar mezclar documentos. Cambia:

```python
db_path = PROJECT_DIR / "chatlas_hf_nuevo.db"
```

5. Ejecuta las celdas en orden. La prueba actual usa `data\input\Informe Proyecto Bim 1 EDAII.pdf`.

La base de esta prueba es `data\vectorstore\informe_bim1_edaII.db` y se abre en solo lectura. La base anterior `data\vectorstore\chatlas_hf.db` no se borra ni se modifica automáticamente.

## 6. Orden de ejecución

Ejecuta las celdas de arriba hacia abajo:

1. Dependencias documentadas.
2. Configuración del entorno y carpetas del disco `D:`.
3. Dependencias opcionales de embeddings.
4. Conversión del documento e inicialización de Raghilda.
5. Definición de `QAState` y herramientas.
6. Detección del modelo Ollama.
7. Definición de los cuatro agentes.
8. Construcción y visualización del grafo.
9. Ejecución del flujo.
10. Exportación del resultado.

Los bloques de texto que aparecen encima de cada celda explican su propósito.

## 7. Archivos generados

### `data\processed\documento_base.md`

Es la versión Markdown del documento original. Debe verse como texto estructurado, por ejemplo:

```markdown
# Título del documento

## Primera sección

Contenido de la primera sección.

## Segunda sección

Contenido de la segunda sección.
```

### `outputs\cuestionario_final.md`

Es el resultado final. Debe contener un título, cinco preguntas, respuestas basadas en el documento y las fuentes. Ejemplo de estructura:

```markdown
# Cuestionario para estudiante universitario

## 1. What does the document explain about embeddings?

La respuesta debe utilizar información recuperada del documento.

Fuente: CHUNK 1

## 2. What is the purpose of the vector store?

La respuesta debe estar respaldada por el contexto recuperado.

Fuente: CHUNK 2
```

Cuando Ollama está disponible, las respuestas son redactadas por el LLM con instrucciones para no salir del contexto. Cuando no está disponible, el fallback imprime directamente el primer chunk recuperado y conserva `Fuente: CHUNK 1`.

## 8. Cómo leer la certeza

Las impresiones del notebook muestran una certeza heurística, no una probabilidad matemática:

- `1.00`: cálculo determinista, como TF-IDF o formateo Markdown.
- `0.70`: preguntas creadas por el fallback a partir de conceptos.
- `0.85`: salida del LLM o adaptación con instrucciones explícitas.
- Entre `0.45` y `0.95`: cantidad de evidencia recuperada por la búsqueda RAG.

La certeza indica cuánta evidencia o control tiene el proceso; no garantiza que el documento original sea correcto.

## 9. Qué hacer si cambia el documento

Si se cambia la fuente y se desea reindexar:

1. Cambia `pdf_path` al nuevo archivo dentro de `data\input`.
2. Usa un nombre distinto en `db_path` dentro de `data\vectorstore`.
3. Ejecuta nuevamente la celda de ingesta.
4. Ejecuta el resto de las celdas.

Esto evita mezclar los chunks de documentos diferentes y protege la base original.

## 10. Finalizar

Para salir del entorno virtual:

```powershell
deactivate
```
