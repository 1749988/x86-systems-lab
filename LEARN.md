# Guía de estudio: del C al ensamblador y la caché

## Qué conecta con la universidad

Este laboratorio trabaja tamaños de datos, extensión de signo, registros, direccionamiento indexado, saltos condicionales, convenios de llamada y caché. El simulador no implementa pipeline: IF/ID/OF/EX/WB es otro tema de arquitectura y no debe confundirse con los estados de la caché.

## Recorrido recomendado

1. Ejecuta `make test` y después `./build/array-demo 4 -2 4 0`.
2. Lee `main.c`: valida la entrada, llama a funciones declaradas en `array_ops.h` y muestra resultados.
3. Lee `array_ops.S`: implementa esas funciones sin código C oculto.
4. Compara una función con su equivalente escrito por ti en C.
5. Ejecuta el simulador con una y dos vías y explica la diferencia de fallos.

## Suma: los detalles que importan

Un `int32_t` ocupa 4 bytes, por eso el elemento `i` está en `[rdi + rcx * 4]`. RDI contiene la dirección base, RSI la longitud y RCX el índice. RAX acumula el resultado de 64 bits.

`movsxd` extiende el signo de 32 a 64 bits. El número -2 debe seguir siendo -2 al sumarlo. Cargarlo en un registro de 32 bits sin extensión de signo produciría un valor positivo al interpretarlo como entero de 64 bits.

`cmp rcx, rsi` seguido de `jae` compara índices sin signo: `size_t` no es negativo. Una condición sobre números con signo podría requerir otros saltos. No elijas `jge` o `jae` por parecido en el nombre.

`xor eax, eax` pone a cero todo RAX en modo de 64 bits. Escribir EAX tiene un efecto diferente a escribir solo AX o AL.

## Pila y convenio de llamada

`call` coloca la dirección de retorno en la pila y `ret` la recupera. Estas funciones no llaman a otras y solo utilizan registros que el llamador puede esperar que cambien. Por eso no necesitan guardar RBX/RBP/R12–R15 ni reservar un marco de pila.

El convenio System V usado aquí no es el convenio de Windows x64. No se puede copiar este código directamente a un proyecto MSVC y asumir que recibe los argumentos en los mismos registros.

## Caché: un ejemplo calculable a mano

Con 64 bytes de capacidad, líneas de 16 bytes y una vía, hay 4 conjuntos. Las direcciones 0 y 64 son los bloques 0 y 4: ambos van al conjunto 0. Alternar esas direcciones produce expulsiones constantes.

Con dos vías y la misma capacidad hay 2 conjuntos. Esos bloques siguen compartiendo conjunto, pero ahora caben juntos. Tras dos fallos iniciales, los siguientes accesos aciertan.

LRU significa expulsar la línea utilizada menos recientemente. Un acierto también actualiza ese orden. La prueba `test_hits_refresh_lru` comprueba precisamente ese detalle.

## Qué demuestran las pruebas

Las pruebas diferenciales comparan ensamblador con un resultado de referencia calculado en C. La semilla es fija para reproducir los mismos casos. Se comprueban cero elementos, negativos, extremos, longitudes pares/impares, no modificación de entradas y doble inversión.

Las páginas de guarda no permiten acceso: un acceso fuera del límite probado hace fallar el proceso. Cubren límites concretos, no constituyen una prueba formal de ausencia de errores para cualquier entrada.

## Ejercicios siguientes

1. Implementa `min_i32` en C y Assembly. Define qué debe pasar con un array vacío antes de programar.
2. Añade pruebas para preservar los registros exigidos por el ABI.
3. Crea dos trazas sintéticas para recorrer una matriz por filas y por columnas; compara la tasa de fallos manteniendo la misma geometría.
4. Añade FIFO al simulador y busca una traza donde difiera de LRU.
5. Describe cómo ampliarías el modelo con escrituras antes de escribir código.

Para una entrevista: explica una función instrucción a instrucción y calcula una traza corta a mano. Presenta las limitaciones del modelo y evita atribuirle resultados de rendimiento que no se han medido.
