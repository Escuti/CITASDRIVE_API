from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import routes_p
from routes.routes import routes_a

app=FastAPI()
app.title="citasdriveAPI"
app.version="0.0.1"
app.description="Servicios para gestión de citas a pacientes"

load_dotenv()

app.include_router(routes_p)
app.include_router(routes_a)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"]
)

@app.get(
    path="/",
    status_code=status.HTTP_200_OK,
    summary="DEFAULT",
    tags=["APP"]
)
def message():
    """ HOME API
    Return:
        Message
    """
    return HTMLResponse("<h1> CITASDRIVE_API </h1>")