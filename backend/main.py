from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import os
import asyncio
from dotenv import load_dotenv
from services.scraper import scrape_company_data, normalize_url
from services.script_generator import generate_video_ideas, generate_script
from services.influencer_matcher import match_influencer
from database import init_db
import logging

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

@app.post("/api/submit-quiz")
async def submit_quiz(quiz_result: QuizResult):
    try:
        # Validate that we have all required answers
        if len(quiz_result.answers) < 5:
            raise HTTPException(status_code=400, detail="Please answer all questions")

        # Get industry from first quiz answer
        industry = "Tech"  # Default
        for answer in quiz_result.answers:
            if answer.question_id == 1:  # First question is industry
                industry_options = {
                    "A": "Tech", 
                    "B": "SaaS", 
                    "C": "E-commerce", 
                    "D": "Finance", 
                    "E": "Healthcare", 
                    "F": "Education", 
                    "G": "Other"
                }
                industry = industry_options.get(answer.answer, "Tech")
                break

        # Match influencer based on quiz answers
        influencer, influencer_info = match_influencer(quiz_result.answers)

        # Check if we have pre-fetched company data
        normalized_url = normalize_url(quiz_result.user_info.website_url)
        cache_key = f"{quiz_result.user_info.company_name}:{normalized_url}"
        
        if cache_key in company_data_cache:
            # Get pre-fetched data
            company_summary = await company_data_cache[cache_key]
            # Clean up cache
            del company_data_cache[cache_key]
        else:
            # Fetch data if not pre-fetched
            company_summary = await scrape_company_data(
                quiz_result.user_info.company_name,
                normalized_url
            )

        # Generate video ideas
        video_ideas = await generate_video_ideas(influencer_info["style"], industry, company_summary)

        # Generate scripts concurrently
        script_tasks = [
            generate_script(idea, influencer_info["style"], company_summary)
            for idea in video_ideas[:3]  # Only generate scripts for top 3 ideas
        ]
        scripts = await asyncio.gather(*script_tasks)

        return {
            "influencer": influencer,
            "influencer_style": influencer_info["style"],
            "company_summary": company_summary,
            "ideas": video_ideas,
            "scripts": scripts
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in submit_quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 