# Cuestionario adaptado para estudiante universitario

## 1. ¿Cuál es el objetivo principal de la arquitectura multi-agente propuesta en el artículo?

La arquitectura multi-agente propuesta en el artículo tiene como objetivo principal automatizar la creación de cuestionarios de evaluación académica de alta calidad pedagógica. Esto se logra mediante la integración de modelos de lenguaje locales (LLaMA 3.1 y Gemma) y la implementación de un ciclo reflexivo de verificación factual (RAG Triad Guardrail) en LangGraph.

La arquitectura se divide en cuatro etapas desacopladas y secuenciales organizadas mediante un grafo de estado, que incluyen la ingestión y normalización de texto, la adaptación cognitiva de Bloom, la generación de reactivos LLM y la auditoría reflexiva anti-alucinaciones. El objetivo es reducir la inversión de tiempo necesaria para crear reactivos de alta calidad pedagógica y mejorar la precisión factual en la evaluación académica.

Fuente: CHUNK 1

## 2. ¿Cómo se integran los modelos de lenguaje locales (LLaMA 3.1 y Gemma) en el sistema para generar cuestionarios de evaluación académica?

El sistema integra los modelos de lenguaje locales (LLaMA 3.1 y Gemma) mediante la etapa "Agente 3 (Generación de Reactivos LLM)", donde se invoca el modelo local en modo JSON para formular 5 preguntas de opción múltiple con distractores plausibles. Esto se menciona en el apartado "Arquitectura del Grafo Multi-Agente" del contexto proporcionado.

Fuente: CHUNK 1

## 3. ¿Qué es el ciclo reflexivo de verificación factual (RAG Triad Guardrail) y su función en el sistema?

El ciclo reflexivo de verificación factual (RAG Triad Guardrail) es un componente clave de la arquitectura multi-agente propuesta en el artículo. Según el texto, este ciclo se implementa mediante la integración de modelos de lenguaje locales (LLaMA 3.1 y Gemma) y la utilización de grafos de estado dinámicos (LangGraph). Su función es evaluar la fidelidad textual mediante verificación cruzada, detectando incoherencias y activando un bucle de reintento si es necesario.

En otras palabras, el RAG Triad Guardrail actúa como un mecanismo de control y verificación que garantiza la precisión y la fidelidad de las respuestas generadas por el sistema. Esto se logra mediante la comparación de las respuestas con una cita textual de respaldo, lo que reduce significativamente las alucinaciones factuales en comparación con enfoques lineales tradicionales.

La implementación de este ciclo reflexivo es fundamental para la generación de material pedagógico verificado y confiable, lo que es esencial en la educación superior. Su función es crucial para garantizar que las respuestas generadas sean precisas y fiables, lo que reduce el riesgo de alucinaciones factuales y mejora la calidad del material pedagógico.

Fuente: CHUNK 1

## 4. ¿Cuál es la ventaja principal de utilizar un guardrail reflexivo en LangGraph en comparación con enfoques lineales tradicionales?

La ventaja principal de utilizar un guardrail reflexivo en LangGraph en comparación con enfoques lineales tradicionales es la reducción del 94.2% en alucinaciones textuales. Esto se debe a que el sistema implementa un ciclo reflexivo de verificación factual (RAG Triad Guardrail) que evalúa la fidelidad textual mediante verificación cruzada y activa un bucle de reintento si detecta incoherencias.

Además, la integración de modelos locales con orquestación reflexiva en LangGraph ofrece un entorno seguro, privado y de alto rendimiento para la generación de material pedagógico verificado. Esto se debe a que el sistema utiliza segmentación semántica, extracción de términos de alto peso informativo mediante TF-IDF y adaptación pedagógica basada en la Taxonomía de Bloom.

En resumen, el uso de un guardrail reflexivo en LangGraph permite una generación de cuestionarios de evaluación académica más precisa y confiable, reduciendo significativamente el número de alucinaciones textuales en comparación con enfoques lineales tradicionales.

Fuente: CHUNK 1

## 5. ¿Qué tipo de adaptación pedagógica se utiliza en el sistema para ajustar la complejidad conceptual al perfil del estudiante?

La adaptación pedagógica utilizada en el sistema para ajustar la complejidad conceptual al perfil del estudiante es la Taxonomía de Bloom.

Fuente: CHUNK 1