import re
from typing import Union

def normalize_year(year_val: Union[str, int, float]) -> int:
    """
    Normalizes various year formats into a standard 4-digit integer (e.g., 2023).
    Handles: 'FY23', 'FY2023', '2023-24', '23-24', 2023.0, '2023'
    """
    if year_val is None:
        raise ValueError("Year cannot be None")
        
    if isinstance(year_val, (int, float)):
        year_str = str(int(year_val)).strip()
    else:
        year_str = str(year_val).strip()

    if not year_str:
        raise ValueError("Year cannot be empty")

    match_4digit = re.search(r'\b(19|20)\d{2}\b', year_str)
    if match_4digit:
        return int(match_4digit.group(0))

    match_fy2digit = re.search(r'(?:FY|fy)\s*(\d{2})', year_str)
    if match_fy2digit:
        short_year = int(match_fy2digit.group(1))
        return 2000 + short_year

    match_range = re.search(r'\b(\d{2,4})\s*-\s*\d{2,4}', year_str)
    if match_range:
        part = match_range.group(1)
        if len(part) == 4:
            return int(part)
        elif len(part) == 2:
            return 2000 + int(part)

    if year_str.isdigit() and len(year_str) == 2:
        return 2000 + int(year_str)

    raise ValueError(f"Could not parse year format: '{year_val}'")


def normalize_ticker(ticker_val: Union[str, None]) -> str:
    """
    Normalizes stock tickers to clean uppercase, stripping extensions like .NS or .BOM
    and removing any surrounding whitespace. Preserves special chars like '&'.
    """
    if ticker_val is None:
        raise ValueError("Ticker cannot be None")
        
    ticker_str = str(ticker_val).strip().upper()
    
    if not ticker_str:
        raise ValueError("Ticker cannot be empty")
        
    ticker_str = re.split(r'\.(NS|BO|BOM)$', ticker_str)[0]
    ticker_str = re.sub(r'[^A-Z0-9_\-&]', '', ticker_str)
    
    return ticker_str