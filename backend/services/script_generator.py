import os
import logging
import aiohttp
import json
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from .influencer_matcher import get_influencer_info
from utils.timing import Timer  # Replace the Timer import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

async def generate_video_ideas(influencer_style: str, industry: str, company_data: List[str], num_ideas: int = 5) -> List[Dict[str, str]]:
    """Generate video ideas using AI model"""
    try:
        async with Timer("Video Ideas Generation") as timer:
            if not DEEPSEEK_API_KEY:
                logger.error("DeepSeek API key not configured")
                return []
            
            company_info = "\n".join(company_data)
            
            prompt = f"""
            Generate {num_ideas} video content ideas for a {industry} company with this style: {influencer_style}

            Company Information:
            {company_info}

            Format each video idea exactly like this, with 3 asterisks and clear sections:
            **Title:** *"Catchy Title Here"*
            **Concept:** Brief description of the video concept
            **Appeal:** Why this would resonate with the target audience

            Separate each idea with three dashes (---).
            Generate exactly {num_ideas} ideas.
            """
            
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    DEEPSEEK_API_URL,
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                        "max_tokens": 1000
                    }
                )
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error: {error_text}")
                    return []
                
                data = await response.json()
                logger.debug(f"Raw DeepSeek response: {data}")
                
                ideas = parse_deepseek_response(data)
                logger.info(f"Generated {len(ideas)} video ideas")
                for i, idea in enumerate(ideas, 1):
                    logger.info(f"Idea {i}: {idea['title']}")
                
                return ideas
                
    except Exception as e:
        logger.error(f"Error generating video ideas: {e}", exc_info=True)
        return []

async def generate_script(video_idea: Dict[str, str], influencer_style: str, company_data: List[str]) -> str:
    """Generate a video script based on the selected video idea"""
    logger.info(f"Generating script for video: {video_idea.get('title', 'Unknown')}")
    
    try:
        if not DEEPSEEK_API_KEY:
            logger.error("DeepSeek API key not configured")
            raise ValueError("DeepSeek API key not configured")
            
        # Create a detailed prompt for script generation
        prompt = f"""Generate a detailed video script in {influencer_style} style for this video idea:

Title: {video_idea.get('title')}
Concept: {video_idea.get('concept')}
Appeal: {video_idea.get('appeal')}

Company Information:
{chr(10).join(company_data)}

Format the script with these sections:
**Hook:** [Attention-grabbing opening, 2-3 lines]
**Main Points:** [3-5 key points with supporting details]
**Call to Action:** [Clear next steps for viewers]
**Signature Move:** [Unique stylistic element or transition]

Keep the tone motivational and action-oriented."""
        
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 1000
                }
            )
            
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"DeepSeek API error: {error_text}")
                return ""
            
            data = await response.json()
            script_content = data["choices"][0]["message"]["content"]
            
            logger.info("=== Generated Script ===")
            logger.info(script_content)
            logger.info("======================")
            
            return script_content
            
    except Exception as e:
        logger.error(f"Error generating script: {e}", exc_info=True)
        return ""

async def generate_scripts_parallel(ideas: List[Dict[str, str]], influencer_style: str, company_data: List[str]) -> List[str]:
    """Generate multiple scripts in parallel"""
    logger.info(f"Starting parallel script generation for {len(ideas)} ideas")
    
    try:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for idea in ideas:
                task = asyncio.create_task(
                    generate_single_script(session, idea, influencer_style, company_data)
                )
                tasks.append(task)
            
            scripts = await asyncio.gather(*tasks)
            logger.info(f"Successfully generated {len(scripts)} scripts in parallel")
            return scripts
            
    except Exception as e:
        logger.error(f"Error in parallel script generation: {e}", exc_info=True)
        return []

async def generate_single_script(
    session: aiohttp.ClientSession,
    video_idea: Dict[str, str],
    influencer_style: str,
    company_data: List[str]
) -> Dict[str, str]:
    """Generate a single script using shared session"""
    logger.info(f"Generating script for idea: {video_idea.get('title', 'Unknown')}")
    
    try:
        prompt = f"""Generate a detailed video script in {influencer_style} style for this video idea:

Title: {video_idea.get('title')}
Concept: {video_idea.get('concept')}
Appeal: {video_idea.get('appeal')}

Company Information:
{chr(10).join(company_data)}

Format the script with these sections:
**Hook:** [Attention-grabbing opening, 2-3 lines]
**Main Points:** [3-5 key points with supporting details]
**Call to Action:** [Clear next steps for viewers]
**Signature Move:** [Unique stylistic element or transition]

Keep the tone motivational and action-oriented."""

        async with session.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 1000
            }
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"API error for {video_idea.get('title')}: {error_text}")
                return {}
            
            data = await response.json()
            content = data["choices"][0]["message"]["content"]
            
            logger.info(f"Generated script for: {video_idea.get('title')}")
            return {
                "content": content,
                "title": video_idea.get('title'),
                "concept": video_idea.get('concept')
            }
            
    except Exception as e:
        logger.error(f"Error generating script for {video_idea.get('title')}: {e}")
        return {}

