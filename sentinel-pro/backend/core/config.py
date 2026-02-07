import os
from dotenv import load_dotenv

# Load environment variables from .env file
# We need to construct the path relative to this file to ensure it works from root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)

# --- Vision Config ---
YOLO_MODEL = "yolov8n-pose.pt"
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
IMG_SIZE = 640

# --- Audio Config ---
AUDIO_RATE = 22050
AUDIO_CHUNK = 1024
AUDIO_BUFFER_SECONDS = 1.0
RMS_THRESHOLD = 0.05
SPECTRAL_CENTROID_THRESHOLD = 2000.0
PANIC_PERSISTENCE = 3

# --- Crowd Density Config ---
CROWD_DENSITY_HIGH = 5
CROWD_DENSITY_MEDIUM = 3

# --- Hardware Config ---
ARDUINO_PORT = "COM3"
ARDUINO_BAUD = 9600

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Database Config ---
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sentinel_db")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}" # Async driver

# --- Models ---
MODELS_DIR = os.path.join(BASE_DIR, "models")
# DB_DIR & DB_PATH are deprecated for Postgres but kept for legacy ref references if any
DB_DIR = os.path.join(BASE_DIR, "db")
AUDIO_MODEL_PATH = os.path.join(BASE_DIR, "engine", "audio", "classifier.pkl")
