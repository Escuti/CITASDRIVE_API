from datetime import date, time
from pydantic import BaseModel

class Appoint(BaseModel):
    fecha_cita: date
    hora_inicio: time
    hora_fin: time
    doc_asig: str
    pacienteFK: int