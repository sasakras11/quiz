from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company_name = Column(String, index=True)
    website_url = Column(String)
    role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    quiz_results = relationship("QuizResult", back_populates="user")
    company_data = relationship("CompanyData", back_populates="user")
    script_results = relationship("ScriptResult", back_populates="user")

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    answers = Column(JSON)  # Store the full answers array
    matched_influencer = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="quiz_results")

class CompanyData(Base):
    __tablename__ = "company_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    summary = Column(JSON)  # Store the summary as a JSON array of strings
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="company_data")

class VideoIdea(Base):
    __tablename__ = "video_ideas"

    id = Column(Integer, primary_key=True, index=True)
    script_result_id = Column(Integer, ForeignKey("script_results.id"))
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    script_result = relationship("ScriptResult", back_populates="video_ideas")
    scripts = relationship("Script", back_populates="video_idea")

class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    video_idea_id = Column(Integer, ForeignKey("video_ideas.id"))
    content = Column(Text)
    delivery_notes = Column(Text)
    editing_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    video_idea = relationship("VideoIdea", back_populates="scripts")

class ScriptResult(Base):
    __tablename__ = "script_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    influencer = Column(String)
    influencer_style = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="script_results")
    video_ideas = relationship("VideoIdea", back_populates="script_result") 