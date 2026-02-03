"""Extract and validate Planogram data from PSA files."""
from __future__ import annotations

from typing import Tuple, List, Optional
import pandas as pd

from app.services.planogram_psa_reader import read_planogram_rows_from_bytes
from app.services.planogram_mapper import smart_map_planogram_fields, FIELD_NAMES
from app.services.planogram_validator import DataValidator, ValidationResult


def extract_planogram_data(
    psa_bytes: bytes,
    excel_reference_bytes: Optional[bytes] = None
) -> Tuple[pd.DataFrame, List[ValidationResult], dict]:
    """Extract Planogram data and run validation checks.
    
    Args:
        psa_bytes: Raw PSA file bytes
        excel_reference_bytes: Optional Excel reference file bytes for department validation
        
    Returns:
        Tuple of:
        - DataFrame with smart-mapped Planogram data (22 columns)
        - List of ValidationResult objects
        - Summary dict (passed, failed, warnings counts)
    """
    
    print("[PLANOGRAM] Starting extraction...")
    
    # Step 1: Extract Planogram rows
    planogram_rows = read_planogram_rows_from_bytes(psa_bytes)
    if not planogram_rows:
        raise ValueError("No Planogram rows found in PSA file")
    
    print(f"[PLANOGRAM] Extracted {len(planogram_rows)} records")
    
    # Step 2: Apply smart mapping to each row
    mapped_data = []
    for row in planogram_rows:
        mapped_row = smart_map_planogram_fields(row)
        mapped_data.append(mapped_row)
    
    print(f"[PLANOGRAM] Smart-mapped {len(mapped_data)} rows with 22 fields each")
    
    # Step 3: Create DataFrame with renamed columns
    df = pd.DataFrame(mapped_data)
    
    # Ensure columns are in the correct order (0-21)
    ordered_columns = [FIELD_NAMES[i] for i in range(22)]
    df = df[ordered_columns]
    
    print(f"[PLANOGRAM] Created DataFrame with columns: {', '.join(df.columns.tolist())}")
    
    # Step 4: Run validation checks
    print(f"[PLANOGRAM] Running validation checks...")
    validator = DataValidator(df, excel_reference_bytes=excel_reference_bytes)
    validation_results = validator.run_all_checks()
    summary = validator.get_summary()
    
    print(f"[PLANOGRAM] Validation complete: {summary['passed']} passed, {summary['failed']} failed")
    
    return df, validation_results, summary
