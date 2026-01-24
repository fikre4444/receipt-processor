from datetime import datetime, timedelta

def analyze_receipt(total: float | None, date_str: str | None) -> list[str]:
    """
    Applies business rules to flag suspicious or noteworthy receipts.
    """
    tags = []

    if not total:
        tags.append("MISSING_TOTAL")
    if not date_str:
        tags.append("MISSING_DATE")

    if total and total > 100.00:
        tags.append("HIGH_VALUE")

    if date_str:
        try:
            receipt_date = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.now()
            
            if receipt_date > today:
                tags.append("FUTURE_DATE")
            
            ninety_days_ago = today - timedelta(days=90)
            if receipt_date < ninety_days_ago:
                tags.append("OLD_RECEIPT")
                
        except ValueError:
            pass

    return tags