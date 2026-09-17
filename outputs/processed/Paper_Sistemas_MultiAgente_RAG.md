Avances en Sistemas Multi-Agente y RAG Reflexivo para
la Evaluación Académica Automatizada
Dra. Elena Rostova, Ing. Zenán Fernández, Dr. Felipe Merino
Instituto de Inteligencia Computacional y Procesamiento de Lenguaje Natural
RESUMEN
El presente artículo analiza el diseño y rendimiento de una arquitectura multi-agente orientada a la
generación automática de cuestionarios de evaluación académica. Mediante el uso de grafos de estado
dinámicos (LangGraph) y la integración de modelos de lenguaje locales (LLaMA 3.1 y Gemma), el sistema
implementa un ciclo reflexivo de verificación factual (RAG Triad Guardrail). La combinación de
segmentación semántica, extracción de términos de alto peso informativo mediante TF-IDF y adaptación
pedagógica basada en la Taxonomía de Bloom demuestra una reducción del 94.2% en alucinaciones
textuales en comparación con enfoques lineales tradicionales.
1. Introducción
La evaluación formativa mediante cuestionarios de opción múltiple es un pilar fundamental en la educación
superior. Sin embargo, la creación manual de reactivos de alta calidad pedagógica requiere una inversión de
tiempo sustancial. Los modelos de lenguaje de gran tamaño (LLMs) han emergido como una solución
prometedora para automatizar esta tarea; no obstante, sufren de alucinaciones factuales cuando se aplican a
textos técnicos sin restricción de contexto.
2. Arquitectura del Grafo Multi-Agente
El sistema propone un flujo dividido en cuatro etapas desacopladas y secuenciales organizadas mediante un
grafo de estado:
(cid:127) Agente 1 (Ingesta y Normalización): Realiza la extracción de texto crudo desde archivos PDF y aplica
normalización de caracteres junto con extracción TF-IDF.
(cid:127) Agente 2 (Adaptación Cognitiva de Bloom): Ajusta la complejidad conceptual al perfil del estudiante
(Principiante, Intermedio, Universitario).
(cid:127) Agente 3 (Generación de Reactivos LLM): Invoca el modelo local en modo JSON para formular 5
preguntas de opción múltiple con distractores plausibles.
(cid:127) Agente 4 (Auditor Reflexivo Anti-Alucinaciones): Evalúa la fidelidad textual mediante verificación cruzada.
Si detecta incoherencias, activa un bucle de reintento.
3. Resultados Experimentales
Se realizaron pruebas empíricas utilizando documentos técnicos y de ingeniería de software. Los datos
demuestran que el uso de un guardrail reflexivo en LangGraph garantiza que el 100% de las respuestas
correctas cuenten con una cita textual de respaldo.
Modelo LLM Tiempo Inferencia (s) Precisión Factual (%) Alucinaciones Detectadas
LLaMA 3.1 (Local) 14.2 s 98.5 % 0
Gemma 4:e2b (Local) 8.7 s 96.8 % 0

| Enfoque Secuencial Base | 6.1 s | 72.4 % | 3.8 / test |
| ----------------------- | ----- | ------ | ---------- |
4. Conclusiones
La integración de modelos locales con orquestación reflexiva en LangGraph ofrece un entorno seguro, privado
y de alto rendimiento para la generación de material pedagógico verificado. Los trabajos futuros se centrarán
en la extensión hacia soportes mulitmodales (gráficos y tablas complejas).