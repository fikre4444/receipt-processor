import requests
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_receipt_summary(raw_text: str, total: float | None, date: str | None) -> str:
    """
    Sends data to OpenRouter (DeepSeek/Llama/etc) for summarization.
    """
    if not settings.OPENROUTER_API_KEY:
        return "LLM Summary unavailable (API Key not configured)."

    user_content = f"""
        Act as a financial assistant. Analyze the following receipt text and extracted data.
        
        Extracted Data:
        - Total: {total}
        - Date: {date}
        
        Raw OCR Text:
        {raw_text}
        
        Task:
        1. Identify the Merchant Name (Vendor) (If not available say unknown).
        2. Categorize the expense (e.g., Groceries, Travel, Dining, Office Supplies) (if not possible say could not categorize).
        3. Write a 1-sentence summary of the transaction.
        The whole output shouldn't be no longer than 30 words.
        Format the output as a simple string, do not use Markdown.
        """

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.SITE_URL, 
        "X-Title": settings.SITE_NAME,
    }
    
    data = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": user_content
            }
        ],
        "temperature": 0.3, 
    }

    try:        
        response = requests.post(
            url=url, 
            headers=headers, 
            data=json.dumps(data),
            timeout=10
        )

        response.raise_for_status()
        
        result_json = response.json()
        
        if 'choices' in result_json and len(result_json['choices']) > 0:
            content = result_json['choices'][0]['message']['content']
            
            # The model might include internal tags like <think>...</think>. 
            # This is to strip that out if it exists to keep the UI clean.
            if "<think>" in content:
                content = content.split("</think>")[-1].strip()
                
            return content
        else:
            logger.warning(f"Unexpected API response format: {result_json}")
            return "Summary unavailable (Invalid response format)."

    except requests.exceptions.Timeout:
        logger.error("OpenRouter API timed out.")
        return "Summary unavailable (Timeout)."
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"OpenRouter HTTP Error: {e}")
        return f"Summary unavailable (Provider Error: {response.status_code})"
        
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "Summary generation failed."