import os
import logging
import aiohttp
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from .influencer_matcher import get_influencer_info

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

async def generate_video_ideas(influencer_style: str, industry: str, company_data: List[str], num_ideas: int = 5) -> List[Dict[str, str]]:
    """Generate video ideas based on influencer style and company data"""
    logger.info(f"Generating video ideas for style: {influencer_style}")
    
    try:
        if not DEEPSEEK_API_KEY:
            logger.error("DeepSeek API key not configured")
            # Return mock data if API key is not configured
            return [
                {
                    "title": f"The {industry} Challenge",
                    "concept": "A high-stakes competition where companies compete to solve a real-world problem in 24 hours",
                    "appeal": "Combines entertainment with valuable industry insights"
                },
                {
                    "title": f"Secret Sauce Revealed",
                    "concept": "Behind-the-scenes look at how successful {industry} companies operate",
                    "appeal": "Provides actionable insights while maintaining viewer interest"
                },
                {
                    "title": f"Tech Transformation",
                    "concept": "Dramatic before-and-after reveal of a company's digital transformation",
                    "appeal": "Visual storytelling with clear value proposition"
                }
            ]
        
        company_info = "\n".join(company_data) if isinstance(company_data, list) else str(company_data)
        
        prompt = f"""
        As a content creator with the style of {influencer_style}, generate {num_ideas} unique video ideas 
        for a {industry} company with the following information:
        
        {company_info}
        
        For each idea, provide:
        1. A catchy title
        2. A brief description of the video concept
        3. Why this would appeal to the target audience
        
        Format each idea as a JSON object with these exact keys:
        - title: The video title
        - concept: The video concept
        - appeal: Why it appeals to the audience
        
        Return ONLY a JSON array of these objects, with no additional text or formatting.
        """
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.8,
            "max_tokens": 1000
        }
        
        logger.info("Calling DeepSeek API for video ideas")
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
                    raise Exception(f"Failed to generate video ideas: {error_text}")
                
                data = await response.json()
                logger.info("Received response from DeepSeek API")
                
                try:
                    ideas_text = data["choices"][0]["message"]["content"].strip()
                    # Try to find JSON array in the response
                    start_idx = ideas_text.find("[")
                    end_idx = ideas_text.rfind("]") + 1
                    
                    if start_idx == -1 or end_idx == 0:
                        raise ValueError("Could not find JSON array in response")
                    
                    json_str = ideas_text[start_idx:end_idx]
                    ideas = json.loads(json_str)
                    
                    if not isinstance(ideas, list):
                        raise ValueError("Response is not a list of ideas")
                    
                    # Validate each idea has required fields
                    for idea in ideas:
                        if not all(key in idea for key in ["title", "concept", "appeal"]):
                            raise ValueError("Ideas missing required fields")
                    
                    logger.info(f"Successfully generated {len(ideas)} video ideas")
                    return ideas
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.error(f"Error parsing API response: {str(e)}")
                    # Return mock data on error
                    return [
                        {
                            "title": f"The {industry} Challenge",
                            "concept": "A high-stakes competition where companies compete to solve a real-world problem in 24 hours",
                            "appeal": "Combines entertainment with valuable industry insights"
                        },
                        {
                            "title": f"Secret Sauce Revealed",
                            "concept": "Behind-the-scenes look at how successful {industry} companies operate",
                            "appeal": "Provides actionable insights while maintaining viewer interest"
                        },
                        {
                            "title": f"Tech Transformation",
                            "concept": "Dramatic before-and-after reveal of a company's digital transformation",
                            "appeal": "Visual storytelling with clear value proposition"
                        }
                    ]
    
    except Exception as e:
        logger.error(f"Error in generate_video_ideas: {str(e)}")
        # Return mock data on any error
        return [
            {
                "title": f"The {industry} Challenge",
                "concept": "A high-stakes competition where companies compete to solve a real-world problem in 24 hours",
                "appeal": "Combines entertainment with valuable industry insights"
            },
            {
                "title": f"Secret Sauce Revealed",
                "concept": "Behind-the-scenes look at how successful {industry} companies operate",
                "appeal": "Provides actionable insights while maintaining viewer interest"
            },
            {
                "title": f"Tech Transformation",
                "concept": "Dramatic before-and-after reveal of a company's digital transformation",
                "appeal": "Visual storytelling with clear value proposition"
            }
        ]

