# Monitoreo de Sitios Pro

Este proyecto es un sistema de monitoreo de sitios web que verifica el estado de salud de URLs registradas y envía notificaciones a Discord cuando un sitio cambia de estado.

## Features
- Monitoreo automático cada 10 minutos
- Alertas en Discord cuando un sitio cae o se recupera
- Anti-spam: no repite alertas del mismo estado
- API protegida con API Key

## Arquitectura y Tecnologías

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) para la API y gestión de tareas en segundo plano.
- **Base de Datos:** [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic) con **SQLite**.
- **Cliente HTTP:** [HTTPX](https://www.python-httpx.org/) para peticiones asíncronas.
- **Configuración:** `python-decouple` para manejar variables de entorno en un archivo `.env`.

## Estructura del Proyecto

- `main.py` (raíz): Versión monolítica inicial (legacy).
- `app/`: Nueva estructura modular recomendada.
    - `main.py`: Punto de entrada de la aplicación FastAPI.
    - `models.py`: Definición de modelos de datos (SQLModel).
    - `database.py`: Configuración de la conexión a SQLite.
    - `services.py`: Lógica de monitoreo y alertas.
    - `routers/`: Definición de endpoints de la API.

## Convenciones de Desarrollo

1.  **Async/Await:** Utilizar siempre funciones asíncronas para operaciones de E/S (HTTPX, FastAPI).
2.  **Modelos:** Los modelos deben heredar de `SQLModel` y definir `table=True` para persistencia.
3.  **Monitoreo:** El bucle de monitoreo se ejecuta como una `asyncio.create_task` dentro del `lifespan` de FastAPI.
4.  **Alertas:** Las alertas se envían a través de Discord Webhooks. Evitar el spam; el sistema actual tiene lógica para limitar las notificaciones.

## Configuración Local

1.  Crear un entorno virtual: `python -m venv venv`
2.  Instalar dependencias: `pip install -r requirements.txt`
3.  Configurar el archivo `.env`:
    ```env
    DISCORD_WEBHOOK_URL=tu_webhook_acá
    ADMIN_API_KEY=tu_api_key_acá
    ```
4.  Ejecutar la aplicación (Modular): `fastapi dev app/main.py` o `uvicorn app.main:app --reload`

## Endpoints (Uso Interno)

> **Nota:** Por razones de seguridad y para evitar spam en el canal de alertas de Discord, los endpoints de escritura están protegidos (`X-Admin-Key`) para uso personal. 

- `GET /sites/`: Lista todos los sitios y su estado actual.
- `POST /sites/`: Registra un sitio nuevo.
    - **Header:** `X-Admin-Key: tu_clave_aca`
    - **Body:** `{"name": "Google", "url": "https://google.com"}`
- `POST /sites/bulk/`: Registro masivo de sitios.
    - **Header:** `X-Admin-Key: tu_clave_aca`
    - **Body:** `[{"name": "Site1", "url": "..."}, {"name": "Site2", "url": "..."}]`

