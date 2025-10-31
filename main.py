from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import jobs, scans, sortly_sync, sortly_webhook

# Create tables (no-op if they already exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sortly MVP Backend")

# ✅ Allowed origins — NO trailing slashes
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Your Vercel production domain (replace if yours is different)
    "https://sortly-x-eargasm-internal-tool.vercel.app",
    # Vercel preview domains (hashes change each deploy)
    "https://sortly-x-eargasm-internal-tool-64zao8r7n-eargasms-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*vercel\.app",   # allow all vercel.app previews
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Routers
app.include_router(jobs.router)
app.include_router(scans.router)
app.include_router(sortly_sync.router)
app.include_router(sortly_webhook.router)

@app.get("/")
def root():
    return {"message": "Sortly MVP backend running successfully"}

# (Optional helper to make some proxies happy with preflight)
@app.options("/jobs")
def options_jobs():
    return {"ok": True}
