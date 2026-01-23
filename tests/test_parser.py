import pytest
from app.services import parser

def test_extract_total_simple():
    text = "Item 1... 10.00\nTotal: 25.50"
    assert parser.extract_total(text) == 25.50

def test_extract_total_with_currency_symbol():
    text = "TOTAL AMOUNT $1,200.50"
    assert parser.extract_total(text) == 1200.50

def test_extract_total_fallback_max_number():
    text = "Burger 10.00\nFries 5.00\nTax 1.00\n16.00"
    assert parser.extract_total(text) == 16.00

def test_extract_total_none():
    text = "No numbers here"
    assert parser.extract_total(text) is None

def test_extract_date_iso():
    text = "Date: 2023-10-15"
    assert parser.extract_date(text) == "2023-10-15"

def test_extract_date_us_format():
    text = "Transaction Date: 12/25/2023"
    assert parser.extract_date(text) == "2023-12-25"

def test_extract_date_text_format():
    text = "Nov 12, 2023"
    assert parser.extract_date(text) == "2023-11-12"