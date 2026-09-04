Guía de Arquitectura Modular: Sistema QnA RAG con LangGraph

Esta guía documenta la estructura definitiva del proyecto en su fase "Beta", explicando la responsabilidad de cada directorio y archivo, y cómo se mapea la lógica del Sistema_QnA-main.ipynb original hacia el nuevo diseño modular de Python. El objetivo de esta reestructuración es lograr un sistema escalable, mantenible y preparado para integraciones futuras (como bases de datos de configuración), separando claramente la orquestación, las herramientas de soporte y la lógica de inteligencia artificial.

1. Estructura General de Carpetas

La arquitectura adopta un enfoque orientado a componentes, aislando el punto de entrada, los datos, las plantillas y el código fuente:

sh/: Panel de control y disparador del proyecto. Aquí reside la configuración inicial.

inputs/: Buzón de entrada para documentos crudos (PDFs, DOCX, TXT).

outputs/: Almacenamiento de los cuestionarios finales generados y subproductos procesados.

prompts/: Repositorio de instrucciones en texto plano para los agentes.

Python/ (o src/): El motor lógico del sistema, donde reside el código modular.

2. Detalle por Carpeta y Archivo

A continuación, se detalla la función específica de cada archivo, qué código debe contener y qué celdas del Notebook original reemplaza o adapta.

2.1 Carpeta sh/ (El Orquestador)

Función: Actúa como el único punto de entrada (Entry Point) del sistema. Su propósito es aislar las configuraciones (los parámetros) del código fuente en Python. En esta fase Beta, los parámetros están "quemados" (hardcodeados) en un script Bash, pero el diseño permite que en el futuro este script sea el responsable de consultar una base de datos MySQL (basándose en un ENV_CODE como 010) para obtener la configuración antes de lanzar el programa.

Archivo: lanzar_beta.sh

Descripción Detallada:
Es un Shell Script que define todas las variables de entorno y de ejecución. Configura qué documento procesar (INPUT_FILE), el perfil objetivo (TARGET_PROFILE), el modelo LLM a utilizar (MODEL_NAME, TEMPERATURE), el modelo de embeddings (EMBEDDING_MODEL), y los parámetros dinámicos para la longitud y cantidad de las interacciones (TOP_N_CONCEPTS, QUESTION_LENGTH, ANSWER_LENGTH, TOP_K_CHUNKS).

Mecánica: Tras definir estas variables, el script ejecuta un comando echo para mostrar un resumen visual en la terminal y luego invoca el archivo principal de Python inyectándole todos estos parámetros mediante banderas (--env, --input, etc.).

2.2 Carpeta inputs/

Función: Actuar como el repositorio de lectura inicial para el sistema.

Archivos esperados: Archivos crudos que el usuario deposita para ser analizados, como Informe Proyecto Bim 1 EDAII.pdf, o Nodo Actual Análisis.pdf. El sistema (a través de MarkItDown) leerá estos archivos para comenzar el flujo de extracción.

2.3 Carpeta outputs/

Función: Almacenar todo el material generado por el sistema, separando los entregables finales de los archivos de soporte intermedios.

Archivos en la Raíz: Los cuestionarios finales en formato Markdown (ej. cuestionario_Informe Proyecto Bim 1 EDAII.md). Estos son los entregables que el usuario final consumirá.

Subcarpeta processed/:

Archivos Markdown Convertidos (.md): El resultado de pasar los PDFs crudos por la herramienta MarkItDown. Mantenerlos aquí evita reprocesar documentos grandes innecesariamente.

Bases de Datos Vectoriales (.db): Los archivos generados por DuckDBStore (utilizando la extensión VSS). Aquí persisten los chunks vectorizados del documento, permitiendo búsquedas semánticas eficientes en ejecuciones posteriores sin necesidad de re-ingestar todo el texto.

2.4 Carpeta prompts/

Función: Desacoplar la personalidad y las reglas de los agentes de la lógica pura en Python.

Archivos: prompt_agente_2.md, prompt_agente_3.md, prompt_agente_4.md.

Descripción: Al mantener estas instrucciones en archivos de texto, cualquier persona (incluso sin conocimientos de programación) puede ajustar el comportamiento de los agentes. El código Python simplemente lee estos archivos y reemplaza marcadores (como {conceptos}, {texto}, {q_len}) con los valores en tiempo de ejecución.

2.5 Carpeta Python/ (El Motor del Proyecto)

Esta carpeta reemplaza por completo a los Notebooks (Sistema_QnA-main.ipynb). Se ha dividido la lógica en tres módulos especializados.

Archivo A: main.py (El Controlador)

Función: Es el puente entre las instrucciones del usuario (el archivo .sh) y el procesamiento interno.

Descripción Detallada:

Utiliza la librería argparse para atrapar todas las banderas (--env, --perfil, etc.) enviadas por lanzar_beta.sh.

Define y construye las rutas dinámicas hacia inputs/ y outputs/processed/ basándose en el nombre del archivo proporcionado.

Llama a las funciones en utils.py para preparar el entorno, convertir el PDF a Markdown y levantar la base vectorial en DuckDB.

Instancia el modelo LLM (ChatOllama) y verifica su disponibilidad local.

