from fastapi import FastAPI
from .database import Base, engine
from . import models

# Membuat tabel otomatis saat aplikasi dijalankan
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GLI Task Tracker API")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Database terhubung dan tabel tasks siap!"}