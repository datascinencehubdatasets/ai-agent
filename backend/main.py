from fastapi import FastAPI
from backend.routers import intents
from backend.routers import router as processing_router

app = FastAPI(title="Zaman AI — Intent/Router Service", version="0.2.0")
app.include_router(intents.router)
app.include_router(processing_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
