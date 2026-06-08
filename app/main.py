import asyncio
import json
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from .database import engine
from .models import SQLModel, Site
from .services import monitor_all_sites_loop
from .routers import sites

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas si no existen
    SQLModel.metadata.create_all(engine)
    
    # Carga inicial desde JSON si la DB está vacía (usamos esto para entornos efímeros como Render Free)
    with Session(engine) as session:
        statement = select(Site)
        existing_sites = session.exec(statement).first()
        
        if not existing_sites and os.path.exists("new_sites.json"):
            print("--- [INIT] Database empty, loading sites from new_sites.json ---")
            try:
                with open("new_sites.json", "r") as f:
                    sites_data = json.load(f)
                    for item in sites_data:
                        new_site = Site(name=item["name"], url=item["url"])
                        session.add(new_site)
                    session.commit()
                print(f"--- [INIT] Successfully loaded {len(sites_data)} sites ---")
            except Exception as e:
                print(f"--- [ERROR] Failed to load initial sites: {e} ---")

    # Arrancar monitoreo
    asyncio.create_task(monitor_all_sites_loop())
    yield

app = FastAPI(title="Monitor de Sitios", 
            description="Monitoreo automático de sitios web con alertas en Discord",
            version="1.0.0",
            lifespan=lifespan)

# Incluimos las rutas del módulo sites
app.include_router(sites.router)

@app.get("/ping")
def chequear_estado():
    return {"estado": "ok", "mensaje":"la api esta viva"}