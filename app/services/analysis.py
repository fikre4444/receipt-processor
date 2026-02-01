from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    def analyze_receipt(self, data: dict) -> list[str]:
        """
        Applies business rules to flag suspicious or noteworthy receipts.
        Expected data dict: {total, date, ...}
        """
        tags = []
        
        date_str = data.get("date")
        total = data.get("total")

        # 1. Missing Data Checks
        if not total:
            tags.append("MISSING_TOTAL")
        if not date_str:
            tags.append("MISSING_DATE")

        # 2. Value Thresholds
        if total and total > 500.00:
            tags.append("HIGH_VALUE")
        
        if total and total < 2.00:
            tags.append("LOW_VALUE")

        if date_str:
            try:
                receipt_date = datetime.strptime(date_str, "%Y-%m-%d")
                today = datetime.now()
                
                if receipt_date > today + timedelta(days=1):
                    tags.append("FUTURE_DATE")
                
                if receipt_date.weekday() >= 5: # 5=Sat, 6=Sun
                    tags.append("WEEKEND_EXPENSE")
                    
                ninety_days_ago = today - timedelta(days=90)
                if receipt_date < ninety_days_ago:
                    tags.append("OLD_RECEIPT")
                    
            except ValueError:
                pass

        return tags
