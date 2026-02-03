"""Smart field mapper for Planogram data using custom search/calculation logic."""
from __future__ import annotations

import re
from datetime import datetime

# Field name mapping (22 fields)
FIELD_NAMES = {
    0: 'Table_Name',
    1: 'Modular_Description',
    2: 'Field_2',
    3: 'Width_Inches',
    4: 'Height_Inches',
    5: 'Depth_Inches',
    6: 'Field_6',
    7: 'Offset',
    8: 'Notch_Bar_Width',
    9: 'Department',
    10: 'Category',
    11: 'Effective_Date',
    12: 'Print_1',
    13: 'Print_2',
    14: 'Print_3',
    15: 'Print_4',
    16: 'File_Name',
    17: 'Width_Feet',
    18: 'Segments',
    19: 'Drawing_ID',
    20: 'Footage',
    21: 'Trait_Number'
}


def smart_map_planogram_fields(fields: list[str]) -> dict[str, str]:
    """
    Apply smart mapping to Planogram fields.
    
    Strategy:
        - Indices 0-6: Fixed (as-is from PSA)
        - Index 7: Search for '7.81'
        - Index 8: Search for '1.25'
        - Index 9: Search for any of [14, 17, 20, 22, 71, 74]
        - Index 10: Closest 4-digit number after Index 9
        - Index 11: Date (M/D/Y) that is after today AND on a Monday
        - Index 12: "GENERAL_TC" (case-insensitive)
        - Index 13: "PRODUCT LISTING.PST" (case-insensitive)
        - Index 14: "SHELF" (case-insensitive)
        - Index 15: "NR_P_C_SEG.PSY" (case-insensitive)
        - Index 16: Any field containing ".psa" (case-insensitive)
        - Index 17: Calculated - Field_3 value / 12
        - Index 18: Calculated - Index 17 value / 4
        - Index 19: First 5 digits from Index 16
        - Index 20: Characters 6, 7, 8 from Index 16
        - Index 21: Numbers between _ and first alphabet in Index 16
    
    Args:
        fields: Raw field list from Planogram row
        
    Returns:
        Dictionary mapping field names to values
    """
    
    # Start with first 7 fields as-is (indices 0-6)
    mapped = fields[:7] if len(fields) >= 7 else fields + [''] * (7 - len(fields))
    
    # Search in remaining fields (from index 7 onwards)
    search_pool = fields[7:] if len(fields) > 7 else []
    
    # Index 7: Search for '7.81'
    idx_7_value = ''
    for field in search_pool:
        if '7.81' in field:
            idx_7_value = field.strip()
            break
    mapped.append(idx_7_value)
    
    # Index 8: Search for '1.25'
    idx_8_value = ''
    for field in search_pool:
        if '1.25' in field:
            idx_8_value = field.strip()
            break
    mapped.append(idx_8_value)
    
    # Index 9 & 10: Search for any of [14, 17, 20, 22, 71, 74]
    # Index 10: Find the closest 4-digit number after Index 9
    target_values = ['14', '17', '20', '22', '71', '74']
    idx_9_value = ''
    idx_10_value = ''
    
    for i, field in enumerate(search_pool):
        if field.strip() in target_values:
            idx_9_value = field
            # Search for the closest 4-digit number after Index 9
            for j in range(i + 1, len(search_pool)):
                candidate = search_pool[j].strip()
                # Check if it's a 4-digit number (with or without leading zeros)
                if re.match(r'^\d{4}$', candidate):
                    idx_10_value = candidate
                    break
            break
    
    mapped.append(idx_9_value)
    mapped.append(idx_10_value)
    
    # Index 11: Date pattern (mo/day/year) - only if after today AND on a Monday
    date_pattern = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}')
    idx_11_value = ''
    today = datetime.now()
    
    for field in search_pool:
        match = date_pattern.search(field.strip())
        if match:
            date_str = match.group()  # Extract ONLY the date, not the whole field
            try:
                # Parse the date (try different year formats)
                for fmt in ['%m/%d/%Y', '%m/%d/%y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        # Check if date is after today AND is a Monday (weekday 0)
                        if parsed_date > today and parsed_date.weekday() == 0:
                            idx_11_value = date_str
                            break
                        break  # Successfully parsed, exit format loop
                    except ValueError:
                        continue
                if idx_11_value:  # Found valid date
                    break
            except (ValueError, AttributeError):
                continue
    
    mapped.append(idx_11_value)
    
    # Index 12: Search for "GENERAL_TC" (case-insensitive)
    idx_12_value = ''
    for field in search_pool:
        if 'general_tc' in field.lower():
            idx_12_value = field.strip()
            break
    mapped.append(idx_12_value)
    
    # Index 13: Search for "PRODUCT LISTING.PST" (case-insensitive)
    idx_13_value = ''
    for field in search_pool:
        if 'product listing.pst' in field.lower():
            idx_13_value = field.strip()
            break
    mapped.append(idx_13_value)
    
    # Index 14: Search for "SHELF" (case-insensitive)
    idx_14_value = ''
    for field in search_pool:
        if 'shelf' in field.lower() and len(field.strip()) < 20:  # Avoid long text matches
            idx_14_value = field.strip()
            break
    mapped.append(idx_14_value)
    
    # Index 15: Search for "NR_P_C_SEG.PSY" (case-insensitive)
    idx_15_value = ''
    for field in search_pool:
        if 'nr_p_c_seg.psy' in field.lower():
            idx_15_value = field.strip()
            break
    mapped.append(idx_15_value)
    
    # Index 16: Search for any field containing ".psa" (case-insensitive)
    idx_16_value = ''
    for field in search_pool:
        if '.psa' in field.lower():
            idx_16_value = field.strip()
            break
    mapped.append(idx_16_value)
    
    # Index 17: Field_3 value divided by 12 (calculated field)
    idx_17_value = ''
    try:
        field_3_value = mapped[3] if len(mapped) > 3 else ''
        field_3_numeric = float(field_3_value) if field_3_value else 0
        idx_17_value = str(field_3_numeric / 12) if field_3_numeric != 0 else ''
    except (ValueError, IndexError):
        idx_17_value = ''
    mapped.append(idx_17_value)
    
    # Index 18: Index 17 value divided by 4 (calculated field)
    idx_18_value = ''
    try:
        idx_17_numeric = float(idx_17_value) if idx_17_value else 0
        idx_18_value = str(idx_17_numeric / 4) if idx_17_numeric != 0 else ''
    except (ValueError, IndexError):
        idx_18_value = ''
    mapped.append(idx_18_value)
    
    # Index 19: First 5 digits from Index 16 (extract from .psa field)
    idx_19_value = ''
    try:
        idx_16_text = mapped[16] if len(mapped) > 16 else ''
        # Extract all digits from Index 16
        digits_only = ''.join(re.findall(r'\d', idx_16_text))
        # Take first 5 digits
        idx_19_value = digits_only[:5] if len(digits_only) >= 5 else digits_only
    except (IndexError, AttributeError):
        idx_19_value = ''
    mapped.append(idx_19_value)
    
    # Index 20: Characters 6, 7, 8 from Index 16 (positions 5, 6, 7 in 0-based indexing)
    idx_20_value = ''
    try:
        idx_16_text = mapped[16] if len(mapped) > 16 else ''
        # Extract characters at positions 5, 6, 7 (6th, 7th, 8th characters)
        idx_20_value = idx_16_text[5:8] if len(idx_16_text) >= 8 else ''
    except (IndexError, AttributeError):
        idx_20_value = ''
    mapped.append(idx_20_value)
    
    # Index 21: Numbers between underscore (_) and first alphabet from Index 16
    idx_21_value = ''
    try:
        idx_16_text = mapped[16] if len(mapped) > 16 else ''
        # Find underscore position
        if '_' in idx_16_text:
            after_underscore = idx_16_text.split('_', 1)[1]  # Get everything after first _
            # Extract digits until we hit a letter
            match = re.match(r'^(\d+)', after_underscore)
            if match:
                idx_21_value = match.group(1)
    except (IndexError, AttributeError):
        idx_21_value = ''
    mapped.append(idx_21_value)
    
    # Convert to dictionary with field names
    result = {}
    for i, value in enumerate(mapped):
        field_name = FIELD_NAMES.get(i, f'Field_{i}')
        result[field_name] = value
    
    return result
