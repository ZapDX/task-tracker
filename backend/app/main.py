from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import tasks

# Membuat tabel otomatis saat aplikasi dijalankan
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GLI Task Tracker API",
    description="REST API untuk Simple Task/Project Tracker",
    version="1.0.0"
)

# Konfigurasi CORS agar Frontend Vue 3 dapat mengakses API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan endpoint /tasks
app.include_router(tasks.router)

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "GLI Task Tracker API is running"}