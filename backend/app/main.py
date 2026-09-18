import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import router as api_router
from app.utils.config import settings
from app.utils.logger import setup_logging, app_logger

# Setup logging
setup_logging()

app = FastAPI(
    title="AI Customer Service Intelligence & Support Assistant API",
    description="Machine Learning Intent Classification, Sentiment Diagnostics, Knowledge Base Retrieval, and Escalation Engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router)

# Locate Frontend directory
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
)

# Static file serving
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_index():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "AI Customer Service Intelligence API is online. Go to /docs for API documentation."}


@app.get("/health")
async def root_health():
    return {
        "status": "ok",
        "service": "AI Customer Service Intelligence & Support Assistant",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
