"""Extract and validate Product data from PSA files."""
from __future__ import annotations

from typing import Tuple, List, Optional
import pandas as pd

from app.services.product_psa_reader import read_product_rows_from_bytes
from app.services.xlsx_writer import create_standard_headers
from app.services.product_column_remapper import remap_and_clean_columns
from app.services.product_validator import DataValidator, ValidationResult


def extract_product_data(
    psa_bytes: bytes,
    excel_reference_bytes: Optional[bytes] = None
) -> Tuple[pd.DataFrame, List[ValidationResult], dict]:
    """Extract Product data and run validation checks.
    
    Args:
        psa_bytes: Raw PSA file bytes
        excel_reference_bytes: Optional Excel reference file bytes for Has_Alt_UPC validation
        
    Returns:
        Tuple of:
        - DataFrame with clean Product data (46 columns)
        - List of ValidationResult objects
        - Summary dict (passed, failed, warnings counts)
    """
    
    print("[PRODUCT] Starting extraction...")
    
    # Step 1: Extract Product rows
    product_rows = read_product_rows_from_bytes(psa_bytes)
    if not product_rows:
        raise ValueError("No Product rows found in PSA file")
    
    print(f"[PRODUCT] Extracted {len(product_rows)} records")
    
    # Step 2: Create DataFrame with standardized headers
    max_cols = max(len(r) for r in product_rows)
    headers = create_standard_headers(max_cols)
    
    # Pad rows to match max columns
    padded_rows = [row + [''] * (max_cols - len(row)) for row in product_rows]
    df = pd.DataFrame(padded_rows, columns=headers)
    
    print(f"[PRODUCT] Created DataFrame with {len(df.columns)} columns")
    
    # Step 3: Remap and clean columns
    df_cleaned = remap_and_clean_columns(df)
    print(f"[PRODUCT] Cleaned to {len(df_cleaned.columns)} columns")
    
    # Step 4: Run validation checks
    print(f"[PRODUCT] Running validation checks...")
    validator = DataValidator(df_cleaned, excel_reference_bytes=excel_reference_bytes)
    validation_results = validator.run_all_checks()
    summary = validator.get_summary()
    
    print(f"[PRODUCT] Validation complete: {summary['passed']} passed, {summary['failed']} failed")
    
    return df_cleaned, validation_results, summary