async def generate_script(video_idea: Dict[str, str], influencer_style: str, company_data: List[str]) -> str:
    """Generate a video script based on the selected video idea"""
    logger.info(f"Generating script for video: {video_idea.get('title', 'Unknown')}")
    
    try:
        if not DEEPSEEK_API_KEY:
            logger.error("DeepSeek API key not configured")
            raise Exception("DeepSeek API key not configured")
        
        company_info = "\n".join(company_data)
        
        prompt = f"""
        As a content creator with the style of {influencer_style}, write a detailed script for this video idea:
        
        Title: {video_idea.get('title')}
        Concept: {video_idea.get('concept')}
        Target Appeal: {video_idea.get('appeal')}
        
        Company Information:
        {company_info}
        
        Write a complete video script that includes:
        1. Opening hook
        2. Introduction
        3. Main content sections
        4. Call to action
        5. Closing
        
        Format the script with clear section headers and timing estimates.
        Maintain the style and tone of {influencer_style} throughout.
        Focus on engaging delivery and maintaining viewer interest.
        Include any specific catchphrases or signature moves associated with the style.
        """
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        logger.info("Calling DeepSeek API for script generation")
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
                    raise Exception(f"Failed to generate script: {error_text}")
                
                data = await response.json()
                logger.info("Received response from DeepSeek API")
                script = data["choices"][0]["message"]["content"]
                
                logger.info("Successfully generated script")
                return script
    
    except Exception as e:
        logger.error(f"Error in generate_script: {str(e)}")
        raise

def _process_script_sections(text: str) -> Dict[str, str]:
    """Process raw script text into sections"""
    sections = {
        "content": "",
        "delivery_notes": "",
        "editing_notes": ""
    }
    
    current_section = "content"
    lines = text.split("\n")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        lower_line = line.lower()
        if "delivery note" in lower_line:
            current_section = "delivery_notes"
            continue
        elif "editing note" in lower_line:
            current_section = "editing_notes"
            continue
        
        sections[current_section] = sections[current_section] + "\n" + line if sections[current_section] else line
    
    return sections

def _get_mock_video_ideas(industry: str) -> List[str]:
    """Generate mock video ideas"""
    return [
        f'"The {industry} Challenge" - A high-stakes competition where companies compete to solve a real-world problem in 24 hours',
        f'"Secret Sauce Revealed" - Behind-the-scenes look at how successful {industry} companies operate',
        f'"Tech Transformation" - Dramatic before-and-after reveal of a company\'s digital transformation'
    ]

def _get_mock_script(video_idea: str) -> Dict[str, str]:
    """Generate a mock script"""
    return {
        "content": f"Hey guys! Today we're doing something INSANE with {video_idea}! [Dramatic pause] We're going to show you exactly how this works, and trust me, you won't believe the results!",
        "delivery_notes": "High energy throughout. Use dramatic pauses for emphasis. Maintain eye contact with camera.",
        "editing_notes": "Fast cuts between scenes. Add suspenseful music. Use zoom effects for emphasis. Include b-roll of product demos."
    }

def generate_script_prompt(influencer: str, topic: str) -> str:
    """
    Generate a prompt based on influencer style
    """
    info = get_influencer_info(influencer)
    
    if influencer == "Hormozi":
        return f"""
        Create a direct, value-packed script about {topic}.
        Focus on clear actionable insights.
        Use Hormozi's signature style:
        - Start with a hook about the problem
        - Deliver clear, actionable steps
        - End with a powerful value proposition
        """
    
    elif influencer == "MrBeast":
        return f"""
        Create an exciting, challenge-based script about {topic}.
        Focus on dramatic moments and reveals.
        Use MrBeast's signature style:
        - Start with an attention-grabbing challenge
        - Build suspense throughout
        - Include dramatic reveals and twists
        """
    
    # ... similar prompts for other influencers ... 