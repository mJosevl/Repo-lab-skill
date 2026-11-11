# Bloque 19 · Enrutamiento condicional

## Qué hace
Lee un ticket, decide de qué tipo es y lo manda a la "cola" que corresponde.
Cada cola responde con un rol distinto.

```
ticket ──► clasificador ──► "factoria"       ──► analista de factoría
                         ├► "administracion" ──► administrador
                         ├► "soporte"        ──► soporte de turno
                         └► otra cosa        ──► pide más datos (default)
```

**Analogía:** la mesa de ayuda que hace el triage. Según el tipo de ticket, lo deriva a otro equipo.

## Archivos
| Archivo | Para qué |
|---|---|
| `clasificador.py` | Devuelve una palabra: factoria, administracion o soporte |
| `enrutamiento.py` | Una cadena por categoría + `RunnableBranch` |
| `test_clasificador.py` | Comprueba que " Soporte." quede como "soporte" |
| `test_enrutamiento.py` | Comprueba que cada categoría vaya a su ruta |

## Cómo se corre
```powershell
python -m pytest -v          # pruebas, sin API (6 en verde)
python clasificador.py       # demo: solo clasifica 3 tickets
python enrutamiento.py       # demo: clasifica y responde 4 tickets
```

## Conceptos clave
- **`RunnableBranch`**: el switch/case de LangChain. Gana la primera condición que se cumpla.
- **El último elemento va sin condición**: es el default (como `else`).
- **Normalizar** con `.strip(" .\n").lower()`: si el modelo responde "Soporte.", sin normalizar caería en el default sin avisar.
- **`RunnablePassthrough.assign(categoria=...)`**: agrega la categoría al diccionario sin perder el ticket.
