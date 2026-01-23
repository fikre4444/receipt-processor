import re
import logging
from typing import Optional, Tuple
from dateparser.search import search_dates

logger = logging.getLogger(__name__)

def extract_total(text: str) -> Optional[float]:
    """
    Attempts to find the Total Amount.
    Strategy 1: Look for the word 'Total' and the number immediately following it.
    Strategy 2: If that fails, find the largest currency-like number in the text.
    """
    try:
        total_pattern = r"(?i)total.*?((\d{1,3}(?:,\d{3})*|(\d+))(\.\d{2}))"
        
        matches = re.findall(total_pattern, text)
        
        if matches:
            amount_str = matches[-1][0]
            return float(amount_str.replace(',', ''))

        money_pattern = r"(\d{1,3}(?:,\d{3})*|(\d+))(\.\d{2})"
        all_numbers = re.findall(money_pattern, text)
        
        if all_numbers:
            valid_floats = []
            for num_tuple in all_numbers:
                try:
                    val = float(num_tuple[0].replace(',', ''))
                    valid_floats.append(val)
                except ValueError:
                    continue
            
            if valid_floats:
                return max(valid_floats)

        return None

    except Exception as e:
        logger.error(f"Error extracting total: {e}")
        return None

def extract_date(text: str) -> Optional[str]:
    """
    Uses dateparser to find the likely transaction date.
    Returns ISO 8601 format (YYYY-MM-DD).
    """
    try:
        dates = search_dates(text, languages=['en'])
        
        if not dates:
            return None
        
        for date_str, date_obj in dates:
            if 2000 < date_obj.year < 2030:
                return date_obj.strftime("%Y-%m-%d")
        
        return dates[0][1].strftime("%Y-%m-%d")

    except Exception as e:
        logger.error(f"Error extracting date: {e}")
        return None