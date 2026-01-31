import re
import logging
from typing import Optional, List, Tuple
from dateparser.search import search_dates
from app.schemas.receipt import LineItem

logger = logging.getLogger(__name__)

class FinancialParser:
    def __init__(self, text: str):
        self.text = text
        self.lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Regex for currency: Matches $10.00, 1,000.50, 50.00, (20.00), -15.00 etc.
        self.money_pattern = r"([\(|-]?\s*(?:[$€£¥]?\s*)?\d{1,3}(?:,\d{3})*(\.\d{2})\s*[\)|-]?)"

    def _parse_float(self, amount_str: str) -> float:
        """
        Cleans currency string and converts to float.
        Handles parentheses (10.00) as negative, though for extraction 
        we usually want absolute values and handle logic in the analyzer.
        """
        try:
            # Remove currency symbols and whitespace
            clean_str = re.sub(r'[^\d.,-]', '', amount_str)
            
            # Handle trailing negative sign (OCR quirk: "5.00-")
            if clean_str.endswith('-'):
                clean_str = '-' + clean_str[:-1]
                
            val = float(clean_str.replace(',', ''))
            return abs(val)
        except ValueError:
            return 0.0

    def _is_valid_date(self, date_obj) -> bool:
        """Helper to ensure date is within a reasonable receipt range."""
        if not date_obj:
            return False
        return 1970 <= date_obj.year <= 2030

    def extract_date(self) -> Optional[str]:
        """
        Robust strategy:
        1. Look for 'Date:' label + Regex (Highest Confidence)
        2. Look for strict Regex patterns (Medium Confidence)
        3. Fallback to dateparser (Low Confidence)
        """
        full_text = "\n".join(self.lines)

        # --- STRATEGY 1: Regex Patterns ---
        regex_patterns = [
            # Labeled Date (e.g., "Date: 10/12/23")
            r"(?i)date\s*[:.]?\s*(\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{2,4})",
            # Standard Slash/Dash (e.g., 12/12/2023 or 2023-12-12)
            r"(\d{1,2}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{4})", 
            r"(\d{4}\s*[/\-.]\s*\d{1,2}\s*[/\-.]\s*\d{1,2})",
            # Text Month (e.g., 12 Oct 2023)
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"
        ]

        for pattern in regex_patterns:
            matches = re.search(pattern, full_text)
            if matches:
                date_str = matches.group(1)
                # use dateparser to convert the clean regex string to an object
                try:
                    parsed = search_dates(date_str, languages=['en'])
                    if parsed:
                        date_obj = parsed[0][1]
                        if self._is_valid_date(date_obj):
                            return date_obj.strftime("%Y-%m-%d")
                except Exception:
                    continue

        try:
            settings = {
                'STRICT_PARSING': False, 
                'REQUIRE_PARTS': ['year', 'month', 'day']
            }

            dates = search_dates(full_text, languages=['en'], settings=settings)
            
            if dates:
                for _, date_obj in dates:
                    if self._is_valid_date(date_obj):
                        return date_obj.strftime("%Y-%m-%d")

        except Exception as e:
            logger.warning(f"Date extraction failed: {e}")
        
        return None

    def extract_financials(self) -> dict:
        """
        Extracts Total, Subtotal, and Tax using a tiered keyword strategy.
        """
        results = {
            "total": None, 
            "subtotal": None, 
            "tax": None, 
            "discount": None, 
            "tip": None
        }
        
        total_keywords = ["total", "amount due", "grand total", "balance due", "payment", "grand amount"]
        subtotal_keywords = ["subtotal", "sub total", "net amount", "taxable"]
        tax_keywords = ["tax", "vat", "gst", "hst", "sales tax"]
        tip_keywords = ["tip", "gratuity", "service charge", "svc chg"]
        discount_keywords = ["discount", "savings", "coupon", "promo", "credit"]

        # Iterate lines backwards (Totals are usually at the bottom)
        for line in reversed(self.lines):
            lower_line = line.lower()
            
            # Find all numbers in the line
            matches = re.findall(self.money_pattern, line)
            if not matches:
                continue
            
            # The last number in the line is usually the value (e.g., "Total ........ 10.00")
            val_str = matches[-1][0] 
            val = self._parse_float(val_str)
            
            # Check for Total (High Priority)
            if not results["total"] and any(k in lower_line for k in total_keywords):
                # Avoid "Subtotal" triggering "Total"
                if "sub" not in lower_line: 
                    results["total"] = val
                    continue

            # Check for Subtotal
            if not results["subtotal"] and any(k in lower_line for k in subtotal_keywords):
                results["subtotal"] = val
                continue

            # Check for Tax
            if not results["tax"] and any(k in lower_line for k in tax_keywords):
                results["tax"] = val
                continue

            if not results["tip"] and any(k in lower_line for k in tip_keywords):
                results["tip"] = val
                continue

            # checking for Discount
            if not results["discount"] and any(k in lower_line for k in discount_keywords):
                results["discount"] = val
                continue

        if not results["total"]:
            all_floats = []
            for line in self.lines:
                matches = re.findall(self.money_pattern, line)
                for m in matches:
                    all_floats.append(self._parse_float(m[0]))
            if all_floats:
                results["total"] = max(all_floats)

        return results

    def extract_merchant(self) -> str:
        """
        Heuristic: The merchant is usually the first non-numeric line in the header.
        """
        for line in self.lines[:5]: # Check top 5 lines
            if len(line) < 3: continue
            if re.search(r"\d", line): continue # Skip lines with numbers (dates/phones)
            if "welcome" in line.lower(): continue
            return line.title()
        return "Unknown Merchant"

def parse_receipt(text: str) -> dict:
    parser = FinancialParser(text)
    
    financials = parser.extract_financials()
    
    return {
        "merchant": parser.extract_merchant(),
        "date": parser.extract_date(),
        "total": financials["total"],
        "subtotal": financials["subtotal"],
        "tax": financials["tax"],
        "tip": financials.get("tip"),           
        "discount": financials.get("discount")
    }