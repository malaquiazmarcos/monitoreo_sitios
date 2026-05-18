import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks
from sqlmodel import Field, Session, SQLModel, create_engine, select
import httpx

# Definición del modelo de datos
class Site(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    is_online: bool = True

# Configuración de la base de datos
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

# Función para chequear un sitio individual
async def check_site_status(site: Site, session: Session):
    try:
        # Agregamos follow_redirects=True por si el sitio redirige (ej: de http a https)
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(site.url, timeout=10.0)
            # Consideramos online si el código está entre 200 y 299
            site.is_online = (200 <= response.status_code < 300)
            if not site.is_online:
                print(f"--- [DEBUG] {site.name} responded with status: {response.status_code}")
    except Exception as e:
        site.is_online = False
        print(f"--- [DEBUG] Error checking {site.name} ({site.url}): {type(e).__name__} - {e}")
    
    session.add(site)
    session.commit()
    print(f"--- [Loop] Monitoring: {site.name} is {'ONLINE' if site.is_online else 'DOWN'} ---")

# Bucle infinito que chequea todos los sitios cada 60 segundos
async def monitor_all_sites_loop():
    while True:
        print("\n--- Starting automatic check of all sites ---")
        with Session(engine) as session:
            statement = select(Site)
            sites = session.exec(statement).all()
            
            # Chequeamos cada sitio en la base de datos
            for site in sites:
                await check_site_status(site, session)
        
        # Esperamos 60 segundos antes de la próxima vuelta
        await asyncio.sleep(60)

# El 'lifespan' gestiona qué pasa cuando arranca y cuando cierra la app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al arrancar: creamos tablas e iniciamos el bucle de fondo
    SQLModel.metadata.create_all(engine)
    asyncio.create_task(monitor_all_sites_loop())
    yield
    # Al cerrar: aquí podrías limpiar recursos si hiciera falta

app = FastAPI(lifespan=lifespan)

# Endpoint para registrar un nuevo sitio
@app.post("/sites/", response_model=Site)
async def create_site(site: Site):
    with Session(engine) as session:
        session.add(site)
        session.commit()
        session.refresh(site)
        return site

# Endpoint para obtener la lista de todos los sitios
@app.get("/sites/", response_model=List[Site])
async def list_sites():
    with Session(engine) as session:
        sites = session.exec(select(select(Site))).all()
        return sites
