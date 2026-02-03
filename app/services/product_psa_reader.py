from __future__ import annotations

import csv


def parse_psa_line(line: str) -> list[str]:
    """Parse a PSA line, handling quoted fields and ProSpace escape sequences.
    
    ProSpace format:
    - Fields are comma-separated
    - Fields containing commas have backslash-escaped commas inside them
    - Backslash escapes special characters like commas within text fields
    - Strategy: look ahead - if we see backslash-comma, that indicates an escaped char
    - Example: MS 6FT TBL\\, WHT is a single field = 'MS 6FT TBL, WHT'
    """
    fields = []
    current_field = []
    i = 0
    backslash = chr(92)  # Backslash character
    
    while i < len(line):
        char = line[i]
        
        # Check for escape sequence (backslash followed by a character)
        if char == backslash and i + 1 < len(line):
            next_char = line[i + 1]
            # Add the escaped character (unescaped)
            if next_char == ',':
                # Escaped comma - add it as a regular comma to the field
                current_field.append(',')
            else:
                # Other escape - add the escaped character
                current_field.append(next_char)
            i += 2  # Skip both the backslash and the next character
        elif char == ',':
            # Unescaped comma = field separator
            fields.append(''.join(current_field))
            current_field = []
            i += 1
        else:
            # Regular character
            current_field.append(char)
            i += 1
    
    # Don't forget the last field
    if current_field or (line and line[-1] == ','):
        fields.append(''.join(current_field))
    
    return fields


def read_product_rows_from_bytes(psa_bytes: bytes) -> list[list[str]]:
    """Parse PSA bytes and return Product rows INCLUDING the leading 'Product' token.
    
    Uses custom parser to handle ProSpace escape sequences (escaped commas).
    Keeps Field_0 (the 'Product' text) to maintain consistency with original PSA structure.
    """

    text = psa_bytes.decode("cp1252", errors="replace")
    lines = text.splitlines()

    product_rows: list[list[str]] = []
    for line in lines[3:]:  # Skip PSA header
        fields = parse_psa_line(line)
        if fields and fields[0] == "Product":
            product_rows.append(fields)  # Keep all fields including 'Product'

    return product_rows
