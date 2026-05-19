from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Site(SQLModel, table=True):
    """
    Representa un sitio web bajo monitoreo.
    
    Este modelo persiste tanto el estado de salud actual como el historial de 
    notificaciones para garantizar la entrega de alertas y evitar duplicados.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    is_online: bool = True
    last_notified: Optional[datetime] = Field(default=None)
    last_notified_status: Optional[bool] = Field(default=None)
