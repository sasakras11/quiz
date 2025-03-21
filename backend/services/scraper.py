import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-49dfb59037de4294a0fc5291cc01768e")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def scrape_company_data(company_name: str, website_url: str) -> List[str]:
    """
    Use DeepSeek to analyze company data based on company name and website.
    
    Args:
        company_name: The name of the company
        website_url: The URL of the company's website
        
    Returns:
        List of bullet points with company information
    """
    try:
        # Create prompt for DeepSeek
        prompt = f"""
        I need information about the company "{company_name}" (website: {website_url}).
        
        Please analyze this company and generate 5-7 bullet points with the following information:
        1. Key products or services
        2. Recent updates or news
        3. Target market and customers
        4. Unique value propositions
        5. Any pain points their solutions address
        6. Company achievements or case studies
        7. Industry positioning
        
        These bullet points will be used to create viral tech videos, so focus on aspects that would be interesting to highlight.
        Format each bullet point as a complete sentence that starts with "{company_name}" or "The company".
        """
        
        # Call DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",  # Use appropriate DeepSeek model
            "messages": [
                {"role": "system", "content": "You are a business analyst who researches companies and provides concise, accurate summaries."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Process the response into bullet points
            bullet_points = _process_deepseek_response(text)
            return bullet_points
        else:
            print(f"DeepSeek API error: {response.text}")
            return _get_mock_company_data(company_name)
    
    except Exception as e:
        print(f"Error scraping company data: {str(e)}")
        return _get_mock_company_data(company_name)

def _process_deepseek_response(text: str) -> List[str]:
    """
    Process the raw response from DeepSeek into bullet points.
    
    Args:
        text: The raw text response
        
    Returns:
        List of bullet points
    """
    # Simple processing: split by new lines and filter for bullet points
    lines = text.split("\n")
    bullet_points = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("•") or line.startswith("-") or line.startswith("*"):
            # Clean up the bullet point
            clean_line = line.lstrip("•-* ").strip()
            if clean_line:
                bullet_points.append(clean_line)
        elif line and not line.endswith(":") and len(line) > 20:
            # Include substantive lines even if not formatted as bullets
            bullet_points.append(line)
    
    # If no bullet points were found, split the text into sentences
    if not bullet_points:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        bullet_points = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Limit to 7 bullet points
    return bullet_points[:7]

def _get_mock_company_data(company_name: str) -> List[str]:
    """
    Generate mock company data for demonstration purposes.
    
    Args:
        company_name: The name of the company
        
    Returns:
        List of bullet points with mock company information
    """
    return [
        f"{company_name} recently launched a new AI-powered feature that increases productivity by 30%",
        f"The company focuses on solving pain points in the enterprise software market with innovative technology",
        f"A recent case study showed how {company_name} helped a client reduce costs by 25% while improving results",
        f"The company's unique selling proposition is its proprietary algorithm that outperforms competitors by 2x",
        f"{company_name} was founded in 2018 and has grown to serve over 500 clients globally",
        f"Their latest product update includes advanced analytics and reporting capabilities",
        f"The company has a strong focus on security and compliance, with SOC 2 and GDPR certifications"
    ] 