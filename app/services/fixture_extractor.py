"""Extract Fixture data from PSA files."""
from __future__ import annotations

from typing import Tuple, List
import pandas as pd

from app.services.fixture_mapper import extract_and_map_fixture
from app.services.fixture_validator import ValidationResult


def extract_fixture_data(psa_bytes: bytes) -> Tuple[pd.DataFrame, List[ValidationResult], dict]:
    """Extract and validate Fixture data.
    
    Args:
        psa_bytes: Raw PSA file bytes
        
    Returns:
        Tuple of (DataFrame, validation_results, summary)
    """
    
    print("[FIXTURE] Starting extraction and validation...")
    
    # Use the mapper which handles extraction, mapping, and validation
    df, validation_results, summary = extract_and_map_fixture(psa_bytes)
    
    print(f"[FIXTURE] Extraction complete: {len(df)} rows, {len(df.columns)} columns")
    print(f"[FIXTURE] Validation summary: {summary['passed']} passed, {summary['failed']} failed")
    
    return df, validation_results, summary
