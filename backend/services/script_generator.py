import os
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv
from backend.services.influencer_matcher import get_influencer_info

# Load environment variables
load_dotenv()

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-49dfb59037de4294a0fc5291cc01768e")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_video_ideas(influencer: str, industry: str, company_data: List[str]) -> List[Dict[str, str]]:
    """
    Generate video ideas based on the matched influencer, industry, and company data.
    
    Args:
        influencer: The matched influencer name
        industry: The user's industry
        company_data: List of bullet points with company information
        
    Returns:
        List of dictionaries with video ideas (title and description)
    """
    try:
        # Get influencer style information
        influencer_info = get_influencer_info(influencer)
        
        # Prepare company data as text
        company_data_text = "\n".join([f"- {item}" for item in company_data])
        
        # Create prompt for DeepSeek
        prompt = f"""
        Generate 3 viral video ideas for a {industry} company that align with {influencer}'s content style ({influencer_info['style']}).
        
        About the company:
        {company_data_text}
        
        For each idea, provide:
        1. A catchy, clickable title (under 60 characters)
        2. A brief description (1-2 sentences) explaining the concept
        
        The ideas should be original, engaging, and have viral potential while showcasing the company's strengths.
        """
        
        # Call DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a creative social media strategist specializing in viral tech content."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Process the response
            ideas = _parse_ideas_from_response(text)
            return ideas
        else:
            print(f"DeepSeek API error: {response.text}")
            return _get_mock_video_ideas(influencer)
    
    except Exception as e:
        print(f"Error generating video ideas: {str(e)}")
        return _get_mock_video_ideas(influencer)

def generate_script(idea: Dict[str, str], influencer: str, company_data: List[str]) -> Dict[str, str]:
    """
    Generate a video script based on a video idea, the matched influencer, and company data.
    
    Args:
        idea: Dictionary with video idea (title and description)
        influencer: The matched influencer name
        company_data: List of bullet points with company information
        
    Returns:
        Dictionary with script content and notes
    """
    try:
        # Get influencer style information
        influencer_info = get_influencer_info(influencer)
        
        # Prepare company data as text
        company_data_text = "\n".join([f"- {item}" for item in company_data])
        
        # Create prompt for DeepSeek
        prompt = f"""
        Write a 150-200 word script for a viral tech video with the title "{idea['title']}" in the style of {influencer} ({influencer_info['style']}).
        
        About the company:
        {company_data_text}
        
        Video concept:
        {idea['description']}
        
        Include:
        1. The actual script that would be spoken on camera (150-200 words)
        2. Delivery notes (how to present, tone, energy level)
        3. Editing notes (pacing, visual elements, b-roll suggestions)
        
        The script should capture {influencer}'s unique style and voice while being engaging and shareable.
        """
        
        # Call DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are {influencer}, a tech content creator with a {influencer_info['style']} style."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 700,
            "temperature": 0.7
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Process the response
            script = _parse_script_from_response(text)
            return script
        else:
            print(f"DeepSeek API error: {response.text}")
            return _get_mock_script(idea, influencer)
    
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        return _get_mock_script(idea, influencer)

def _parse_ideas_from_response(text: str) -> List[Dict[str, str]]:
    """
    Parse the raw response from DeepSeek into structured video ideas.
    
    Args:
        text: The raw text response
        
    Returns:
        List of dictionaries with video ideas
    """
    ideas = []
    lines = text.split("\n")
    
    current_title = None
    current_description = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a new idea (usually starts with a number or has "Title:" in it)
        if line[0].isdigit() and line[1] in ['.', ')'] or "Title:" in line or "TITLE:" in line:
            # Save previous idea if exists
            if current_title:
                ideas.append({
                    "title": current_title,
                    "description": " ".join(current_description)
                })
                current_description = []
                
            # Extract new title
            if ":" in line:
                current_title = line.split(":", 1)[1].strip()
            else:
                # Remove any leading number and punctuation
                import re
                current_title = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                
        # Check if this is a description
        elif current_title and ("Description:" in line or "DESCRIPTION:" in line):
            desc_part = line.split(":", 1)[1].strip()
            current_description.append(desc_part)
        # If we have a title but not explicitly a description, consider it part of description
        elif current_title and len(ideas) < 3:
            current_description.append(line)
    
    # Add the last idea
    if current_title and len(ideas) < 3:
        ideas.append({
            "title": current_title,
            "description": " ".join(current_description)
        })
    
    # Ensure we have exactly 3 ideas
    while len(ideas) < 3:
        ideas.append({
            "title": f"Viral Tech Idea #{len(ideas) + 1}",
            "description": "A creative video concept showcasing your technology's unique value proposition."
        })
    
    return ideas[:3]

