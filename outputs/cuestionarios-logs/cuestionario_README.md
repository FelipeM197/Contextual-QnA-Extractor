# Cuestionario adaptado para estudiante universitario

## 1. ¿Cuál es la función específica del directorio `inputs/` dentro de la estructura del sistema RAG modular y qué tipo de documentos se espera que contenga?

La función principal del directorio `inputs/` en la arquitectura del sistema RAG modular es servir como el repositorio de los documentos originales que serán procesados posteriormente por el sistema. Estos son los datos fuente esenciales para la base de conocimiento del sistema.

Fuente: CHUNK 1

## 2. Describa el papel de la carpeta `python/` en el flujo del sistema, identificando los componentes clave relacionados con la configuración, ingesta y las herramientas RAG.

La carpeta `python/` alberga los componentes esenciales que gestionan el funcionamiento interno del sistema RAG modular. Esta carpeta incluye elementos cruciales como la configuración general del sistema, los módulos de ingesta de datos, las herramientas específicas para RAG, los agentes, el grafo de conocimiento y la entrada principal. Los parámetros fundamentales que definen el comportamiento del sistema se encuentran almacenados en el archivo `python/config.py`.

Fuente: CHUNK 1

## 3. ¿Cómo se relaciona la carpeta `prompts/` con el formato Markdown y cuál es su propósito dentro de la arquitectura del sistema?

La carpeta `prompts/` contiene las instrucciones o *prompts* que están formateadas en Markdown. Su propósito dentro de la arquitectura es definir las preguntas y respuestas específicas que el sistema debe generar, asegurando que la interacción con la arquitectura se realice utilizando un formato estructurado y legible (Markdown) para facilitar la generación de resultados.

Fuente: CHUNK 1

## 4. Si se desea obtener el cuestionario final, ¿qué elementos deben estar presentes en el directorio `outputs/` según la estructura definida?

Para generar el cuestionario final, el directorio `outputs/` debe contener los siguientes artefactos resultantes del proceso de ejecución: el contenido convertido a formato Markdown, la base de datos DuckDB y el cuestionario final consolidado.

Fuente: CHUNK 1

## 5. Explique el proceso de ejecución desde la raíz del proyecto, detallando qué comando `python` se utiliza y dónde se localizan los parámetros principales para la entrada.

El proceso de ejecución del sistema comienza en la raíz del proyecto siguiendo estos pasos:

1.  Activar el entorno virtual utilizando el comando `conda activate QAG_System`.
2.  Ejecutar el script principal mediante el comando `python -m python.main`.

Los parámetros principales que se utilizan para definir la entrada del sistema se encuentran definidos en el archivo `python/config.py`.

Fuente: CHUNK 1