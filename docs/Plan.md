Plan de Implementación Estratégica: Arquitectura Multi-Agente RAG + LangGraph

Este documento establece las directrices, el enfoque de desarrollo y la planeación paso a paso para implementar un sistema de 4 agentes con LangGraph y el motor RAG de Raghilda (basado en DuckDB).

El enfoque principal de esta guía es proporcionar instrucciones específicas de programación, diseño de prompts y manejo de flujo de datos, garantizando la integración fluida del RAG y la restricción estricta al disco D para almacenamiento.

Fase 0: Preparación Segura del Entorno (Restricción Disco D)

Enfoque de Configuración:
El mayor riesgo al usar modelos locales es saturar el disco principal (C:). Antes de importar librerías de IA, debes garantizar mediante código que las dependencias utilicen tu disco secundario.

Instrucciones de Implementación:

Al inicio de tu script principal, antes de cualquier importación de LangChain o Raghilda, utiliza la librería nativa de Python os para establecer programáticamente las variables de entorno.

Configura OLLAMA_MODELS apuntando a tu carpeta D:\Ollama_Modelos.

Configura HF_HOME apuntando a D:\labADA\huggingface_cache.

Instala las librerías necesarias en tu entorno virtual. Dado que ya tienes Raghilda, asegúrate de contar con LangGraph, LangChain-Ollama, Pydantic, scikit-learn y MarkItDown. No uses corchetes en las instalaciones si tu terminal presenta problemas; instala sentence-transformers por separado si es necesario.

Fase 1: Módulo de Ingesta de Datos y RAG (Fuera del Grafo)

Enfoque de Programación:
Una regla de oro en LangGraph es que el grafo no debe encargarse de procesar PDFs pesados ni inicializar bases de datos desde cero. La ingesta de datos ocurre una sola vez, ANTES de invocar el grafo de agentes.

Instrucciones de Implementación:

Conversión Universal: Escribe una función cuya única responsabilidad sea usar MarkItDown. Esta función recibirá la ruta de tu documento original y creará un archivo documento_base.md en el disco D.

Construcción del Vector Store:
Crea una función separada que inicialice tu base de datos Raghilda:

Instancia el modelo EmbeddingSentenceTransformers (usa "all-MiniLM-L6-v2" para que sea rápido y ligero).

Pasa tu archivo Markdown por el MarkdownChunker.

Realiza un upsert y build_index en la base de datos chatlas_hf.db.

Bloqueos de Archivo: Cuando termines la ingesta y vayas a usar la base de datos dentro del grafo (para buscar contexto), asegúrate de conectarte a DuckDB con el parámetro de solo lectura activado. Esto previene bloqueos de archivo (file locks) durante la ejecución paralela o concurrente.

Fase 2: Diseño del Estado Global (QAState)

Enfoque de Programación:
El estado es la memoria compartida de todos los agentes. Debe estar fuertemente tipado. Evita diccionarios genéricos; usa TypedDict para prevenir errores de llaves inexistentes. La filosofía aquí es la inmutabilidad: los agentes añaden datos al estado, no los sobrescriben.

Instrucciones de Implementación:
Define tu clase de estado con las siguientes propiedades exactas:

transcripcion_original: Cadena de texto. Contiene el texto base inyectado al inicio.

conceptos_clave: Lista de cadenas. Alimentada por el Agente 1.

preguntas_generadas: Lista de cadenas. Alimentada por el Agente 2.

respuestas_crudas: Lista de diccionarios. Alimentada por el Agente 3. Cada diccionario debe tener la pregunta, la respuesta generada y la cita de la fuente.

perfil_objetivo: Cadena de texto. Define la audiencia (ej. "estudiante universitario").

cuestionario_final: Cadena de texto. El Markdown final formateado por el Agente 4.

Fase 3: Ingeniería de Herramientas (Tools)

Enfoque de Programación:
En LangChain, las herramientas son funciones decoradas con @tool. La clave del éxito aquí es manejar los errores internamente para que, si una herramienta falla, no detenga todo el grafo, sino que devuelva un mensaje de error que el LLM pueda entender.

Instrucciones de Implementación:

Tool 1 (Extractor TF-IDF): Toma la lógica que ya tienes en el archivo base, adáptala para limpiar puntuación y extraer los 5 conceptos más relevantes.

Tool 2 (Estructurador Pydantic): Para evitar que el LLM alucine o devuelva texto basura (ej. "¡Claro! Aquí tienes tus preguntas..."), define una clase de Pydantic que represente una lista de strings. Usarás el método .with_structured_output() sobre tu LLM para forzarlo a devolver exactamente este objeto.

Tool 3 (Recuperador RAG):

