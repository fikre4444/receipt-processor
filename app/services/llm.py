import logging
import json
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_summary(self, raw_text: str, total: float | None, date: str | None) -> str:
        """
        Sends data to OpenRouter (DeepSeek/Llama/etc) for summarization.
        """
        if not self.api_key:
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
            The whole output shouldn't be no longer than 60 words.
            Format the output as a simple string, do not use Markdown.
            """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.SITE_URL, 
            "X-Title": settings.SITE_NAME,
        }
        
        data = {
            "model": self.model,
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
                url=self.url, 
                headers=headers, 
                data=json.dumps(data),
                timeout=10
            )

            response.raise_for_status()
            result_json = response.json()
            
            if 'choices' in result_json and len(result_json['choices']) > 0:
                content = result_json['choices'][0]['message']['content']
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
            return f"Summary unavailable (Provider Error: {response.status_code if 'response' in locals() else 'Unknown'})"
            
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "Summary generation failed."
