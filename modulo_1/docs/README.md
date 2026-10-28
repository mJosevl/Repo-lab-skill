# Miniaplicación con Gemini — Gate 1 (Módulo 1)

Entrega del Gate 1 del programa de Especialización en Desarrollo con IA Generativa (Accenture / Skillnest).

La miniaplicación se conecta a la API de Google Gemini, calcula latencia y costo por petición, y valida con un banco de prompts que el modelo responda de forma consistente en formato JSON.

## Estructura del proyecto

```
gate_1/
├── bloque_11/
│   ├── docs/
│   │   └── diagrama_gate1.png             # Diagrama de arquitectura
│   └── src/
│       ├── cliente_gemini.py        # Conexión a la API: armar, enviar y extraer
│       ├── banco.py                 # Banco de 3 prompts con salida JSON
│       ├── test_consistencia.py     # Ejecuta cada prompt 3 veces y registra resultados
│       ├── registro_resultados.json # Evidencia de consistencia
│       └── decision-arquitectura.md # Comparación de modelos y modelo elegido
├── .env.example                     # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## Requisitos previos

- Python 3.10 o superior
- Git
- Una API key de Gemini, que se crea gratis en https://aistudio.google.com/apikey

## Instalación y ejecución

Los pasos 1 a 4 se ejecutan desde la **raíz del repositorio**, donde está este README.

### Paso 1: Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd gate_1
```

### Paso 2: Crear y activar el entorno virtual

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Mac / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Sabrás que funcionó porque aparece `(venv)` al inicio de la línea de comandos.

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar la API key

El archivo `.env` no viene en el repositorio porque contiene la clave privada de cada persona (está excluido en `.gitignore`). Se crea copiando la plantilla:

Windows:

```powershell
Copy-Item .env.example .env
```

Mac / Linux:

```bash
cp .env.example .env
```

Abre el `.env`, reemplaza `aqui va tu llave` por tu API key y **guarda el archivo** (Ctrl+S). Debe quedar así, sin espacios después del `=`:

```
GEMINI_API_KEY=tu_clave_real
```

Opcional: para usar otro modelo, agrega una línea `GEMINI_MODEL=nombre-del-modelo`. Si no la pones, se usa `gemini-3.5-flash-lite`.

### Paso 5: Ejecutar

Entra a la carpeta del código:

```bash
cd bloque_11/src
```

Prueba de conexión, costo y comparación de modelos:

```bash
python cliente_gemini.py      # Mac/Linux: python3 cliente_gemini.py
```

Test de consistencia del banco de prompts:

```bash
python test_consistencia.py   # Mac/Linux: python3 test_consistencia.py
```

Salida esperada del test:

```
[OK] capital_pais: 3/3 ok | prompt=0 infra=0
[OK] es_par: 3/3 ok | prompt=0 infra=0
[OK] colores_primarios: 3/3 ok | prompt=0 infra=0
```

El detalle de cada ciclo queda en `registro_resultados.json`.

## Solución de problemas

**"La ejecución de scripts está deshabilitada en este sistema" (Windows)**
Aparece al activar el entorno virtual. Ejecuta una vez el siguiente comando y vuelve a activar:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**"API key not valid" o todos los ciclos marcan `infra=3`**
El `.env` probablemente no tiene tu clave guardada. Revisa lo que realmente hay en el archivo:

```powershell
Get-Content ../../.env      # Mac/Linux: cat ../../.env
```

Si sigue mostrando el texto de ejemplo, vuelve a pegar tu clave y guarda con Ctrl+S.

**Error 503 en algún modelo de la comparación**
Es un error temporal del servicio de Google. El programa omite ese modelo y sigue con los demás. Puedes volver a ejecutarlo unos minutos después.

**"Invalid requirement: '\ufeff...'" al instalar**
El `requirements.txt` quedó guardado con codificación UTF-8 con BOM. Ábrelo en VS Code y guárdalo como UTF-8 (sin BOM).

## Registro del ensayo de instalación limpia

**Fecha:** 23-10-2026

**Hallazgos y correcciones:**
- `requirements.txt` incluía librerías que el código no usa (algunas solo para Windows, como `pywin32`), porque se había generado con `pip freeze`. Se dejó solo con las 3 librerías que importa el código: `google-genai`, `python-dotenv` y `httpx`.
- `test_consistencia.py` importaba con rutas de otra estructura de carpetas (`bloque_11.src...` y `modulo_1/src`). Se corrigieron los imports para que funcionen desde `bloque_11/src`.
- La API key no quedaba guardada en `.env` porque el archivo no se guardaba desde el editor. Se agregó al README el paso explícito de guardar y un comando para verificarlo.
- Se separó `armar_peticion` de `enviar_peticion`, para que armar, enviar y extraer queden como funciones independientes.

**Resultado:** tras recrear el entorno virtual desde cero e instalar solo con `requirements.txt`, `cliente_gemini.py` y `test_consistencia.py` corren sin errores, y el test da 3/3 en los tres prompts.