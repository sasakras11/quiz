from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db
from models.models import User, QuizResult, CompanyData, VideoIdea, Script, ScriptResult
from services.influencer_matcher import match_influencer, get_influencer_info
from services.scraper import scrape_company_data
from services.script_generator import generate_video_ideas, generate_script
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Pydantic models for request/response
class UserInfoRequest(BaseModel):
    name: str
    company_name: str
    website_url: str
    role: Optional[str] = None

class QuizAnswerRequest(BaseModel):
    question_id: int
    answer: str

class QuizResultRequest(BaseModel):
    user_info: UserInfoRequest
    answers: List[QuizAnswerRequest]

class VideoIdeaResponse(BaseModel):
    title: str
    description: str

class ScriptResponse(BaseModel):
    content: str
    delivery_notes: str
    editing_notes: str

class FullResultResponse(BaseModel):
    influencer: str
    influencer_style: str
    company_summary: List[str]
    ideas: List[VideoIdeaResponse]
    scripts: List[ScriptResponse]

@router.post("/submit-quiz", response_model=Dict[str, Any])
async def submit_quiz(quiz_result: QuizResultRequest, db: Session = Depends(get_db)):
    """
    Process quiz submission and return influencer match
    """
    try:
        print(f"Received quiz submission with answers: {quiz_result.answers}")  # Debug log
        
        # Extract user info and answers
        user_info = quiz_result.user_info
        answers = quiz_result.answers
        
        print(f"Processing submission for user: {user_info.name} ({user_info.company_name})")  # Debug log
        
        # Create user in database
        db_user = User(
            name=user_info.name,
            company_name=user_info.company_name,
            website_url=user_info.website_url,
            role=user_info.role
        )
        db.add(db_user)
        db.flush()
        print(f"Created user with ID: {db_user.id}")  # Debug log
        
        # Convert Pydantic models to dictionaries for the matcher
        answers_list = [{"question_id": a.question_id, "answer": a.answer} for a in answers]
        print(f"Converted answers to dict format: {answers_list}")  # Debug log
        
        try:
            influencer_name, influencer_style = match_influencer(answers_list)
            print(f"Successfully matched influencer: {influencer_name} with style: {influencer_style}")  # Debug log
        except Exception as e:
            print(f"Error matching influencer: {str(e)}")  # Debug log
            print(f"Answer data that caused error: {answers_list}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to match influencer: {str(e)}")
        
        # Store quiz result in database
        try:
            db_quiz_result = QuizResult(
                user_id=db_user.id,
                answers=answers_list,
                matched_influencer=influencer_name
            )
            db.add(db_quiz_result)
            print(f"Stored quiz result for user {db_user.id}")  # Debug log
        except Exception as e:
            print(f"Error storing quiz result: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to store quiz result: {str(e)}")
        
        # Get industry from first quiz answer
        industry = "Tech"  # Default
        for answer in answers:
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
                print(f"Determined industry: {industry}")  # Debug log
                break
        
        try:
            # Scrape company data
            print(f"Starting company data scraping for {user_info.company_name}")  # Debug log
            company_summary = await scrape_company_data(user_info.company_name, user_info.website_url)
            print(f"Successfully scraped company data: {company_summary[:100]}...")  # Debug log
        except Exception as e:
            print(f"Error scraping company data: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to scrape company data: {str(e)}")
        
        # Store company data in database
        try:
            db_company_data = CompanyData(
                user_id=db_user.id,
                summary=company_summary
            )
            db.add(db_company_data)
            print(f"Stored company data for user {db_user.id}")  # Debug log
        except Exception as e:
            print(f"Error storing company data: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to store company data: {str(e)}")
        
        try:
            # Generate video ideas
            print(f"Generating video ideas for {influencer_name} in {industry}")  # Debug log
            video_ideas = await generate_video_ideas(influencer_name, industry, company_summary)
            print(f"Generated {len(video_ideas)} video ideas")  # Debug log
        except Exception as e:
            print(f"Error generating video ideas: {str(e)}")  # Debug log
            print(f"Input data that caused error - influencer: {influencer_name}, industry: {industry}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to generate video ideas: {str(e)}")
        
        # Create script result in database
        try:
            db_script_result = ScriptResult(
                user_id=db_user.id,
                influencer=influencer_name,
                influencer_style=influencer_style
            )
            db.add(db_script_result)
            db.flush()
            print(f"Created script result with ID: {db_script_result.id}")  # Debug log
        except Exception as e:
            print(f"Error creating script result: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to create script result: {str(e)}")
        
        # Store video ideas in database
        db_ideas = []
        try:
            for i, idea in enumerate(video_ideas):
                db_idea = VideoIdea(
                    script_result_id=db_script_result.id,
                    title=idea["title"],
                    description=idea["description"]
                )
                db.add(db_idea)
                db_ideas.append(db_idea)
            db.flush()
            print(f"Stored {len(db_ideas)} video ideas in database")  # Debug log
        except Exception as e:
            print(f"Error storing video ideas: {str(e)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to store video ideas: {str(e)}")
        
        # Generate scripts for each idea
        scripts = []
        try:
            for i, idea in enumerate(video_ideas):
                print(f"Generating script {i+1}/{len(video_ideas)}")  # Debug log
                script_data = await generate_script(idea, influencer_name, company_summary)
                print(f"Generated script {i+1} with length: {len(script_data['content'])}")  # Debug log
                
                # Store script in database
                db_script = Script(
                    video_idea_id=db_ideas[i].id,
                    content=script_data["content"],
                    delivery_notes=script_data["delivery_notes"],
                    editing_notes=script_data["editing_notes"]
                )
                db.add(db_script)
                scripts.append(script_data)
            print(f"Generated and stored {len(scripts)} scripts")  # Debug log
        except Exception as e:
            print(f"Error generating scripts: {str(e)}")  # Debug log
            print(f"Failed at idea {i+1}: {idea}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Failed to generate scripts: {str(e)}")
        
        try:
            db.commit()
            print("Successfully committed all database changes")  # Debug log
        except Exception as e:
            print(f"Error committing to database: {str(e)}")  # Debug log
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save results to database: {str(e)}")
        
        # Return results
        result = {
            "influencer": influencer_name,
            "influencer_style": influencer_style,
            "company_summary": company_summary,
            "ideas": video_ideas,
            "scripts": scripts
        }
        print("Successfully prepared response")  # Debug log
        return result
    
    except HTTPException as he:
        db.rollback()
        print(f"HTTP Exception occurred: {str(he)}")  # Debug log
        raise he
    except Exception as e:
        db.rollback()
        print(f"Unexpected error in submit_quiz: {str(e)}")  # Debug log
        print(f"Error type: {type(e)}")  # Debug log
        print(f"Error args: {e.args}")  # Debug log
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/quiz-questions")
async def get_quiz_questions():
    """
    Get the quiz questions and options
    """
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
            },
            {
                "id": 6,
                "text": "What would your video thumbnail style be?",
                "options": [
                    {"value": "A", "text": "Shocked expression with bold text"},
                    {"value": "B", "text": "Clean product shot with minimal text"},
                    {"value": "C", "text": "You in action with a clear value prop"},
                    {"value": "D", "text": "Humorous scene or meme format"},
                    {"value": "E", "text": "Before/after demonstration"}
                ]
            },
            {
                "id": 7,
                "text": "What's your preferred video pacing?",
                "options": [
                    {"value": "A", "text": "Fast-paced with lots of cuts"},
                    {"value": "B", "text": "Methodical and measured"},
                    {"value": "C", "text": "Dynamic with storytelling arcs"},
                    {"value": "D", "text": "Unpredictable with pattern interrupts"},
                    {"value": "E", "text": "Conversational with natural flow"}
                ]
            },
            {
                "id": 8,
                "text": "How would you handle criticism or competition?",
                "options": [
                    {"value": "A", "text": "Turn it into a challenge or contest"},
                    {"value": "B", "text": "Analyze it objectively with data"},
                    {"value": "C", "text": "Share the journey and lessons learned"},
                    {"value": "D", "text": "Use humor and self-awareness"},
                    {"value": "E", "text": "Focus on differentiation and unique value"}
                ]
            },
            {
                "id": 9,
                "text": "What would your call-to-action style be?",
                "options": [
                    {"value": "A", "text": "High-energy challenge or dare"},
                    {"value": "B", "text": "Data-backed recommendation"},
                    {"value": "C", "text": "Authentic invitation to connect"},
                    {"value": "D", "text": "Unexpected or humorous twist"},
                    {"value": "E", "text": "Clear and direct value proposition"}
                ]
            },
            {
                "id": 10,
                "text": "You just went viral! What's your first thought?",
                "options": [
                    {"value": "A", "text": "How can I double down on this success?"},
                    {"value": "B", "text": "What metrics can I analyze to understand why?"},
                    {"value": "C", "text": "My authentic story really resonated!"},
                    {"value": "D", "text": "The humor and hook really worked!"},
                    {"value": "E", "text": "Time to make another similar video!"}
                ]
            }
        ]
    }

@router.get("/influencers")
async def get_influencers():
    """
    Get the list of influencers and their styles
    """
    influencers = [
        {"name": "MrBeast", "style": "High-energy, bold, challenge-driven"},
        {"name": "Gary Vee", "style": "Motivational, no-nonsense, action-oriented"},
        {"name": "Marques Brownlee", "style": "Chill, analytical, tech-focused"},
        {"name": "Alex Hormozi", "style": "Direct, no-fluff, value-driven"},
        {"name": "Steven Bartlett", "style": "Relatable, storytelling-focused"},
        {"name": "Mino", "style": "Chaotic, bro-y, relatable"},
        {"name": "Dan Toomey", "style": "Sarcastic, humorous, corporate-focused"},
        {"name": "Corporate Natalie", "style": "Sarcastic, self-aware, corporate satire"},
        {"name": "Corporate Bro", "style": "Humorous, bro-y, corporate satire"},
        {"name": "Kallaway", "style": "Analytical, tech-savvy, visionary"}
    ]
    
    return {"influencers": influencers} 