Invoca a RAG.py para construir el grafo y le envía el estado inicial (QAState) para comenzar la ejecución.

Toma la salida final del grafo y la escribe en un nuevo archivo en la carpeta outputs/.

Celdas Originales Reemplazadas:

Celda 6 (Verificación del modelo Ollama).

Celda 9 (Ejecución del grafo e inicialización del QAState).

Celda 10 (Exportación del archivo de texto final).

Archivo B: utils.py (Soporte Técnico y Herramientas)

Función: Agrupar todas las funciones de limpieza, conversión de formatos, procesamiento determinista de texto y gestión de bases de datos. Almacena las "herramientas" que no forman parte de la arquitectura del grafo en sí, manteniendo el código principal limpio.

Descripción Detallada:

configurar_entorno(): Redirige los directorios temporales de HuggingFace y Ollama para evitar el consumo excesivo en el disco principal.

convertir_a_markdown(): Llama a MarkItDown para transformar el documento fuente (PDF/DOCX) a texto plano.

abrir_o_crear_store(): Gestiona el ciclo de vida de DuckDB. Se encarga de aplicar chunking al Markdown y crear los índices HNSW para las búsquedas vectoriales, o simplemente conectar a una base existente de solo lectura.

extraer_conceptos_tfidf(): Una función matemática determinista que usa TfidfVectorizer (con un diccionario de stop words en español) para identificar los términos más importantes de un texto. A diferencia del Notebook original, ahora acepta un parámetro dinámico top_n para definir cuántos conceptos extraer.

Celdas Originales Reemplazadas:

Celda 2 (Configuración de entorno).

Celda 4 (Ingesta, conversión MarkItDown y gestión DuckDB).

Celda 5 (Parcial: lógica TF-IDF desacoplada de herramientas específicas de LangChain).

Archivo C: RAG.py (El Cerebro: LangGraph y Agentes)

Función: Definir estrictamente la topología de la inteligencia artificial: el estado compartido, el comportamiento interno de los nodos (agentes) y las transiciones (aristas) que los unen. No debe encargarse de lectura de archivos ni configuraciones de rutas.

Descripción Detallada:

Define el esquema de datos tipado QAState que viaja entre los agentes.

Contiene la función principal crear_grafo(llm, store, prompts_dir, params). Esta encapsulación es crítica: elimina la dependencia de variables globales, permitiendo que main.py inyecte el LLM, la conexión a la base de datos y los parámetros dinámicos de longitud/cantidad de forma segura.

Generación Dinámica de Esquemas: Reemplaza la restricción "dura" de 5 preguntas utilizando create_model de Pydantic, forzando al LLM a devolver una lista estructurada basada en el parámetro TOP_N_CONCEPTS.

Inyección en Caliente: Modifica los prompts base al vuelo, utilizando .replace() para incrustar no solo el texto y los conceptos, sino también las reglas dinámicas de longitud ({q_len}, {a_len}) provenientes del disparador.

Implementa los 4 nodos principales (agente_1_analista, agente_2_preguntas, agente_3_resolutor, agente_4_adaptador), incluyendo el uso de DuckDB en el nodo 3 para la recuperación de contexto (retrieve(pregunta, top_k)).

Ensambla y compila el flujo lineal del StateGraph (START -> Nodo 1 -> Nodo 2 -> Nodo 3 -> Nodo 4 -> END).

Celdas Originales Reemplazadas:

Celda 2.5 (Función cargar_prompt para leer los archivos Markdown).

Celda 5 (Parcial: definición de QAState y certeza_contexto).

Celda 7 (La lógica de los 4 agentes, ahora parametrizada).

Celda 8 (La construcción del StateGraph).

3. Flujo de Ejecución (End-to-End)

Para entender cómo estos archivos trabajan en conjunto, este es el ciclo de vida completo de una solicitud en la fase Beta:

El usuario ejecuta bash sh/lanzar_beta.sh.

El script de bash carga en la memoria temporal los parámetros deseados (ej. 5 preguntas, perfil de estudiante universitario, el archivo PDF a leer) e invoca python main.py con estos valores.

main.py atrapa los argumentos, calcula las rutas de lectura/escritura y le pide a utils.py que configure el entorno, convierta el PDF a Markdown en outputs/processed/ y levante la base de datos DuckDB.

main.py inicializa el cliente de Ollama y le pasa todas las piezas (el modelo, la conexión a la BD, la ruta a las plantillas y los parámetros) a la función crear_grafo de RAG.py.

RAG.py ensambla la estructura de agentes. Se inyecta el estado inicial (el texto procesado) y arranca el grafo.

Agente 1: Usa utils.extraer_conceptos_tfidf con el top_n solicitado.

Agente 2: Modifica el prompt con {q_len} y genera preguntas usando Pydantic dinámico.

Agente 3: Consulta la BD vectorial (top_k) y le pide a Ollama que responda respetando el {a_len}.

Agente 4: Formatea las respuestas crudas según el perfil objetivo.

El grafo termina y devuelve el QAState final a main.py.

main.py extrae el cuestionario_final del estado y lo guarda como un archivo Markdown limpio en la carpeta outputs/.