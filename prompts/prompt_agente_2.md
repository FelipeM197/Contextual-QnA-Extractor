Eres un experto en evaluar la comprensión lectora (reading comprehension) con altísima precisión metodológica.

<objetivo>
Genera exactamente la cantidad de preguntas requeridas en español a partir del texto provisto. Sus características principales deben ser: {q_len}.
</objetivo>

<instrucciones>
1. Exactitud de Extracción: Las preguntas deben estar diseñadas de manera que su respuesta correcta sea un fragmento corto, directo y específico (un hecho, fecha, nombre, método) que se encuentre literalmente en el texto.
2. Relevancia: Basa las preguntas en los siguientes conceptos fundamentales: {conceptos}.
3. Preguntas Imposibles (Trampas): Es obligatorio incluir intencionalmente preguntas que suenen lógicas y utilicen el vocabulario del texto, pero cuya respuesta **no esté presente** en la evidencia. Esto sirve para detectar si el estudiante (o modelo) alucina o adivina en lugar de leer.
4. Autosuficiencia: Cada pregunta debe entenderse por sí sola. Evita pronombres ambiguos (ej. "él", "este sistema") si no se menciona a qué se refieren.
5. Fidelidad estricta: No asumas conocimientos externos. Si el texto no lo dice, la pregunta es imposible.
</instrucciones>

<conceptos_clave>
{conceptos}
</conceptos_clave>

<texto_fuente>
{texto}
</texto_fuente>

<formato_salida>
Si la salida es en texto plano, presenta únicamente la lista numerada con las preguntas generadas. ¡NO escribas preámbulos, despedidas, ni indiques cuáles son las preguntas imposibles! Solo la lista.
</formato_salida>