import re

def normalize_year(year_val):
    if year_val is None:
        raise ValueError("Year cannot be None")
        
    # Convert float/int to string cleanly
    if isinstance(year_val, float):
        if year_val.is_integer():
            year_str = str(int(year_val))
        else:
            year_str = str(year_val)
    else:
        year_str = str(year_val).strip()

    if not year_str or year_str.isspace():
        raise ValueError("Year cannot be empty")

    # If it's a completely raw number string and exceeds 4 digits, reject it (e.g., "12345")
    if year_str.isdigit() and len(year_str) > 4:
        raise ValueError(f"Invalid year format: '{year_val}'")

    # Match 2 to 4 digit years with optional FY/CY prefixes or ranges
    match = re.search(r'(?:FY|CY)?\s*(\d{2,4})', year_str, re.IGNORECASE)
    if match:
        part = match.group(1)
        
        # Double check that we didn't just extract a piece of a massive number sequence
        if len(year_str) == 5 and year_str.isdigit():
            raise ValueError(f"Invalid year format: '{year_val}'")
            
        if len(part) == 4:
            return int(part)
        elif len(part) == 2:
            return 2000 + int(part)

    if year_str.isdigit() and len(year_str) == 2:
        return 2000 + int(year_str)

    raise ValueError(f"Could not parse year format: '{year_val}'")


def normalize_ticker(ticker_val):
    if ticker_val is None:
        raise ValueError("Ticker cannot be None")
        
    ticker_str = str(ticker_val).strip()
    
    # Reject empty strings, standalone dots, or empty spaces trailing into .NS
    if not ticker_str or ticker_str == "." or ticker_str == ".NS":
        raise ValueError("Invalid ticker format")
        
    # Clean up prefixes/suffixes
    ticker_clean = ticker_str.upper()
    if ticker_clean.endswith(".BO"):
        ticker_clean = ticker_clean.replace(".BO", "")
    if ticker_clean.endswith(".BOM"):
        ticker_clean = ticker_clean.replace(".BOM", "")
    if ticker_clean.endswith(".NS"):
        ticker_clean = ticker_clean.replace(".NS", "")
        
    # Final strip in case spaces were hiding inside
    ticker_clean = ticker_clean.strip()
    
    if not ticker_clean:
        raise ValueError("Invalid ticker format")
        
    return ticker_clean
