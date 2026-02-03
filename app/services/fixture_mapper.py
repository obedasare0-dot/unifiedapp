"""Fixture field mapper - extracts all fields, trims to needed ones, and renames.

Process:
1. Extract ALL fields from PSA Fixture rows (expect Field_0 to Field_165)
2. Validate field count (Field_Count validation)
3. Trim to only the 15 fields we need
4. Rename to clean business names
"""
import pandas as pd
from typing import List, Tuple

from app.services.fixture_validator import validate_fixture_data, ValidationResult

# Expected field count from PSA files
EXPECTED_FIELD_COUNT = 166  # Field_0 through Field_165

# Define the field mapping (original Field_X → clean name)
FIXTURE_FIELD_MAPPING = {
    'Field_0': 'Type',
    'Field_1': 'Name',
    'Field_3': 'X',
    'Field_4': 'Width',
    'Field_5': 'Y',
    'Field_7': 'Z',
    'Field_8': 'Depth',
    'Field_12': 'Color',
    'Field_22': 'Merch',
    'Field_26': 'Left_Overhang',
    'Field_27': 'Right_Overhang',
    'Field_30': 'Back_Overhang',
    'Field_31': 'Front_Overhang',
    'Field_76': 'Notch',
    'Field_104': 'Proof_Notes'
}

# Fields to keep (in the order we want them)
FIELDS_TO_KEEP = [
    'Field_0',   # Type
    'Field_1',   # Name
    'Field_3',   # X
    'Field_4',   # Width
    'Field_5',   # Y
    'Field_7',   # Z
    'Field_8',   # Depth
    'Field_12',  # Color
    'Field_22',  # Merch
    'Field_26',  # Left_Overhang
    'Field_27',  # Right_Overhang
    'Field_30',  # Back_Overhang
    'Field_31',  # Front_Overhang
    'Field_76',  # Notch
    'Field_104'  # Proof_Notes
]

# Type code mapping (numeric to text)
TYPE_CODE_MAPPING = {
    '0': 'Shelf',
    '4': 'Rod',
    '6': 'Bar',
    '7': 'Pegboard',
    '10': 'Obstruction'
}


def extract_and_map_fixture(psa_bytes: bytes) -> Tuple[pd.DataFrame, List[ValidationResult], dict]:
    """Extract Fixture table from PSA bytes, validate, and apply mapping.
    
    Steps:
    1. Read all Fixture rows from PSA bytes
    2. Validate field count (must be 166 fields)
    3. Create DataFrame with all fields (Field_0, Field_1, ...)
    4. Trim to only needed fields
    5. Rename to clean names
    6. Map Type codes to text
    7. Run full validation
    
    Args:
        psa_bytes: Raw PSA file content as bytes
        
    Returns:
        Tuple of (DataFrame, validation_results, summary)
    """
    
    print("[FIXTURE MAPPER] Starting extraction...")
    
    # Step 1: Decode and read all Fixture rows
    try:
        content = psa_bytes.decode('utf-8', errors='ignore')
    except Exception:
        content = psa_bytes.decode('latin-1', errors='ignore')
    
    lines = content.split('\n')
    
    fixture_rows = []
    for line in lines:
        line = line.strip()
        if line.startswith('Fixture,'):
            parts = line.split(',')
            fixture_data = parts[1:]  # Skip "Fixture" table name
            fixture_rows.append(fixture_data)
    
    print(f"[FIXTURE MAPPER] Found {len(fixture_rows)} rows")
    
    if not fixture_rows:
        raise ValueError("No Fixture rows found in PSA file")
    
    # Step 2: Run initial validation (Field_Count only)
    initial_validation, _ = validate_fixture_data(fixture_rows, df=None)
    
    # Check if Field_Count validation failed
    field_count_check = next((r for r in initial_validation if r.check_name == 'Field_Count'), None)
    if field_count_check and not field_count_check.passed:
        raise ValueError(f"Validation failed: {field_count_check.message}")
    
    # Step 3: Create DataFrame with ALL fields (validation passed)
    max_cols = max(len(row) for row in fixture_rows)
    
    all_field_names = [f'Field_{i}' for i in range(max_cols)]
    
    # Pad rows to match max columns
    padded_rows = [row + [''] * (max_cols - len(row)) for row in fixture_rows]
    df_all = pd.DataFrame(padded_rows, columns=all_field_names)
    
    print(f"[FIXTURE MAPPER] Extracted all fields: {len(df_all.columns)} columns")
    
    # Step 4: Trim to only needed fields
    df_trimmed = df_all[FIELDS_TO_KEEP].copy()
    
    print(f"[FIXTURE MAPPER] Trimmed to {len(df_trimmed.columns)} needed fields")
    
    # Step 5: Rename to clean names
    df_renamed = df_trimmed.rename(columns=FIXTURE_FIELD_MAPPING)
    
    print(f"[FIXTURE MAPPER] Renamed to clean names")
    print(f"[FIXTURE MAPPER] Final columns: {list(df_renamed.columns)}")
    
    # Step 6: Map Type codes to text values
    if 'Type' in df_renamed.columns:
        # Convert Type values from numeric codes to text
        df_renamed['Type'] = df_renamed['Type'].astype(str).map(
            lambda x: TYPE_CODE_MAPPING.get(x.strip(), x)  # Use mapping or keep original if not found
        )
        print(f"[FIXTURE MAPPER] Mapped Type codes to text values")
        print(f"[FIXTURE MAPPER] Type values: {df_renamed['Type'].value_counts().to_dict()}")
    
    # Step 7: Add Table_Name column as FIRST column (for consistency with Product/Planogram)
    df_renamed.insert(0, 'Table_Name', 'Fixture')
    print(f"[FIXTURE MAPPER] Added Table_Name column as first column")
    print(f"[FIXTURE MAPPER] Final column order: {list(df_renamed.columns)}")
    
    # Step 8: Run full validation on cleaned DataFrame (including Unique_Name)
    validation_results, validation_summary = validate_fixture_data(fixture_rows, df=df_renamed)
    
    return df_renamed, validation_results, validation_summary
