from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import intents
from backend.routers import router as processing_router

app = FastAPI(title="Zaman AI — Intent/Router Service", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(intents.router)
app.include_router(processing_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