Esta es tu conexión con DuckDB.

La herramienta debe recibir un string (una pregunta).

Ejecutará store.retrieve(pregunta, top_k=3).

Formato Crítico: No devuelvas una lista de objetos al LLM. Concatena los textos recuperados en un solo string gigante, pero introduce delimitadores visuales severos entre ellos (por ejemplo: "--- INICIO CHUNK 1 --- 

$$texto$$

 --- FIN CHUNK 1 ---"). Esto es absolutamente vital para que el LLM pueda realizar citaciones precisas en la Fase 4.

Fase 4: Orquestación de los 4 Agentes

Enfoque de Programación:
Cada agente (nodo) en LangGraph es simplemente una función de Python que recibe el QAState actual y devuelve un diccionario con las llaves que desea actualizar.

Instrucciones de Implementación:

Agente 1 (Analista): No malgastes llamadas al LLM aquí. Este agente es puramente determinístico. Pasa la transcripción por la Tool 1 y devuelve la lista de conceptos.

Agente 2 (Generador): Construye un Prompt que obligue al LLM a formular 5 preguntas basadas en los conceptos del Agente 1. Aplica la Tool 2 (Pydantic) para que el retorno sea directamente iterable en Python.

Agente 3 (Resolutor RAG - El Núcleo):

Este nodo es el más complejo. Debe contener un bucle for que itere sobre cada pregunta generada por el Agente 2.

Por cada pregunta, llama a la Tool 3 (Recuperador) para obtener los chunks.

Ingeniería de Prompt: El System Prompt de este agente debe ser draconiano. Instrucciones como: "RESPONDE ÚNICAMENTE BASADO EN EL CONTEXTO PROVISTO. SI LA RESPUESTA NO ESTÁ EN EL CONTEXTO, DI 'NO LO SÉ'. DEBES TERMINAR TU RESPUESTA CITANDO LA FUENTE EXACTA USANDO EL NOMBRE DEL CHUNK PROVISTO".

Almacena los resultados en una estructura de datos clara dentro de respuestas_crudas.

Agente 4 (Adaptador):

Este es un agente de traducción de audiencias. Lee las respuestas técnicas del Agente 3 y el perfil_objetivo.

Regla de Preservación: El System Prompt debe incluir una advertencia inquebrantable: "Bajo ninguna circunstancia debes eliminar o alterar las etiquetas de las fuentes (ej. 'Fuente: CHUNK 2'). Estas deben permanecer intactas en tu reescritura."

Fase 5: Conexión del Grafo y Ejecución

Enfoque de Programación:
Una vez definidos los nodos, la construcción del grafo es una receta lineal. Por ahora, evita ciclos condicionales complejos (como enviar respuestas a corregir) hasta que el flujo base funcione.

Instrucciones de Implementación:

Instancia StateGraph usando tu esquema QAState.

Agrega los 4 nodos.

Define los "Edges" (bordes) conectándolos secuencialmente desde START hasta END.

Compila el grafo.

Ejecuta tu script inyectando el texto base y el perfil objetivo en el estado inicial, y finalmente exporta la llave cuestionario_final utilizando las funciones de escritura nativas de Python (open("ruta_en_d.md", "w")).

Anexo: Arquitectura del Sistema

El siguiente diagrama representa el flujo lógico del sistema descrito en este documento.

graph TD

InputDoc((Entrada de Datos\nArchivo Origen)) --> Preprocesamiento
InputPerfil((Entrada:\nPerfil Objetivo)) --> EstadoGlobal

subgraph Preprocesamiento [Fase 1: Preparación RAG]
    Conversor[MarkItDown\nConvierte a .md]
    DB[(DuckDB Vector Store\nAlmacenado en Disco D)]
    Conversor --> DB
end

Preprocesamiento --> EstadoGlobal[(QAState\nMemoria Inmutable)]

subgraph Orquestacion [Fase Orquestación LangGraph]
    A1[Agente 1: Analista TF-IDF]
    A2[Agente 2: Generador Pydantic]
    A3[Agente 3: Resolutor RAG]
    A4[Agente 4: Adaptador Perfil]
    
    A1 -->|Extrae Conceptos| A2
    A2 -->|Genera 5 Preguntas| A3
    
    A3 -->|Consulta Bucle| ToolB[(Tool: Búsqueda DuckDB)]
    ToolB -.->|Devuelve Contexto Etiquetado| A3
    
    A3 -->|Respuestas Crudas + Citas| A4
end

EstadoGlobal -.-> Orquestacion
Orquestacion -.-> EstadoGlobal

A4 --> Salida((Exportación\nCuestionario .md\nGuardado en Disco D))
