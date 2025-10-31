from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import jobs, scans
from app.routes import sortly_sync
from app.routes import sortly_webhook



# Create all tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Sortly MVP Backend")

# Define allowed frontend origins
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],     # allows OPTIONS, GET, POST, etc.
    allow_headers=["*"],     # allows Content-Type, Authorization, etc.
)

# Routers
app.include_router(jobs.router)
app.include_router(scans.router)
app.include_router(sortly_sync.router)
app.include_router(sortly_webhook.router)


# Root endpoint
@app.get("/")
def root():
    return {"message": "Sortly MVP backend running successfully"}
