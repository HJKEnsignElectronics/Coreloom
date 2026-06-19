# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import api
import os

# Initialize FastAPI App
app = FastAPI(
    title="CoreLoom API",
    description="Distributed Compute Virtualization and Resource Provisioning Framework",
    version="1.0.0"
)

# Configure CORS for Frontend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API Router
app.include_router(api.router)

# Mount Frontend Static Files (Create a 'frontend' folder with index.html)
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