def _parse_script_from_response(text: str) -> Dict[str, str]:
    """
    Parse the raw response from DeepSeek into a structured script.
    
    Args:
        text: The raw text response
        
    Returns:
        Dictionary with script content and notes
    """
    script = {
        "content": "",
        "delivery_notes": "",
        "editing_notes": ""
    }
    
    current_section = "content"
    sections = []
    
    # First, try to split by clear section headers
    if "SCRIPT:" in text or "Script:" in text:
        for part in text.split("\n\n"):
            part = part.strip()
            if not part:
                continue
                
            if part.upper().startswith("SCRIPT:") or part.capitalize().startswith("Script:"):
                sections.append(("content", part.split(":", 1)[1].strip()))
            elif part.upper().startswith("DELIVERY") or part.capitalize().startswith("Delivery"):
                sections.append(("delivery_notes", part.split(":", 1)[1].strip()))
            elif part.upper().startswith("EDITING") or part.capitalize().startswith("Editing"):
                sections.append(("editing_notes", part.split(":", 1)[1].strip()))
            else:
                # If no clear header but we have sections already, add to the last section
                if sections:
                    last_section = sections[-1][0]
                    sections.append((last_section, part))
                else:
                    sections.append(("content", part))
    else:
        # If no clear section headers, try a more heuristic approach
        parts = text.split("\n\n")
        
        # Longest part is probably the script content
        longest_part = max(parts, key=len)
        sections.append(("content", longest_part))
        
        # Look for delivery and editing notes in other parts
        for part in parts:
            if part == longest_part:
                continue
                
            if "delivery" in part.lower() or "tone" in part.lower() or "energy" in part.lower():
                sections.append(("delivery_notes", part))
            elif "editing" in part.lower() or "visual" in part.lower() or "b-roll" in part.lower():
                sections.append(("editing_notes", part))
    
    # Combine all parts of each section
    for section_type, content in sections:
        if script[section_type]:
            script[section_type] += "\n\n" + content
        else:
            script[section_type] = content
    
    # If we still don't have all sections, provide defaults
    if not script["delivery_notes"]:
        script["delivery_notes"] = "Speak with confidence and energy. Maintain eye contact with the camera and use hand gestures to emphasize key points."
        
    if not script["editing_notes"]:
        script["editing_notes"] = "Use fast cuts between points. Add relevant b-roll to illustrate concepts. Include text overlays for key statistics or points."
    
    return script