async def generate_all_content(
    influencer_style: str,
    industry: str,
    company_data: List[str],
    num_ideas: int = 5
) -> Dict[str, List]:
    """Generate all content in a single API call"""
    logger.info("Starting content generation")
    
    try:
        async with Timer("Content Generation") as timer:
            company_info = "\n".join(company_data)
            
            # Simplified prompt for better response structure
            prompt = f"""Generate {num_ideas} video content ideas with scripts for a {industry} company.
Style: {influencer_style}

Company Information:
{company_info}

For each set, use this exact format:

[SET START]
IDEA:
**Title:** *"Title here"*
**Concept:** Brief concept
**Appeal:** Target appeal

SCRIPT:
**Hook:** Opening hook
**Main Points:**
- Point 1
- Point 2
- Point 3
**Call to Action:** CTA here
**Signature Move:** Unique element
[SET END]

Generate exactly {num_ideas} complete sets."""

            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    DEEPSEEK_API_URL,
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                        "max_tokens": 3000
                    }
                )

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error: {error_text}")
                    return {"ideas": [], "scripts": []}

                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse content using set markers
                sets = content.split("[SET START]")
                ideas = []
                scripts = []

                for set_content in sets:
                    if not set_content.strip():
                        continue

                    # Split into idea and script sections
                    parts = set_content.split("SCRIPT:")
                    if len(parts) != 2:
                        continue

                    idea_text, script_text = parts

                    # Parse idea
                    idea = {}
                    for line in idea_text.split("\n"):
                        line = line.strip()
                        if line.startswith("**Title:**"):
                            idea["title"] = line.replace("**Title:**", "").replace("*", "").strip()
                        elif line.startswith("**Concept:**"):
                            idea["concept"] = line.replace("**Concept:**", "").strip()
                        elif line.startswith("**Appeal:**"):
                            idea["appeal"] = line.replace("**Appeal:**", "").strip()

                    if idea and all(k in idea for k in ["title", "concept", "appeal"]):
                        ideas.append(idea)
                        # Parse script
                        script = {
                            "title": idea["title"],
                            "content": script_text.strip().replace("[SET END]", "")
                        }
                        scripts.append(script)

                logger.info(f"Generated {len(ideas)} content sets")
                for i, idea in enumerate(ideas, 1):
                    logger.info(f"Content Set {i}: {idea['title']}")
                    logger.debug(f"Script {i}: {scripts[i-1]['content'][:100]}...")

                return {"ideas": ideas, "scripts": scripts}

    except Exception as e:
        logger.error(f"Error in generate_all_content: {str(e)}", exc_info=True)
        return {"ideas": [], "scripts": []}

def parse_idea_section(text: str) -> Dict[str, str]:
    """Parse the idea section of the response"""
    idea = {}
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("**Title:**"):
            idea["title"] = line.replace("**Title:**", "").replace("*", "").strip()
        elif line.startswith("**Concept:**"):
            idea["concept"] = line.replace("**Concept:**", "").strip()
        elif line.startswith("**Appeal:**"):
            idea["appeal"] = line.replace("**Appeal:**", "").strip()
    return idea

def parse_script_section(text: str, title: str) -> Dict[str, str]:
    """Parse the script section of the response"""
    return {
        "title": title,
        "content": text.strip()
    }

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

def parse_deepseek_response(data: dict) -> List[Dict[str, str]]:
    """Parse the response from DeepSeek API into structured video ideas"""
    try:
        content = data["choices"][0]["message"]["content"]
        logger.info(f"Raw DeepSeek response:\n{content}")
        
        ideas = []
        current_idea = {}
        
        # Split by triple dashes (---)
        sections = content.split('---')
        
        for section in sections:
            if not section.strip():
                continue
                
            idea = {}
            lines = section.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('**Title:**'):
                    idea['title'] = line.replace('**Title:**', '').replace('*', '').strip()
                elif line.startswith('**Concept:**'):
                    idea['concept'] = line.replace('**Concept:**', '').strip()
                elif line.startswith('**Appeal:**'):
                    idea['appeal'] = line.replace('**Appeal:**', '').strip()
            
            if len(idea) == 3:  # Only add if we have all components
                ideas.append(idea)
        
        logger.info("=== Parsed Video Ideas ===")
        for i, idea in enumerate(ideas, 1):
            logger.info(f"Idea {i}:")
            logger.info(f"  Title: {idea['title']}")
            logger.info(f"  Concept: {idea['concept']}")
            logger.info(f"  Appeal: {idea['appeal']}")
        logger.info("========================")
        
        return ideas
        
    except Exception as e:
        logger.error(f"Error parsing DeepSeek response: {str(e)}")
        return []