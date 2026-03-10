from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS: str = "http://localhost:3000"
ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,PATCH"
ALLOWED_HEADERS: str = "*"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=["*"],
)

@app.get(
    "/",
    tags=["Root"],
    summary="Page d'accueil de l'API"
)
async def root():
    """Route racine de l'API"""
    return {
        "message": f"wellcome to codeBrain api",
        "version": "v1",
        "status": "operational"
    }


if __name__ == "__name__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4000,
        log_level="info"
    )