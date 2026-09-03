Entrada: Archivo .txt / .md

Entrada: Definicion del
Perfil Objetivo

Flujo de Procesamiento LangGraph

Agente 1: Analista de
Contexto

Tool 1: Extractor TF-IDF

Agente 2: Generador de

Preguntas

Inicio

Tool 2: Estructurador

Pydantic/JSON

Agente 3: Resolutor

Tool 3: Motor de Busqueda

Agente 4: Adaptador de

Textual (Chunks)

Perfil

Carga de Datos

Actualiza entidades

Provee entidades

Exporta cuestionario_final

Estado Global Compartido - QAState

[String]

transcripcion_original

[List] conceptos_clave

[List] preguntas_generadas

[List] respuestas_crudas

[String] perfil_objetivo

[List/JSON]

cuestionario_final

Salida: Cuestionario

JSON/Markdown

