Límites de la métrica de evaluación 

Interpretación cualitativa de los resultados del Bloque 16 y límites conocidos del pipeline. Datos: modulo_2/bloque_16/resultados_metricas.json.

1. Qué mide

Mide cuántas palabras comparten una respuesta generada y una referencia escrita por mí, después de normalizar el texto (minúsculas, sin puntuación) con procesar_texto del Bloque 15.

Precisión: de lo que dijo el modelo, ¿cuánto aparece en la referencia?
Cobertura: de lo que debía decir, ¿cuánto dijo?
F1: equilibrio entre las dos.

Cuenta repeticiones (Counter), pero no entiende orden, sinónimos ni significado.

2. Resultados reales y lectura humana

Corrida del 2026-10-30, modelo gemini-3.5-flash-lite, 5 preguntas sobre la obra de Isaac Asimov, con la instrucción de responder en una sola oración. Costo total: US$ 0,000317.

Consulta	Prec	Cob	F1	¿Respuesta correcta?
¿Quién escribió Yo, Robot?	0.57	0.80	0.67	✅ Sí
¿En qué año se publicó Yo, Robot?	0.75	1.00	0.86	✅ Sí
¿Cuál es la Primera Ley de la Robótica?	0.43	0.93	0.59	✅ Sí, y más completa que mi referencia
¿Qué es la psicohistoria?	0.52	0.92	0.67	✅ Sí, con contexto extra útil
¿Cómo se llama la robopsicóloga?	0.50	1.00	0.67	✅ Sí
Promedio	0.55	0.93	0.69	5 de 5 correctas

Hallazgo principal: las 5 respuestas son correctas, pero ninguna supera F1 0.86. Leída sola, la métrica sugeriría un cliente mediocre; leyendo las respuestas, el cliente acertó en todo.

Lectura de los peores casos

Primera Ley (F1 0.59, el más bajo). Referencia: "Un robot no debe dañar a un ser humano ni permitir que sufra daño." Respuesta: "...un robot no debe dañar a un ser humano o, por su inacción, permitir que un ser humano sufra daño." La respuesta es más fiel a la ley original que mi referencia (agrega "por su inacción"). La métrica castiga justamente a la respuesta más completa.

¿Quién escribió Yo, Robot? (F1 0.67). Respuesta: "Yo, Robot fue escrita por Isaac Asimov." Mismo hecho en voz pasiva. Las palabras nuevas ("fue", "escrita", "por") bajan la precisión sin que cambie el significado.

Psicohistoria (F1 0.67). La respuesta agrega "combina historia, sociología y matemáticas". Es información correcta y útil, pero como no está en la referencia, cuenta como "sobrante".

3. Modos de falla conocidos

La métrica se equivoca en dos direcciones.

3.1 Subestima respuestas buenas (falsos negativos)
Caso	Ejemplo	F1
Respuesta más larga o completa	Primera Ley con "por su inacción" (real)	0.59
Paráfrasis o voz pasiva	"fue escrita por Isaac Asimov" (real)	0.67
Sinónimos	"El robot es obediente" / "El autómata es dócil"	0.50
3.2 Sobrestima respuestas malas (falsos positivos), el caso más peligroso
Caso	Ejemplo	F1
Dato equivocado (fecha o cifra)	"Yo, Robot se publicó en 1950" / "...en 1977"	0.83
Negación ausente	"Un robot no debe dañar a un humano" / "Un robot debe dañar a un humano"	0.93
Orden invertido (métrica con set, Bloque 15)	"Robbie cuida a Gloria" / "Gloria cuida a Robbie"	1.00

La Primera Ley sin su "no" saca 0.93: casi perfecto para la frase que ordena lo contrario. Ningún F1 alto garantiza que la respuesta sea correcta.

3.3 Límites del propio pipeline
Los separadores numéricos desaparecen: "1.000" queda como "1000".
Se pierden los emojis y los signos ¿ ¡, que en español a veces marcan intención.
Un texto de pura puntuación queda vacío: la métrica devuelve 0.0 en vez de fallar.
El resultado depende de la referencia que escribí: una referencia corta castiga cualquier respuesta detallada.
4. Muestra revisada

5 respuestas generadas el 2026-10-30, todas leídas a mano (el 100 %, no solo los peores casos). Los ejemplos de falsos positivos son casos construidos para probar los límites, y están cubiertos por pruebas en test_metricas.py.

Limitación de la muestra: 5 casos es una muestra pequeña y de un solo tema. Sirve para identificar modos de falla, no para estimar qué tan seguido ocurren.

5. Recomendación de uso
Usar el F1 para comparar en volumen entre versiones del cliente o del prompt, no para decidir si una respuesta individual es correcta.
Mirar precisión y cobertura por separado. En esta corrida, la precisión baja con cobertura alta indica respuestas largas, no respuestas incorrectas.
Revisar siempre a mano cualquier respuesta con fechas, cifras, nombres propios o negaciones.
Leer primero los peores casos (peores_casos), y también una muestra de los mejores, porque ahí se esconden los falsos positivos.
Ajustar la instrucción al formato de la referencia. "Una sola oración" no bastó; las respuestas siguieron siendo más largas que las referencias.

En términos de Asimov: la métrica es como la psicohistoria de Hari Seldon, útil para ver tendencias en la masa e inútil para el caso individual. Para ese caso hace falta alguien que lea, como Susan Calvin.