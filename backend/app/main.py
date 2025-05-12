from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database.database import get_db, init_db
from .api.plugin_router import router as plugin_router
from .api.query_router import router as query_router
from .api.conversation_router import router as conversation_router
from .api.ipinfo_router import router as ipinfo_router
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CyberSecurity AI Assistant API",
    description="API for processing cybersecurity queries with AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(plugin_router, prefix="/api/plugins", tags=["plugins"])
app.include_router(query_router, prefix="/api/query", tags=["query"])
app.include_router(conversation_router, prefix="/api/conversations", tags=["conversations"])
app.include_router(ipinfo_router, prefix="/api/ipinfo", tags=["ipinfo"])

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "CyberSecurity AI Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
