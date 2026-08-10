from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import routes_cases

app = FastAPI(
    title="በህግ አምላክ - Behèg Amlak",
    description="Ethiopian Legal AI Assistant powered by RAG and Free LLMs",
    version="1.0.0"
)

# CORS – allow your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_cases.router, prefix="/api/v1", tags=["Court Letters"])

@app.get("/")
async def root():
    return {"message": "Welcome to በህግ አምላክ (Behèg Amlak) - Ethiopian Legal AI"}