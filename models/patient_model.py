from datetime import date
from pydantic import BaseModel

class Patient(BaseModel):
    tipo_docum: str
    num_docum: str
    nombre: str
    genero: str
    fecha_nacim: date
    num_celular: str