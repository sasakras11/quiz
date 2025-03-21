from typing import Dict, List, Tuple, Any

# Influencer data
INFLUENCERS = {
    "MrBeast": {
        "style": "High-energy, bold, challenge-driven",
        "description": "Known for ambitious challenges and stunts with a positive and high-energy approach."
    },
    "Gary Vee": {
        "style": "Motivational, no-nonsense, action-oriented",
        "description": "Direct and authentic style focused on hustle, entrepreneurship, and taking action."
    },
    "Marques Brownlee": {
        "style": "Chill, analytical, tech-focused",
        "description": "Calm, detailed, and methodical approach to explaining technology concepts."
    },
    "Alex Hormozi": {
        "style": "Direct, no-fluff, value-driven",
        "description": "Straightforward business advice with a focus on value creation and efficiency."
    },
    "Steven Bartlett": {
        "style": "Relatable, storytelling-focused",
        "description": "Connects with audience through personal stories and deep conversations."
    },
    "Mino": {
        "style": "Chaotic, bro-y, relatable",
        "description": "Energetic, sometimes chaotic delivery with relatable personality."
    },
    "Dan Toomey": {
        "style": "Sarcastic, humorous, corporate-focused",
        "description": "Uses humor and sarcasm to comment on corporate culture and business."
    },
    "Corporate Natalie": {
        "style": "Sarcastic, self-aware, corporate satire",
        "description": "Satirical take on corporate life with a female perspective."
    },
    "Corporate Bro": {
        "style": "Humorous, bro-y, corporate satire",
        "description": "Comedy skits about sales, business, and corporate dynamics with a male perspective."
    },
    "Kallaway": {
        "style": "Analytical, tech-savvy, visionary",
        "description": "Forward-thinking analysis of technology trends and business innovation."
    }
}

def get_influencer_info(influencer: str) -> Dict[str, str]:
    """
    Get influencer style information and characteristics
    """
    influencer_styles = {
        "Hormozi": {
            "style": "direct, strategic, no-fluff",
            "tone": "authoritative",
            "pacing": "medium",
            "characteristics": [
                "Value-first delivery",
                "Direct business insights",
                "Clear actionable steps"
            ]
        },
        "MrBeast": {
            "style": "high-energy, challenge-based, dramatic",
            "tone": "excited",
            "pacing": "fast",
            "characteristics": [
                "Big challenges",
                "Dramatic reveals",
                "High stakes content"
            ]
        },
        "GaryVee": {
            "style": "motivational, raw, unfiltered",
            "tone": "passionate",
            "pacing": "fast",
            "characteristics": [
                "Motivational messages",
                "Raw authenticity",
                "Direct audience engagement"
            ]
        },
        "Casey": {
            "style": "narrative-driven, visual, personal",
            "tone": "storytelling",
            "pacing": "dynamic",
            "characteristics": [
                "Strong visual storytelling",
                "Personal experiences",
                "Journey-based content"
            ]
        },
        "Emma": {
            "style": "casual, authentic, relatable",
            "tone": "conversational",
            "pacing": "natural",
            "characteristics": [
                "Genuine reactions",
                "Casual vlogging",
                "Relatable experiences"
            ]
        },
        "Lilly": {
            "style": "comedic, energetic, entertaining",
            "tone": "upbeat",
            "pacing": "quick",
            "characteristics": [
                "Comedy sketches",
                "Character-based content",
                "Entertaining education"
            ]
        }
    }
    
    return influencer_styles.get(influencer, {
        "style": "professional, balanced",
        "tone": "neutral",
        "pacing": "moderate",
        "characteristics": ["Standard presentation"]
    })

def match_influencer(quiz_answers: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
    """
    Match user with an influencer based on quiz answers
    """
    scores = {
        "Hormozi": 0,
        "MrBeast": 0,
        "GaryVee": 0,
        "Casey": 0,
        "Emma": 0,
        "Lilly": 0
    }
    
    # Example scoring based on quiz answers
    for answer in quiz_answers:
        question_id = answer["question_id"]
        response = answer["answer"]
        
        if question_id == 1:  # Content Style Preference
            if response == "A":  # Direct and educational
                scores["Hormozi"] += 2
            elif response == "B":  # Big and dramatic
                scores["MrBeast"] += 2
            elif response == "C":  # Raw and motivational
                scores["GaryVee"] += 2
                
        elif question_id == 2:  # Presentation Style
            if response == "A":  # Professional and structured
                scores["Hormozi"] += 2
            elif response == "B":  # Casual and relatable
                scores["Emma"] += 2
            elif response == "C":  # Entertaining and funny
                scores["Lilly"] += 2
                
        # ... more scoring logic for other questions ...
    
    # Find the best match
    matched_influencer = max(scores.items(), key=lambda x: x[1])[0]
    return matched_influencer, get_influencer_info(matched_influencer)

def get_influencer_info(influencer_name: str) -> Dict:
    """
    Get the detailed information about an influencer.
    
    Args:
        influencer_name: Name of the influencer
        
    Returns:
        Dictionary with influencer information
    """
    return INFLUENCERS.get(influencer_name, {
        "style": "Unknown",
        "description": "Influencer not found"
    }) 