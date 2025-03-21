from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from backend.routers import quiz_router
from backend.database import engine, Base

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("DEEPSEEK_API_KEY"):
    print("Warning: DEEPSEEK_API_KEY environment variable not set. Using mock data.")

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Viral Tech Video Script Generator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quiz_router.router, prefix="/api", tags=["quiz"])

# Models
class UserInfo(BaseModel):
    name: str
    company_name: str
    website_url: str
    role: Optional[str] = None

class QuizAnswer(BaseModel):
    question_id: int
    answer: str

class QuizResult(BaseModel):
    user_info: UserInfo
    answers: List[QuizAnswer]

class VideoIdea(BaseModel):
    title: str
    description: str

class Script(BaseModel):
    idea: VideoIdea
    content: str
    delivery_notes: str
    editing_notes: str

class ScriptResponse(BaseModel):
    influencer: str
    influencer_style: str
    company_summary: List[str]
    ideas: List[VideoIdea]
    scripts: List[Script]

# Routes
@app.get("/")
async def root():
    return {"message": "Viral Tech Video Script Generator API"}

@app.post("/match-influencer")
async def match_influencer(quiz_result: QuizResult):
    # This would call the influencer matching service
    return {"influencer": "MrBeast", "style": "High-energy, bold, challenge-driven"}

@app.post("/scrape-company-data")
async def scrape_company_data(user_info: UserInfo):
    # This would call the company data scraping service
    return {"summary": ["Recent product launch addressing pain point X", "Company focuses on Y industry"]}

@app.post("/generate-ideas")
async def generate_ideas(data: dict):
    # This would call the idea generation service
    return {"ideas": [
        {"title": "How We Solved X Problem in Just 24 Hours", "description": "A fast-paced video showing the process of solving a major industry problem."},
        {"title": "I Challenged My Team to Improve Conversion by 50%", "description": "A challenge-based video with high stakes and surprising results."},
        {"title": "The Secret Feature Our Competitors Don't Want You To Know About", "description": "A reveal video highlighting a unique product advantage."}
    ]}

@app.post("/generate-scripts")
async def generate_scripts(data: dict):
    # This would call the script generation service
    return {"scripts": [
        {
            "idea": {"title": "How We Solved X Problem in Just 24 Hours", "description": "A fast-paced video showing the process of solving a major industry problem."},
            "content": "Script content would go here...",
            "delivery_notes": "Speak with high energy, use hand gestures",
            "editing_notes": "Fast cuts, dramatic music, countdown timer on screen"
        }
    ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 