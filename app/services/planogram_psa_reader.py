"""PSA file reader for extracting Planogram rows."""
from __future__ import annotations


def parse_csv_line(line: str) -> list[str]:
    """Parse a CSV line respecting quoted fields with commas."""
    fields = []
    current = ""
    in_quotes = False
    
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            fields.append(current)
            current = ""
        else:
            current += char
    
    fields.append(current)  # Add last field
    return fields


def merge_long_text_fields(fields: list[str]) -> list[str]:
    """Merge consecutive long-text fields (documentation, notes, JSON).
    
    Long-text fields are identified as fields containing >100 characters
    or starting with special markers like { or <.
    """
    if not fields:
        return fields
    
    merged = []
    i = 0
    
    while i < len(fields):
        field = fields[i]
        
        # Check if this is a long-text field
        is_long_text = (
            len(field) > 100 or 
            field.strip().startswith(('{', '<', '<?xml'))
        )
        
        if is_long_text:
            # Merge with next fields if they're also long or part of the same block
            merged_field = field
            j = i + 1
            
            while j < len(fields):
                next_field = fields[j]
                # Stop if we hit a "normal" field
                if len(next_field) < 50 and not next_field.strip().startswith(('{', '<')):
                    break
                merged_field += " " + next_field
                j += 1
            
            merged.append(merged_field)
            i = j
        else:
            merged.append(field)
            i += 1
    
    return merged


def read_planogram_rows_from_bytes(psa_bytes: bytes) -> list[list[str]]:
    """Extract all Planogram rows from PSA file bytes.
    
    Args:
        psa_bytes: Raw bytes from uploaded .psa file
        
    Returns:
        List of Planogram rows (each row is a list of field values)
    """
    try:
        # Decode bytes to text
        content = psa_bytes.decode('utf-8', errors='ignore')
        lines = content.splitlines()
        
        planogram_rows = []
        
        for line in lines:
            if line.startswith('Planogram,'):
                # Parse the CSV line
                fields = parse_csv_line(line)
                
                # Merge long-text fields to reduce noise
                merged_fields = merge_long_text_fields(fields)
                
                planogram_rows.append(merged_fields)
        
        print(f"[INFO] Found {len(planogram_rows)} Planogram rows")
        return planogram_rows
    
    except Exception as e:
        print(f"[ERROR] Failed to read Planogram rows: {e}")
        return []
