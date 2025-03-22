from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import os
import asyncio
from dotenv import load_dotenv
from services.scraper import scrape_company_data, normalize_url
from services.script_generator import (
    generate_video_ideas, 
    generate_script,
    generate_scripts_parallel,
    generate_all_content  # Add this import
)
from services.influencer_matcher import match_influencer
from database import init_db
import logging
import time
from contextlib import asynccontextmanager
from utils.timing import Timer

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add this after the logging configuration
@asynccontextmanager
async def time_endpoint(name: str):
    """Async context manager for timing endpoint execution"""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"⏱️ {name} took {duration:.2f} seconds")

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Viral Tech Video Script Generator API")

# Initialize database
init_db()

# Configure CORS - allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug middleware
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

# Debug endpoint
@app.get("/debug")
async def debug():
    return {"status": "ok", "message": "Debug endpoint reached"}

# Models
class CompanyInfo(BaseModel):
    name: str
    website_url: str

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

# Cache for company data
company_data_cache = {}

@app.post("/api/pre-fetch-company")
async def pre_fetch_company(company_info: CompanyInfo):
    """Pre-fetch company data as soon as user enters company details"""
    try:
        # Normalize URL
        normalized_url = normalize_url(company_info.website_url)
        cache_key = f"{company_info.name}:{normalized_url}"

        # Check cache first
        if cache_key in company_data_cache:
            return {"status": "cached", "message": "Company data already fetched"}

        # Start fetching in background
        company_data_cache[cache_key] = asyncio.create_task(
            scrape_company_data(company_info.name, normalized_url)
        )

        return {"status": "fetching", "message": "Started fetching company data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Routes
@app.get("/api/quiz-questions")
async def get_quiz_questions():
    try:
        return {
            "questions": [
                {
                    "id": 1,
                    "text": "What's your industry?",
                    "options": [
                        {"value": "A", "text": "Tech"},
                        {"value": "B", "text": "SaaS"},
                        {"value": "C", "text": "E-commerce"},
                        {"value": "D", "text": "Finance"},
                        {"value": "E", "text": "Healthcare"},
                        {"value": "F", "text": "Education"},
                        {"value": "G", "text": "Other"}
                    ]
                },
                {
                    "id": 2,
                    "text": "How would you describe your communication style?",
                    "options": [
                        {"value": "A", "text": "Direct and bold"},
                        {"value": "B", "text": "Analytical and methodical"},
                        {"value": "C", "text": "Storytelling and relatable"},
                        {"value": "D", "text": "Humorous and entertaining"},
                        {"value": "E", "text": "Casual and conversational"}
                    ]
                },
                {
                    "id": 3,
                    "text": "What's your approach to content creation?",
                    "options": [
                        {"value": "A", "text": "High-energy and attention-grabbing"},
                        {"value": "B", "text": "Educational and informative"},
                        {"value": "C", "text": "Thought-provoking and insightful"},
                        {"value": "D", "text": "Authentic and personal"},
                        {"value": "E", "text": "Quick and to-the-point"}
                    ]
                },
                {
                    "id": 4,
                    "text": "What do you value most in content?",
                    "options": [
                        {"value": "A", "text": "Entertainment value"},
                        {"value": "B", "text": "Practical usefulness"},
                        {"value": "C", "text": "Emotional connection"},
                        {"value": "D", "text": "Unique perspective"},
                        {"value": "E", "text": "Clear communication"}
                    ]
                },
                {
                    "id": 5,
                    "text": "How would you handle talking about technical details?",
                    "options": [
                        {"value": "A", "text": "Simplify with analogies and examples"},
                        {"value": "B", "text": "Deep dive into the specifics"},
                        {"value": "C", "text": "Focus on benefits and outcomes"},
                        {"value": "D", "text": "Use humor to make it digestible"},
                        {"value": "E", "text": "Compare with familiar concepts"}
                    ]
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Replace the old time_endpoint with Timer usage
@app.post("/api/submit-quiz")
async def submit_quiz(quiz_data: dict):
    try:
        # Validate required fields
        if not quiz_data.get("user_info"):
            raise ValueError("Missing user_info in request")
            
        user_info = quiz_data["user_info"]
        required_fields = ["company_name", "website_url"]
        missing_fields = [field for field in required_fields if not user_info.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        start_time = time.time()
        
        # Step 1: Get company data
        async with Timer("Company data scraping") as scraping_timer:
            company_data = await scrape_company_data(
                quiz_data["user_info"]["company_name"],
                quiz_data["user_info"]["website_url"]
            )
        
        # Step 2: Generate all content in parallel
        async with Timer("Content generation") as generation_timer:
            influencer_style = "Motivational, no-nonsense, action-oriented"
            
            # Create one API call that generates both ideas and scripts
            content = await generate_all_content(
                influencer_style=influencer_style,
                industry="Technology",
                company_data=company_data,
                num_ideas=5
            )
        
        total_time = time.time() - start_time
        logger.info(f"✅ Total processing time: {total_time:.2f} seconds")
        
        return {
            "success": True,
            "influencer": "Gary",  # Change from "Gary Vee" to "Gary" to match frontend
            "influencer_style": influencer_style,
            "company_summary": company_data,
            "ideas": content["ideas"],
            "scripts": content["scripts"],
            "timing": {
                "scraping": round(scraping_timer.duration, 2),
                "content_generation": round(generation_timer.duration, 2),
                "total": round(total_time, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in submit_quiz: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)