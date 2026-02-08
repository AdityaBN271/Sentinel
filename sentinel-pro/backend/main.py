import sys
import os
import uvicorn
import socketio
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api import auth, dashboard, analytics
from backend.core.sentinel_hub import hub
from engine.vision.vision_module import VisionEngine
from engine.audio.audio_module import AudioEngine

# Global Engines
vision_thread = None
audio_thread = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("--- Sentinel-Pro Backend Starting ---")
    global vision_thread, audio_thread
    
    # Start Vision
    vision_thread = VisionEngine(source=0)
    vision_thread.start()
    
    # Start Audio
    audio_thread = AudioEngine()
    audio_thread.start()
    
    # Start Keep-Alive / Monitor Loop
    asyncio.create_task(hub.monitor_loop())
    
    yield
    
    # Shutdown
    print("--- Sentinel-Pro Backend Stopping ---")
    if vision_thread:
        vision_thread.stop()
        vision_thread.join()
    if audio_thread:
        audio_thread.stop()
        audio_thread.join()

app = FastAPI(title="Sentinel Pro", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Socket.IO
# Note: In standard uvicorn run, we need to wrap the app or mount it.
# socketio.ASGIApp is a wrapper. We wrap FastAPI with it, OR mount it?
# The recommend pattern is to wrap FastAPI: socketio_app = socketio.ASGIApp(sio, app)
# But main:app expects FastAPI instance for OpenAPI.
# Let's mount at /socket.io
app.mount("/ws", hub.app) # This might be tricky with path stripping
# Standard way: Wrap the whole thing
app_sio = socketio.ASGIApp(hub.sio, app)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
def health_check():
    return {"status": "running", "system": "Sentinel Pro", "gpu": "RTX 2050 (Target)"}

if __name__ == "__main__":
    # We must run 'app_sio' instead of 'app'
    uvicorn.run("backend.main:app_sio", host="0.0.0.0", port=8000, reload=True)
