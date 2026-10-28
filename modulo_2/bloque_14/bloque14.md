# Bloque 14: Pruebas unitarias del cliente modular

## ¿Qué hay en este bloque?

Pruebas automáticas que comprueban que el **cliente modular de Gemini** funciona bien.
El cliente modular es el código que construimos antes, dividido en funciones pequeñas
y separadas en lugar de un solo bloque grande.

Estas pruebas **no llaman a la API real de Gemini**. Por eso:

- ✅ No necesitan conexión a internet
- ✅ No gastan tokens (no cuestan dinero)
- ✅ Tardan solo unos segundos
- ✅ Siempre dan el mismo resultado

## Conceptos clave

### ¿Qué es una prueba unitaria?

Es un pequeño programa que revisa **una sola pieza** de tu código (una "unidad",
normalmente una función) y comprueba que hace lo que debe.

Siempre sigue la misma idea:

1. **Preparar**: crear los datos de entrada.
2. **Ejecutar**: llamar a la función.
3. **Comprobar**: verificar que el resultado es el esperado (con `assert`).

### ¿Qué es un mock?

Un **mock** es un **objeto falso** que se hace pasar por uno real.

Piensa en un ensayo de teatro: en vez de usar una espada de verdad, usas una de
cartón. La escena se ensaya igual y nadie corre peligro.

Aquí el mock reemplaza al cliente real de Gemini:

| Cliente real | Mock (falso) |
|---|---|
| Se conecta a internet | No se conecta a nada |
| Gasta tokens y dinero | Gratis |
| La respuesta puede variar | Responde exactamente lo que le digamos |
| Puede fallar por la red | Solo falla si le decimos que falle |

Además, el mock **recuerda cómo lo usaron**: cuántas veces lo llamaron y con
qué datos. Así la prueba puede comprobar, por ejemplo, que se llamó 3 veces.

En Python los mocks vienen en `unittest.mock`:

```python
from unittest.mock import Mock

cliente_falso = Mock()
cliente_falso.models.generate_content.return_value = "respuesta inventada"
```

## Las cuatro funciones que se prueban

### 1. `enviar_peticion`
**Qué hace:** manda el prompt al modelo y devuelve la respuesta.
**Qué se prueba:** que le pasa bien los datos al cliente (modelo, texto) y que
devuelve lo que el cliente respondió.

### 2. `con_reintento`
**Qué hace:** si la petición falla (por ejemplo, un error de red o de límite),
lo vuelve a intentar unas cuantas veces antes de rendirse.
**Qué se prueba:**
- Si funciona a la primera, no reintenta.
- Si falla una o dos veces y luego funciona, devuelve la respuesta buena.
- Si falla siempre, se rinde después del número máximo de intentos y avisa del error.

> Aquí el mock es muy útil: le podemos decir "falla la primera vez y funciona la
> segunda" con `side_effect`, cosa que con la API real no se puede controlar.

### 3. `registrar_costo`
**Qué hace:** calcula cuánto costó la petición a partir de los tokens usados
(entrada y salida) y lo guarda o lo muestra.
**Qué se prueba:** que la cuenta es correcta con números conocidos.
Por ejemplo: si se usaron 1000 tokens a cierto precio, el costo debe ser X.

### 4. `consultar_modelo`
**Qué hace:** es la función "principal". Junta todas las demás: envía la
petición con reintentos y registra el costo.
**Qué se prueba:** que las piezas trabajan bien juntas y que el resultado final
es correcto.

## Cómo encajan las funciones

```
consultar_modelo(prompt)
   │
   ├──> con_reintento( enviar_peticion )   ← pide la respuesta, reintenta si falla
   │
   └──> registrar_costo( tokens usados )   ← calcula cuánto costó
   │
   └──> devuelve la respuesta
```

Como cada función está separada, se puede probar **cada una por su cuenta**.
Esa es la gran ventaja del diseño modular.

## Cómo ejecutar las pruebas

Desde la carpeta del bloque:

```bash
pytest -v
```

`-v` (verbose) muestra el nombre de cada prueba y si pasó (`PASSED`) o falló (`FAILED`).

> No necesitas la API key en el `.env` para estas pruebas, porque no se usa el cliente real.

## Resumen en una frase

> Probamos cada pieza del cliente de Gemini usando un **cliente falso (mock)**,
> así sabemos que nuestro código funciona **sin gastar dinero ni depender de internet**.