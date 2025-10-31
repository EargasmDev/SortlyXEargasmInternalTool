from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import jobs, scans, sortly_sync, sortly_webhook

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sortly MVP Backend")

# ✅ Allowed origins (NO trailing slashes)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://sortly-x-eargasm-internal-tool.vercel.app",
    "https://sortly-x-eargasm-internal-tool-64zao8r7n-eargasms-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(scans.router)
app.include_router(sortly_sync.router)
app.include_router(sortly_webhook.router)

@app.get("/")
def root():
    return {"message": "Sortly MVP backend running successfully"}
