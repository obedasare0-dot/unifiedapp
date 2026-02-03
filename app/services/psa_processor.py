"""Orchestrate PSA file processing for all tables."""
from __future__ import annotations

from typing import Dict, Any, Optional
import pandas as pd

from app.services.product_extractor import extract_product_data
from app.services.planogram_extractor import extract_planogram_data
from app.services.fixture_extractor import extract_fixture_data


def process_psa_file(
    psa_bytes: bytes,
    excel_reference_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """Process PSA file and extract all tables with validation.
    
    Args:
        psa_bytes: Raw PSA file bytes
        excel_reference_bytes: Optional Excel reference file bytes for:
            - Product: Has_Alt_UPC validation
            - Planogram: Department and Category validation
        
    Returns:
        Dict containing:
        - 'product_df': Product DataFrame
        - 'product_validation': List of ValidationResult
        - 'product_summary': Summary dict
        - 'planogram_df': Planogram DataFrame
        - 'planogram_validation': List of ValidationResult
        - 'planogram_summary': Summary dict
        - 'fixture_df': Fixture DataFrame
        - 'fixture_validation': List of ValidationResult
        - 'fixture_summary': Summary dict
    """
    
    print("="*80)
    print("PSA PROCESSOR: Starting multi-table extraction")
    print("="*80)
    
    result = {}
    
    # Extract Product table
    try:
        product_df, product_validation, product_summary = extract_product_data(
            psa_bytes,
            excel_reference_bytes=excel_reference_bytes
        )
        result['product_df'] = product_df
        result['product_validation'] = product_validation
        result['product_summary'] = product_summary
        print(f"[SUCCESS] Product: {len(product_df)} rows, {len(product_df.columns)} columns")
    except Exception as e:
        print(f"[ERROR] Product extraction failed: {e}")
        result['product_df'] = None
        result['product_validation'] = []
        result['product_summary'] = {'total_checks': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
    
    # Extract Planogram table
    try:
        planogram_df, planogram_validation, planogram_summary = extract_planogram_data(
            psa_bytes,
            excel_reference_bytes=excel_reference_bytes
        )
        result['planogram_df'] = planogram_df
        result['planogram_validation'] = planogram_validation
        result['planogram_summary'] = planogram_summary
        print(f"[SUCCESS] Planogram: {len(planogram_df)} rows, {len(planogram_df.columns)} columns")
    except Exception as e:
        print(f"[ERROR] Planogram extraction failed: {e}")
        result['planogram_df'] = None
        result['planogram_validation'] = []
        result['planogram_summary'] = {'total_checks': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
    
    # Extract Fixture table
    try:
        fixture_df, fixture_validation, fixture_summary = extract_fixture_data(psa_bytes)
        result['fixture_df'] = fixture_df
        result['fixture_validation'] = fixture_validation
        result['fixture_summary'] = fixture_summary
        print(f"[SUCCESS] Fixture: {len(fixture_df)} rows, {len(fixture_df.columns)} columns")
    except Exception as e:
        print(f"[ERROR] Fixture extraction failed: {e}")
        result['fixture_df'] = None
        result['fixture_validation'] = []
        result['fixture_summary'] = {'total_checks': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
    
    print("="*80)
    print("PSA PROCESSOR: Extraction complete")
    print("="*80)
    
    return result