def _get_mock_video_ideas(influencer: str) -> List[Dict[str, str]]:
    """
    Generate mock video ideas for demonstration purposes.
    
    Args:
        influencer: The matched influencer name
        
    Returns:
        List of dictionaries with mock video ideas
    """
    influencer_info = get_influencer_info(influencer)
    style = influencer_info["style"]
    
    if "challenge" in style.lower() or "MrBeast" == influencer:
        return [
            {
                "title": "I Challenged My Team to 10X Our Conversion Rate",
                "description": "A challenge-based video showing the extreme tactics used to dramatically improve conversion rates, with a surprising twist at the end."
            },
            {
                "title": "We Built a Game-Changing Feature in Just 24 Hours",
                "description": "A time-pressured challenge to create something innovative and record-breaking with your team."
            },
            {
                "title": "Giving Away Our Product to Anyone Who Can Beat Me",
                "description": "A competition-style video where you challenge users to complete tasks with your product for a reward."
            }
        ]
    elif "analytical" in style.lower() or "Marques" in influencer or "Kallaway" == influencer:
        return [
            {
                "title": "The Hidden Feature That Changes Everything",
                "description": "An in-depth analysis of a overlooked feature that provides exceptional value to users."
            },
            {
                "title": "Why This Tech Solution Outperforms Everything Else",
                "description": "A data-driven comparison showing how your technology achieves superior results compared to alternatives."
            },
            {
                "title": "The Future of [Industry] is Already Here",
                "description": "A forward-looking analysis of how your technology is advancing the industry in unexpected ways."
            }
        ]
    else:
        return [
            {
                "title": "How We Solved Our Biggest Customer Problem",
                "description": "A storytelling journey about identifying a critical pain point and developing an innovative solution."
            },
            {
                "title": "The Secret Feature Our Competitors Don't Want You To Know",
                "description": "A reveal-style video highlighting a unique advantage that sets your product apart."
            },
            {
                "title": "Why Most [Industry] Tools Fail (And How We're Different)",
                "description": "A contrarian perspective on industry problems and how your approach solves them."
            }
        ]

def _get_mock_script(idea: Dict[str, str], influencer: str) -> Dict[str, str]:
    """
    Generate a mock script for demonstration purposes.
    
    Args:
        idea: Dictionary with video idea
        influencer: The matched influencer name
        
    Returns:
        Dictionary with mock script content and notes
    """
    title = idea["title"]
    
    if "MrBeast" == influencer:
        return {
            "content": f"What's up guys! Today we're doing something INSANE! {title}! That's right - we're pushing the limits and seeing just how far we can go. I've challenged my entire team to work non-stop on this, and we're putting $10,000 on the line to make it happen! You won't BELIEVE the results we got. We literally changed the game overnight! Watch till the end to see the SHOCKING outcome that even I didn't expect!",
            "delivery_notes": "Ultra high energy throughout. Wide eyes, big gestures. Emphasize key words with volume changes. Speak faster than normal conversation. Use shocked expressions when mentioning results.",
            "editing_notes": "Fast cuts, no clip longer than 3 seconds. Use dramatic zoom effects on key points. Add impact sound effects. Include countdown timer on screen. Show team reactions. Use bright, colorful text overlays for statistics and key numbers."
        }
    elif "Marques" in influencer:
        return {
            "content": f"So, {title}. I've been testing this for about two weeks now, and there are some interesting things to unpack here. What makes this particularly noteworthy is the attention to detail in solving a real problem that users face every day. The technology uses a unique approach that actually improves efficiency by 30% according to my tests. That's significantly better than anything else I've seen in this space. Let's break down why this works and what it means for the industry going forward.",
            "delivery_notes": "Calm, measured pace. Maintain professional but conversational tone. Use subtle hand gestures to emphasize key points. Take slight pauses before revealing important data or conclusions.",
            "editing_notes": "Clean, minimalist visual style. Use split-screen comparisons for before/after. Include close-up b-roll of the product in use. Add simple animated graphics for statistics. Maintain consistent color grading with slightly increased contrast."
        }
    else:
        return {
            "content": f"Listen up. {title} - and I'm not exaggerating when I say this could completely transform your results. Here's the reality most people miss: the standard approach in this industry is fundamentally flawed. We discovered this when working with clients who were struggling despite doing everything 'right.' The solution wasn't adding more complexity - it was stripping everything back to focus on the core value delivery. This approach generated a 43% improvement in outcomes across all our test cases. I'm going to show you exactly how this works and why it matters.",
            "delivery_notes": "Direct, confident delivery. Maintain strong eye contact with camera. Speak with authority and conviction. Use deliberate pacing with strategic pauses after important points. Gesture purposefully to emphasize key concepts.",
            "editing_notes": "Simple, distraction-free background. Use text overlays for key statistics and frameworks. Include brief customer testimonial clips. Add subtle zoom effects during important revelations. Include a clear call-to-action at the end."
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