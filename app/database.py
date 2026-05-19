from sqlmodel import create_engine, Session
import os
from decouple import config

sqlite_file_name = "database.db"
# La DB estará en la raíz del proyecto
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def get_session():
    """
    Generador de sesiones de base de datos para Inyección de Dependencias.
    
    Asegura que cada petición de la API tenga su propia sesión y que esta se 
    cierre correctamente al finalizar el ciclo de vida del request.
    """
    with Session(engine) as session:
        yield session
