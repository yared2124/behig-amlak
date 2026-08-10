from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import routes_cases, routes_pdf

app = FastAPI(
    title="በህግ አምላክ - Behèg Amlak",
    description="Ethiopian Legal AI Assistant powered by RAG and Free LLMs",
    version="1.0.0"
)

# Allow frontend (Vercel/Local) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(routes_cases.router, prefix="/api/v1", tags=["Court Letters"])
app.include_router(routes_pdf.router, prefix="/api/v1", tags=["PDF Export"])

@app.get("/")
async def root():
    return {"message": "Welcome to በህግ አምላክ (Behèg Amlak) - Ethiopian Legal AI"}