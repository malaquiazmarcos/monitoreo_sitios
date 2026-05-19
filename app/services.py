from datetime import datetime, timedelta
import asyncio
import httpx
from sqlmodel import Session, select
from decouple import config
from .models import Site
from .database import engine

DISCORD_WEBHOOK_URL = config("DISCORD_WEBHOOK_URL", default=None)

async def send_discord_alert(site_name: str, site_url: str, status: bool) -> bool:
    """
    Despacha una notificación de estado a Discord vía Webhooks.
    
    Devuelve True solo si la petición fue exitosa (2xx), permitiendo que el 
    llamador gestione la lógica de reintentos en caso de fallos de red o 
    rate-limiting.
    """
    if not DISCORD_WEBHOOK_URL:
        return False

    content = f"🚨 **@everyone: Site DOWN**: {site_name} ({site_url})"
    if status:
        content = f"✅ **Site UP**: {site_name} ({site_url})"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(DISCORD_WEBHOOK_URL, json={"content": content})
            return response.is_success
    except Exception as e:
        print(f"--- [ERROR] Discord alert failed: {e} ---")
        return False

async def check_site_status(site: Site, session: Session):
    """
    Ejecuta la verificación de salud de un sitio y gestiona la lógica de alertas.
    
    Aplica una política de notificaciones basada en cambios de estado y recordatorios 
    periódicos para sitios caídos, asegurando la persistencia del último estado 
    notificado exitosamente para evitar pérdida de información.
    """
    now = datetime.now()
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(site.url, timeout=10.0)
            site.is_online = (200 <= response.status_code < 300)
    except Exception:
        site.is_online = False
    
    should_notify = False
    
    # Caso 1: El estado actual difiere de lo último que avisamos exitosamente
    if site.is_online != site.last_notified_status:
        should_notify = True
    
    # Caso 2: Sigue caído (Recordatorio cada 1 hora)
    elif not site.is_online:
        if site.last_notified is None or (now - site.last_notified) > timedelta(hours=1):
            should_notify = True

    if should_notify:
        alert_sent = await send_discord_alert(site.name, site.url, site.is_online)
        if alert_sent:
            site.last_notified = now
            site.last_notified_status = site.is_online
            print(f"--- [ALERT] Notification sent for {site.name} (Status: {site.is_online}) ---")
        else:
            print(f"--- [RETRY] Notification failed for {site.name}, will retry next loop ---")
    
    session.add(site)
    session.commit()
    print(f"--- [Loop] Monitoring: {site.name} is {'ONLINE' if site.is_online else 'DOWN'} ---")

async def monitor_all_sites_loop():
    """
    Orquestador del bucle de monitoreo automático de alta disponibilidad.
    
    Consulta periódicamente todos los sitios registrados y dispara los chequeos 
    individuales, manteniendo el ciclo de vida de la sesión de base de datos 
    y el intervalo de espera configurado.
    """
    while True:
        print("\n--- Starting automatic check of all sites ---")
        with Session(engine) as session:
            statement = select(Site)
            sites = session.exec(statement).all()
            for site in sites:
                await check_site_status(site, session)
        await asyncio.sleep(600)
