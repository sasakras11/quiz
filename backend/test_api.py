import os
import sys
import requests
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our services
from backend.services.scraper import scrape_company_data
from backend.services.influencer_matcher import match_influencer, get_influencer_info
from backend.services.script_generator import generate_video_ideas, generate_script

# Load environment variables
load_dotenv()

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-49dfb59037de4294a0fc5291cc01768e")

def test_scraper():
    """Test the company data scraper service"""
    print("\n=== Testing Company Data Scraper ===")
    
    company_name = "Acme Tech Solutions"
    website_url = "https://example.com"
    
    print(f"Scraping data for: {company_name}")
    company_data = scrape_company_data(company_name, website_url)
    
    print("\nCompany Data:")
    for item in company_data:
        print(f"- {item}")
    
    return company_data

def test_influencer_matcher():
    """Test the influencer matcher service"""
    print("\n=== Testing Influencer Matcher ===")
    
    # Mock quiz answers
    answers = [
        {"question_id": 1, "answer": "A"},  # Industry: Tech
        {"question_id": 2, "answer": "A"},  # Direct and bold
        {"question_id": 3, "answer": "A"},  # High-energy
        {"question_id": 4, "answer": "A"},  # Entertainment value
        {"question_id": 5, "answer": "C"},  # Focus on benefits
        {"question_id": 6, "answer": "A"},  # Shocked expression
        {"question_id": 7, "answer": "A"},  # Fast-paced
        {"question_id": 8, "answer": "A"},  # Challenge
        {"question_id": 9, "answer": "A"},  # High-energy CTA
        {"question_id": 10, "answer": "A"}  # Double down
    ]
    
    print("Quiz answers pointing to high-energy influencer style")
    influencer, style = match_influencer(answers)
    
    print(f"\nMatched Influencer: {influencer}")
    print(f"Style: {style}")
    
    return influencer

def test_script_generator(influencer, company_data):
    """Test the script generator service"""
    print("\n=== Testing Script Generator ===")
    
    # Generate video ideas
    print(f"Generating video ideas for {influencer} style")
    ideas = generate_video_ideas(influencer, "Tech", company_data)
    
    print("\nVideo Ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea['title']}")
        print(f"   {idea['description']}")
    
    # Generate a script for the first idea
    print("\nGenerating script for the first idea")
    script = generate_script(ideas[0], influencer, company_data)
    
    print("\nScript Content:")
    print(script["content"])
    
    print("\nDelivery Notes:")
    print(script["delivery_notes"])
    
    print("\nEditing Notes:")
    print(script["editing_notes"])

if __name__ == "__main__":
    # Run tests
    company_data = test_scraper()
    influencer = test_influencer_matcher()
    test_script_generator(influencer, company_data) 