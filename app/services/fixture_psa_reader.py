"""Read Fixture rows from PSA file bytes."""
from typing import List


def read_fixture_rows_from_bytes(psa_bytes: bytes) -> List[List[str]]:
    """Extract Fixture rows from PSA file bytes.
    
    Args:
        psa_bytes: Raw PSA file content
        
    Returns:
        List of Fixture rows (each row is a list of field values)
    """
    try:
        content = psa_bytes.decode('utf-8', errors='ignore')
    except Exception:
        content = psa_bytes.decode('latin-1', errors='ignore')
    
    lines = content.split('\n')
    fixture_rows = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('Fixture,'):
            # Split by comma
            parts = line.split(',')
            # Remove the "Fixture" table name from the beginning
            row_data = parts[1:]  # Skip "Fixture" itself
            fixture_rows.append(row_data)
    
    print(f"[INFO] Found {len(fixture_rows)} Fixture rows")
    return fixture_rows
