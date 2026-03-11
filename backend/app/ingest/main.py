from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from process import search

ALLOWED_ORIGINS = ["http://localhost:3000"]
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
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
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(request: ChatRequest):
    return StreamingResponse(
        search(request.query),
        media_type="text/plain"
    )




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4000,
        log_level="info"
    )