import os
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
from urllib.parse import urlparse, urljoin
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def normalize_url(url: str) -> str:
    """Normalize URL by adding scheme if missing"""
    if not url:
        return ""
    
    # Remove any whitespace
    url = url.strip()
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    try:
        # Parse and reconstruct to handle any other issues
        parsed = urlparse(url)
        # Remove any path if it's just '/'
        path = parsed.path if parsed.path != '/' else ''
        # Reconstruct the URL
        normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"
        
        # Final validation
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        return normalized
    except Exception as e:
        logger.error(f"Error normalizing URL {url}: {str(e)}")
        return f"https://{url}"  # Return best effort URL instead of raising error

async def scrape_company_data(company_name: str, website_url: str) -> List[str]:
    """Scrape company data from website and generate summary"""
    logger.info(f"Scraping data for {company_name} from {website_url}")
    
    try:
        if not DEEPSEEK_API_KEY:
            logger.error("DeepSeek API key not configured")
            raise Exception("DeepSeek API key not configured")
        
        # Normalize URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        # Fetch website content
        async with aiohttp.ClientSession() as session:
            try:
                logger.info(f"Fetching website content from {website_url}")
                async with session.get(website_url, timeout=10) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch website: {response.status}")
                        return [
                            f"{company_name} is a technology company",
                            "Website data could not be fetched",
                            "Using basic company information"
                        ]
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract text content
                    text_content = []
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                        if tag.string:
                            text_content.append(tag.string.strip())
                    
                    # Clean and join text
                    text = ' '.join(text_content)
                    text = ' '.join(text.split())  # Remove extra whitespace
                    
                    if not text:
                        logger.warning("No text content found on website")
                        return [
                            f"{company_name} is a technology company",
                            "Website content could not be parsed",
                            "Using basic company information"
                        ]
                    
                    logger.info(f"Successfully extracted {len(text)} characters of content")
                    
                    # Generate summary using DeepSeek API
                    prompt = f"""
                    Analyze this company information and create 5 key points about {company_name}:
                    
                    {text[:2000]}  # Limit text length
                    
                    Format the response as a list of 5 clear, concise statements about the company.
                    Each statement should be on a new line and focus on different aspects:
                    1. Core business/mission
                    2. Products/services
                    3. Target market/customers
                    4. Unique value proposition
                    5. Company culture/approach
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
                        "max_tokens": 500
                    }
                    
                    logger.info("Calling DeepSeek API for company analysis")
                    async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers) as api_response:
                        if api_response.status != 200:
                            error_text = await api_response.text()
                            logger.error(f"API request failed with status {api_response.status}: {error_text}")
                            return [
                                f"{company_name} is a technology company",
                                "Could not generate detailed summary",
                                "Using basic company information"
                            ]
                        
                        data = await api_response.json()
                        logger.info("Received response from DeepSeek API")
                        summary = data["choices"][0]["message"]["content"]
                        
                        # Split into list and clean up
                        summary_points = [
                            point.strip().strip('1234567890.-)') 
                            for point in summary.split('\n') 
                            if point.strip()
                        ]
                        
                        logger.info(f"Generated {len(summary_points)} summary points")
                        return summary_points if summary_points else [
                            f"{company_name} is a technology company",
                            "Detailed information not available",
                            "Using basic company information"
                        ]
            
            except asyncio.TimeoutError:
                logger.error("Timeout while fetching website")
                return [
                    f"{company_name} is a technology company",
                    "Website took too long to respond",
                    "Using basic company information"
                ]
            except Exception as e:
                logger.error(f"Error fetching website: {str(e)}")
                return [
                    f"{company_name} is a technology company",
                    f"Error: {str(e)}",
                    "Using basic company information"
                ]
    
    except Exception as e:
        logger.error(f"Error in scrape_company_data: {str(e)}")
        raise

def _process_deepseek_response(text: str) -> List[str]:
    """Process the raw response from DeepSeek into bullet points"""
    if not text:
        return []
    
    # Split by new lines and filter for bullet points
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
        sentences = re.split(r'(?<=[.!?])\s+', text)
        bullet_points = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Limit to 7 bullet points
    return bullet_points[:7]

def _get_mock_company_data(company_name: str) -> List[str]:
    """Generate mock company data for demonstration purposes"""
    return [
        f"{company_name} recently launched a new AI-powered feature that increases productivity by 30%",
        f"The company focuses on solving pain points in the enterprise software market with innovative technology",
        f"A recent case study showed how {company_name} helped a client reduce costs by 25% while improving results",
        f"The company's unique selling proposition is its proprietary algorithm that outperforms competitors by 2x",
        f"{company_name} was founded in 2018 and has grown to serve over 500 clients globally",
        f"Their latest product update includes advanced analytics and reporting capabilities",
        f"The company has a strong focus on security and compliance, with SOC 2 and GDPR certifications"
    ] 