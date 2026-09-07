# Cuestionario adaptado para estudiante universitario

## 1. ¿Cuál es la diferencia fundamental entre el caso base y el caso recursivo en una función, y por qué es esencial incluir ambos para evitar bucles infinitos?

La función recursiva se define por dos componentes esenciales: el caso recursivo y el caso base. El caso recursivo ocurre cuando la función se invoca a sí misma (recursión), mientras que el caso base es la condición de parada que detiene la recursión. Es fundamental incluir el caso base porque garantiza que la secuencia de llamadas eventualmente termine, previniendo así que la función entre en un bucle infinito y cause un desbordamiento de la pila.

Fuente: CHUNK 1

## 2. ¿Cómo se relaciona la estructura de datos de pila con la gestión de elementos en una lista o arreglo, según el ejemplo de las tareas de la barbacoa?

La estructura de datos de pila (Stack) se relaciona con la gestión de elementos en listas o arreglos al proporcionar un mecanismo simple para manejar operaciones de inserción y eliminación. A diferencia de las listas o arreglos, que permiten agregar o eliminar elementos en cualquier posición, la pila impone una restricción: solo se pueden realizar operaciones en la parte superior (LIFO - Last In, First Out).

En el contexto del ejemplo de las tareas de la barbacoa, la pila se utiliza como una estructura simple donde solo existen dos operaciones fundamentales: `push` (insertar un elemento) y `pop` (eliminar y leer el elemento superior). Al insertar un nuevo elemento, este se añade a la cima de la pila. Al extraer un elemento, solo se accede al elemento más reciente, que es el que se elimina de la pila.

Fuente: CHUNK 1

## 3. Explique cómo la pila de llamadas gestiona el estado de múltiples funciones simultáneamente durante una secuencia de llamadas anidadas, utilizando el ejemplo de `greet` y `greet2`.

La pila de llamadas (Call Stack) gestiona el estado de múltiples funciones mediante la asignación de memoria. Cada vez que se llama a una función, esta guarda los valores de las variables locales y el contexto de ejecución en la memoria. Cuando una función llama a otra, la función actual se detiene en un estado parcialmente completado, y todos los valores de las variables para la función interrumpida se almacenan temporalmente en la pila. Al finalizar la ejecución de la función anidada (`greet2`), esta regresa a la función llamadora (`greet`) y retoma su ejecución exactamente desde el punto donde se detuvo, permitiendo que la pila mantenga el estado de todas las funciones activas.

Fuente: CHUNK 1

## 4. ¿Qué papel juega la pila de llamadas en la implementación de un algoritmo recursivo como el cálculo del factorial, y qué desventaja puede surgir al utilizar esta estructura para gestionar el "montón de cajas"?

La pila de llamadas es crucial en la implementación de algoritmos recursivos, ya que actúa como el mecanismo donde se almacena el estado de las llamadas anidadas. En el caso del cálculo del factorial, la pila gestiona el "montón de cajas" (o *stack frames*), almacenando la información necesaria para cada llamada recursiva a medio completar, permitiendo al algoritmo recordar qué cálculos debe realizar en el futuro.

La desventaja principal que puede surgir al utilizar esta estructura para gestionar este estado es el consumo de memoria. Al almacenar toda la información de las llamadas anidadas en la pila, si la profundidad de la recursión es muy grande, esto puede resultar en un alto uso de memoria y potencialmente causar un desbordamiento de la pila (*stack overflow*).

Fuente: CHUNK 2

## 5. Considerando los dos enfoques presentados para buscar una llave (usando pilas de cajas vs. recursividad), ¿cuál es el costo potencial de usar la pila de llamadas para gestionar la recursividad en comparación con un bucle iterativo?

El uso de la pila de llamadas para gestionar la recursividad conlleva un costo asociado principalmente a la memoria. Cada llamada a función requiere espacio adicional en la pila para almacenar su estado y contexto, lo que incrementa el consumo de memoria. En contraste, un enfoque iterativo (usando bucles) gestiona el estado mediante variables locales dentro del mismo contexto de ejecución, lo que generalmente resulta en una gestión de memoria más eficiente y predecible, evitando el riesgo de desbordamiento de la pila asociado a profundidades de recursión excesivas.

Fuente: CHUNK 2