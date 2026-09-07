Estructuras de Datos
y
Algoritmos II

LORENA RECALDE Ph.D.

Escuela Politécnica Nacional

2026-A

Revisión: Recursividad

2

Introducción

•La recursividad es una forma elegante de resolver problemas, pero es
controversial. La gente lo ama o lo odia, o lo odia hasta que aprende a amarlo
unos años más tarde.

•Para facilitarle las cosas, hay algunos consejos:

üBusque ejemplos de código. Ejecute el código usted mismo para ver cómo

funciona.

ü Al menos una vez, realice una función recursiva con lápiz y papel. Caminar a

través de una función recursiva le enseñará cómo funciona.

•Usted puede generar pseudocódigo a manera de una descripción de alto nivel del
problema que está intentando resolver.

3

Recursividad

•Supongamos que buscas la llave de una
habitación cerrada.

•Y la llave probablemente está en esta caja.

4

Recursividad

•Esta caja contiene más cajas, con más cajas dentro de esas cajas.

•La llave está en una caja en alguna parte.

•¿Cuál es tu algoritmo para buscar la llave?

5

Recursividad

•Aquí hay un primer enfoque.

1. Haz una pila de un montón de cajas para
mirar.

2. Toma una caja y mira en ella.

3. Si encuentras una caja, agrégala a la pila
para verla luego.

4. Si encuentras una llave, ¡ya está!

5. Repite.

6

Recursividad

•Aquí hay un segundo enfoque.

1. Mira a través de la caja.

2. Si encuentras una caja, ve al paso 1.

3. Si encuentras una llave, ¡ya está!

7

Recursividad

•¿Qué enfoque te parece más fácil? El primer enfoque utiliza un bucle while.

•Mientras la pila no está vacía, toma una caja y mira a través de ella:

8

Recursividad

•La segunda forma usa la recursividad. La recursión es donde una función se
llama a sí misma. Aquí está la segunda forma en pseudocódigo:

9

Recursividad

•Ambos enfoques logran lo mismo, pero el segundo enfoque parece ser más
claro.

•No hay beneficio de rendimiento al usar la recursividad; de hecho, los bucles a
veces son mejores para el rendimiento.

•Citando a Leigh Caldwell: “Los bucles pueden lograr una ganancia de
rendimiento para su programa. La recursión puede lograr una ganancia de
rendimiento para su programador. ¡Elija cuál es más importante en su
situación! ”

•Muchos algoritmos importantes utilizan la recursividad, por lo que es
importante comprender cómo trabaja.

10

Base case and recursive case

•Debido a que una función recursiva se llama a sí misma, es fácil escribir una función
incorrectamente que termina en un bucle infinito.

•Por ejemplo, suponga que desea escribir una función que imprima una cuenta regresiva,
como esta:

> 3 ... 2 ... 1

•Puedes escribirlo recursivamente, así:

•Escriba este código y ejecútelo. Notará un problema: ¡esta función se ejecutará para
siempre!

> 3 ... 2 ... 1 ... 0 ...- 1 ...- 2 ...

11

Base case and recursive case

•Cuando escribe una función recursiva, debe decirle cuándo dejar de recurrir.

•Es por eso que cada función recursiva tiene dos partes: el caso base y el caso
recursivo.

•El caso recursivo es cuando la función se llama a sí misma.

•El caso base es cuando la función no se vuelve a llamar a sí misma ... por lo que
no entra en un bucle infinito.

•Agreguemos un caso base a la función de cuenta regresiva:

12

Base case and recursive case

•Ahora la función se ejecuta como se esperaba. Es algo parecido a esto.

13

Pilas

14

La Pila

•La pila de llamadas es un concepto importante en la programación general, y
cuando se utiliza la recursividad.

•Supongamos que está planificando una barbacoa. Mantiene una lista de tareas
para la barbacoa, en forma de una pila de notas adhesivas.

•¿Recuerda el trabajo de arrays y listas enlazadas? Puede agregar elementos de
tareas en cualquier lugar de la lista/arreglo o eliminar elementos de cualquier
posición. La pila de notas adhesivas es mucho más simple:

•Cuando inserta un elemento, se agrega a la parte superior de la pila.

•Cuando lee un elemento, solo lee el elemento superior, y el elemento superior es
el que se elimina de la pila.

15

La Pila

•Por lo tanto, su lista de tareas solo tiene dos acciones: push (insertar) y pop
(eliminar y leer).

16

La Pila
•Veamos la lista de tareas en acción.

•Esta estructura de datos se llama pila.

•La pila es una estructura de datos simple.

17

La Pila de Llamadas

18

