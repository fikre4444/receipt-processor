from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def analyze_receipt(data: dict) -> list[str]:
    """
    Applies business rules to flag suspicious or noteworthy receipts.
    Expected data dict: {total, subtotal, tax, date, ...}
    """
    tags = []
    
    date_str = data.get("date")
    total = data.get("total")
    subtotal = data.get("subtotal")
    tax = data.get("tax")
    tip = data.get("tip")
    discount = data.get("discount")

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


    # # 4. Fraud/Suspicion Indicators
    # # "Round Number" check (e.g., 50.00 is suspicious, 50.23 is natural)
    # if total and total % 1 == 0 and total > 10:
    #     tags.append("ROUND_AMOUNT")

    # if total and subtotal:
    #     v_subtotal = subtotal or 0.0
    #     v_tax = tax or 0.0
    #     v_tip = tip or 0.0
    #     v_discount = discount or 0.0

    #     # Updated Formula
    #     expected_total = v_subtotal + v_tax + v_tip - v_discount
        
    #     diff = abs(total - expected_total)
        
    #     if diff < 5: # Slightly higher tolerance for complex receipts
    #         tags.append("MATH_VERIFIED")
    #     else:
    #         logger.warning(f"Mismatch: {v_subtotal} + {v_tax} + {v_tip} - {v_discount} != {total}")
    #         tags.append("MATH_MISMATCH")

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