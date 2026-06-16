import pytest
from src.etl.normaliser import normalize_year, normalize_ticker

@pytest.mark.parametrize("input_year, expected", [
    (2023, 2023),             ("2023", 2023),           (2025.0, 2025),           
    ("2022.0", 2022),         ("FY23", 2023),           ("FY24", 2024),           
    ("fy25", 2025),           ("FY 26", 2026),          ("FY2023", 2023),         
    ("2023-24", 2023),        ("2024-25", 2024),        ("23-24", 2023),          
    ("25-26", 2025),          ("  2021  ", 2021),       ("CY2020", 2020),         
    ("Year: 2019", 2019),     ("22", 2022),             (1999, 1999),             
    ("FY 09", 2009),          ("2030-31", 2030)         
])
def test_normalize_year_success(input_year, expected):
    assert normalize_year(input_year) == expected

@pytest.mark.parametrize("invalid_year", [None, "", "   ", "abc", "FYABC", "202", "12345"])
def test_normalize_year_failures(invalid_year):
    with pytest.raises(ValueError):
        normalize_year(invalid_year)

@pytest.mark.parametrize("input_ticker, expected", [
    ("RELIANCE", "RELIANCE"),       ("reliance", "RELIANCE"),       
    ("  RELIANCE  ", "RELIANCE"),   ("TCS.NS", "TCS"),              
    ("INFY.BO", "INFY"),            ("WIPRO.BOM", "WIPRO"),          
    ("tcs.ns", "TCS"),              ("HDFCBANK.NS ", "HDFCBANK"),   
    ("CAMPUS-EQ", "CAMPUS-EQ"),     ("NIFTY_100", "NIFTY_100"),     
    ("SBIN.NS", "SBIN"),            (" IOC ", "IOC"),               
    ("M&M.NS", "M&M"),               ("BHARTIARTL", "BHARTIARTL"),   
    ("123STEEL", "123STEEL")        
])
def test_normalize_ticker_success(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected

@pytest.mark.parametrize("invalid_ticker", [None, "", "    ", "   .NS"])
def test_normalize_ticker_failures(invalid_ticker):
    with pytest.raises(ValueError):
        normalize_ticker(invalid_ticker)