La pila de llamadas

•Su computadora usa una pila internamente llamada pila de llamadas.

•Aquí hay una función simple:

•Esta función te saluda y

•luego llama a otras dos funciones

19

La pila de llamadas

•Veamos qué sucede cuando llamas a una función.

•Supongamos que llamas greet ("maggie").

•Primero, su computadora asigna una caja de memoria para esa llamada de
función.

•Ahora usemos la memoria. El nombre de la variable se establece en "maggie".
Eso necesita ser guardado en la memoria.

20

La pila de llamadas

•Cada vez que realiza una llamada de función, su computadora guarda los valores
para todas las variables para esa llamada en la memoria de esta manera. A
continuación, imprime hello, maggie!

•Entonces llamas a greet2("maggie").

•Nuevamente, su computadora asigna una caja de memoria para esta llamada de
función.

21

La pila de llamadas

•Su computadora está usando una pila para estas cajas. La segunda caja se agrega
encima de la primera. Imprimes how are you, maggie? Luego se hace el return de
la llamada a la función. Cuando esto sucede, la caja en la parte superior de la pila
sale.

22

La pila de llamadas

•Ahora la caja superior de la pila es para la función greet, lo que significa que
regresó a la función de saludo.

•Cuando llamó a la función greet2, la función greet se completó parcialmente.
Esta es la idea: cuando llama a una función desde otra función, la función de
llamada se detiene en un estado parcialmente completado.

•Todos los valores de las variables para esa función todavía se almacenan en
la memoria. Ahora que ha terminado con la función greet2, ha vuelto a la
función greet y retomó donde lo dejó.

•Primero imprime getting ready to say bye…. Llama a la función bye.

23

La pila de llamadas

•Se agrega un cuadro para esa función en la parte superior de la pila.

•Entonces imprimes ok bye! y se hace el retorno de la llamada a la función. Y has
vuelto a la función greet.

24

La pila de llamadas

•No hay nada más que hacer, así que también se hace el retorno de la
función de greet.
•Esta pila, utilizada para guardar las variables para múltiples
funciones, se denomina pila de llamadas.

25

La pila de llamadas

26

La pila de llamadas

Ahora veamos la pila de llamadas en acción con una función recursiva.

27

La pila de llamadas con recursividad

•¡Las funciones recursivas también usan la pila de llamadas!

•Veamos esto con la función factorial. factorial(5) se escribe como 5!, y se define
así: 5! = 5 * 4 * 3 * 2 * 1.

• Del mismo modo, factorial(4) es 4 * 3 * 2 * 1.

•Aquí hay una función recursiva para calcular el factorial de un número:

28

La pila de llamadas con recursividad

•Ahora llamas a la función fact(3). Veamos esta llamada línea por línea y veamos
cómo cambia la pila.

•Recuerde, la caja superior de la pila le dice qué llamada a fact está actualmente.

29

30

La pila de llamadas con recursividad

•Tenga en cuenta que cada llamada a fact tiene su propia copia de x. No puede
acceder a una copia de x de una función diferente.

31

La pila de llamadas con recursividad

•La pila juega un papel
importante en la recursividad.
En el ejemplo inicial, hubo dos
enfoques para encontrar la
llave. Aquí está la primera forma
de nuevo.

32

La pila de llamadas con recursividad

•De esta manera, crea una pila de cajas para buscar, de modo que siempre sepa
qué cajas aún necesita buscar.

33

La pila de llamadas con recursividad

•Pero en el enfoque recursivo, no hay una estructura de pila.

34

La pila de llamadas
con recursividad

•Si no hay una pila, ¿cómo sabe
su algoritmo qué cajas todavía
tiene que mirar? Aquí hay un
ejemplo.

35

La pila de llamadas con recursividad

•En este punto, la pila de llamadas se ve así.

36

La pila de llamadas con recursividad

•¡El "montón de cajas" se guarda en la pila de llamadas!

•Esta es una pila de llamadas de función a medio completar, cada una con su
propia lista de cajas a medio completar para examinar. El uso de la pila es
conveniente porque no tiene que hacer un seguimiento de una pila de cajas, la
pila de llamadas lo hace por usted.

•Usar la pila de llamadas es conveniente, pero tiene un costo: guardar toda esa
información puede ocupar mucha memoria. Cada una de esas llamadas a
funciones ocupa algo de memoria, y cuando su pila es demasiado alta, eso
significa que su computadora está guardando información para muchas llamadas
a funciones.

•En ese punto, puede reescribir su código para usar un bucle en su lugar.

37

La pila de llamadas con recursividad

38

La pila de llamadas con recursividad

39

