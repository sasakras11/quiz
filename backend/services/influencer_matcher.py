from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)

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
    "Dan Toomey": {
        "style": "Sarcastic, humorous, corporate-focused",
        "description": "Uses humor and sarcasm to comment on corporate culture and business."
    },
    "Corporate Natalie": {
        "style": "Sarcastic, self-aware, corporate satire",
        "description": "Satirical take on corporate life with a female perspective."
    }
}

def get_influencer_info(influencer_name: str) -> Dict[str, Any]:
    """
    Get information about an influencer
    Returns dict with style and description
    """
    return INFLUENCERS.get(influencer_name, {
        "style": "Professional and engaging",
        "description": "Default style for unknown influencer"
    })

def match_influencer(quiz_answers: List[Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Match user with an influencer based on quiz answers
    Returns tuple of (influencer_name, influencer_info)
    """
    try:
        # Default to MrBeast if something goes wrong
        default_influencer = "MrBeast"
        default_info = INFLUENCERS[default_influencer]
        
        # Initialize scores for all influencers
        scores = {name: 0 for name in INFLUENCERS.keys()}
        
        # Score based on answers
        for answer in quiz_answers:
            question_id = answer.question_id  # Access as attribute instead of dict key
            choice = answer.answer  # Access as attribute instead of dict key
            
            # Scoring logic based on questions
            if question_id == 2:  # Communication style
                if choice == "A":  # Direct and bold
                    scores["Gary Vee"] += 2
                    scores["Alex Hormozi"] += 2
                elif choice == "B":  # Analytical and methodical
                    scores["Marques Brownlee"] += 2
                elif choice == "C":  # Storytelling and relatable
                    scores["MrBeast"] += 2
                    scores["Steven Bartlett"] += 2
                elif choice == "D":  # Humorous and entertaining
                    scores["Dan Toomey"] += 2
                    scores["Corporate Natalie"] += 2
            
            elif question_id == 3:  # Content creation approach
                if choice == "A":  # High-energy
                    scores["MrBeast"] += 2
                elif choice == "B":  # Educational
                    scores["Marques Brownlee"] += 2
                    scores["Alex Hormozi"] += 1
                elif choice == "C":  # Thought-provoking
                    scores["Gary Vee"] += 2
                    scores["Steven Bartlett"] += 2
                elif choice == "D":  # Authentic
                    scores["Corporate Natalie"] += 2
                elif choice == "E":  # Quick
                    scores["Dan Toomey"] += 2
            
            elif question_id == 4:  # Content value
                if choice == "A":  # Entertainment
                    scores["MrBeast"] += 2
                    scores["Dan Toomey"] += 1
                elif choice == "B":  # Practical
                    scores["Marques Brownlee"] += 2
                    scores["Alex Hormozi"] += 2
                elif choice == "C":  # Emotional
                    scores["Gary Vee"] += 2
                    scores["Steven Bartlett"] += 2
                elif choice == "D":  # Unique
                    scores["Corporate Natalie"] += 2
                elif choice == "E":  # Clear
                    scores["Marques Brownlee"] += 1
                    scores["Alex Hormozi"] += 1
        
        # Find influencer with highest score
        matched_influencer = max(scores.items(), key=lambda x: x[1])[0]
        matched_info = INFLUENCERS[matched_influencer]
        
        return matched_influencer, matched_info
        
    except Exception as e:
        logger.error(f"Error in match_influencer: {str(e)}")
        return default_influencer, default_info 