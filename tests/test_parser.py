import pytest
from app.services.parser import FinancialParser, parse_receipt

def test_financial_parser_extract_total_simple():
    text = "Item 1... 10.00\nTotal: 25.50"
    parser = FinancialParser(text)
    financials = parser.extract_financials()
    assert financials["total"] == 25.50

def test_financial_parser_extract_total_with_currency_symbol():
    text = "TOTAL AMOUNT $1,200.50"
    parser = FinancialParser(text)
    financials = parser.extract_financials()
    assert financials["total"] == 1200.50

def test_financial_parser_extract_total_fallback_max_number():
    text = "Burger 10.00\nFries 5.00\nTax 1.00\n16.00"
    parser = FinancialParser(text)
    financials = parser.extract_financials()
    assert financials["total"] == 16.00

def test_financial_parser_extract_total_none():
    text = "No numbers here"
    parser = FinancialParser(text)
    financials = parser.extract_financials()
    assert financials["total"] is None

def test_financial_parser_extract_date_iso():
    text = "Date: 2023-10-15"
    parser = FinancialParser(text)
    assert parser.extract_date() == "2023-10-15"

def test_financial_parser_extract_date_us_format():
    text = "Transaction Date: 12/25/2023"
    parser = FinancialParser(text)
    assert parser.extract_date() == "2023-12-25"

def test_financial_parser_extract_date_text_format():
    text = "Nov 12, 2023"
    parser = FinancialParser(text)
    assert parser.extract_date() == "2023-11-12"

def test_financial_parser_extract_all_financials():
    text = """
    Walmart
    Subtotal: 40.00
    Tax: 4.00
    Tip: 5.00
    Discount: 1.00
    Fee: 2.00
    Total: 50.00
    """
    parser = FinancialParser(text)
    financials = parser.extract_financials()
    assert financials["total"] == 50.00
    assert financials["subtotal"] == 40.00
    assert financials["tax"] == 4.00
    assert financials["tip"] == 5.00
    assert financials["discount"] == 1.00
    assert financials["other_fees"] == 2.00

def test_parse_receipt_wrapper():
    text = "Walmart\nTotal: 50.00\nDate: 2023-01-01"
    result = parse_receipt(text)
    assert result["merchant"] == "Walmart"
    assert result["total"] == 50.00
    assert result["date"] == "2023-01-01"