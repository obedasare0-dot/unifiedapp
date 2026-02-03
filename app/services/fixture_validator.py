"""Fixture data validation - checks data quality before export.

Validations:
1. Field_Count: Ensure PSA has exactly 166 fields (Field_0 to Field_165)
"""
from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    error_count: int = 0
    pass_count: int = 0
    details: str = ""
    
    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == 'PASS'


def validate_field_count(fixture_rows: List[List[str]]) -> ValidationResult:
    """Validate that PSA file has exactly 166 fields (Field_0 to Field_165).
    
    Args:
        fixture_rows: List of Fixture rows (each row is a list of field values)
        
    Returns:
        ValidationResult with pass/fail status
    """
    EXPECTED_FIELD_COUNT = 166
    total_rows = len(fixture_rows)
    
    if not fixture_rows:
        return ValidationResult(
            check_name="Field_Count",
            status="FAIL",
            message="Field_Count_Error: No fixture rows found",
            error_count=1,
            pass_count=0,
            details="PSA file contains no Fixture rows"
        )
    
    # Check field count
    max_cols = max(len(row) for row in fixture_rows)
    
    if max_cols != EXPECTED_FIELD_COUNT:
        return ValidationResult(
            check_name="Field_Count",
            status="FAIL",
            message=f"Field_Count_Error: Expected {EXPECTED_FIELD_COUNT} fields (Field_0 to Field_165), found {max_cols}",
            error_count=total_rows,
            pass_count=0,
            details=f"Field count mismatch: Expected {EXPECTED_FIELD_COUNT}, Got {max_cols}"
        )
    
    return ValidationResult(
        check_name="Field_Count",
        status="PASS",
        message=f"Field count validated: {EXPECTED_FIELD_COUNT} fields (Field_0 to Field_165)",
        error_count=0,
        pass_count=total_rows,
        details=f"All {total_rows} rows have {EXPECTED_FIELD_COUNT} fields"
    )


def validate_unique_names(df: pd.DataFrame) -> ValidationResult:
    """Validate that every fixture has a unique name.
    
    Requirements:
    1. Name field must not be empty/blank
    2. Every fixture must have a UNIQUE name
    
    Args:
        df: DataFrame with 'Name' column
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Unique_Name"
    
    if 'Name' not in df.columns:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message="Name column not found",
            error_count=0,
            pass_count=0,
            details="Column does not exist in dataset"
        )
    
    total_rows = len(df)
    failed_rows = []
    
    # Check 1: Find empty/blank names
    empty_mask = df['Name'].isna() | (df['Name'].astype(str).str.strip() == '')
    empty_rows = df[empty_mask]
    
    for idx in empty_rows.index:
        failed_rows.append({
            'row': idx + 2,  # +2 for Excel (1-indexed + header)
            'name': '<EMPTY>',
            'reason': 'Empty/blank name'
        })
    
    # Check 2: Find duplicate names (only check non-empty names)
    non_empty_df = df[~empty_mask].copy()
    if len(non_empty_df) > 0:
        # Count occurrences of each name
        name_counts = non_empty_df['Name'].value_counts()
        duplicates = name_counts[name_counts > 1]
        
        if len(duplicates) > 0:
            # For each duplicate name, find all rows with that name
            for dup_name in duplicates.index:
                dup_rows = non_empty_df[non_empty_df['Name'] == dup_name]
                for idx in dup_rows.index:
                    failed_rows.append({
                        'row': idx + 2,
                        'name': str(dup_name)[:50],  # Truncate if long
                        'reason': f'Duplicate name (appears {duplicates[dup_name]} times)'
                    })
    
    error_count = len(failed_rows)
    pass_count = total_rows - error_count
    
    if error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {total_rows} fixtures have unique, non-empty names",
            error_count=0,
            pass_count=total_rows,
            details=f"Validated {total_rows} fixture names - all unique and populated"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total fixtures with name issues: {error_count}/{total_rows}"]
        
        # Count empty vs duplicate
        empty_count = sum(1 for f in failed_rows if f['reason'].startswith('Empty'))
        dup_count = error_count - empty_count
        
        if empty_count > 0:
            details_lines.append(f"  - Empty/blank names: {empty_count}")
        if dup_count > 0:
            details_lines.append(f"  - Duplicate names: {dup_count}")
        
        details_lines.append("\nFailed Records (showing first 10):")
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']}: Name='{fail['name']}' - {fail['reason']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {total_rows} fixtures have empty or duplicate names",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_type_dimensions(df: pd.DataFrame) -> ValidationResult:
    """Validate that fixture dimensions match expected values for each Type.
    
    Requirements:
    - Shelf: Width = 48, Depth = 24
    - Rod: Width = 0.5, Depth = 21
    - Bar: Width = 48, Depth = 0.5
    - Pegboard: Width = 46, Depth = 0.25
    - Width/Depth cannot be null or blank
    
    Args:
        df: DataFrame with 'Type', 'Width', and 'Depth' columns
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Type_Dimensions"
    
    # Check if required columns exist
    required_cols = ['Type', 'Width', 'Depth']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message=f"Missing columns: {', '.join(missing_cols)}",
            error_count=0,
            pass_count=0,
            details="Cannot validate - required columns do not exist"
        )
    
    # Define expected dimensions for each type
    TYPE_DIMENSIONS = {
        'Shelf': {'Width': 48, 'Depth': 24},
        'Rod': {'Width': 0.5, 'Depth': 21},
        'Bar': {'Width': 48, 'Depth': 0.5},
        'Pegboard': {'Width': 46, 'Depth': 0.25}
        # Obstruction - no validation rules
    }
    
    total_rows = len(df)
    failed_rows = []
    
    for idx, row in df.iterrows():
        fixture_type = str(row['Type']).strip()
        width_val = row['Width']
        depth_val = row['Depth']
        name = row.get('Name', 'N/A')
        
        # Check for null/blank Width or Depth
        width_is_null = pd.isna(width_val) or str(width_val).strip() == ''
        depth_is_null = pd.isna(depth_val) or str(depth_val).strip() == ''
        
        if width_is_null or depth_is_null:
            failed_rows.append({
                'row': idx + 2,
                'name': str(name)[:30],
                'type': fixture_type,
                'width': '<NULL>' if width_is_null else width_val,
                'depth': '<NULL>' if depth_is_null else depth_val,
                'reason': 'Width/Depth is null or blank'
            })
            continue
        
        # Skip validation for types not in our rules (e.g., Obstruction)
        if fixture_type not in TYPE_DIMENSIONS:
            continue
        
        # Get expected dimensions
        expected = TYPE_DIMENSIONS[fixture_type]
        expected_width = expected['Width']
        expected_depth = expected['Depth']
        
        # Convert to float for comparison
        try:
            actual_width = float(str(width_val).strip())
            actual_depth = float(str(depth_val).strip())
        except (ValueError, TypeError):
            failed_rows.append({
                'row': idx + 2,
                'name': str(name)[:30],
                'type': fixture_type,
                'width': width_val,
                'depth': depth_val,
                'reason': 'Cannot convert Width/Depth to number'
            })
            continue
        
        # Check if dimensions match (with small tolerance for floating point)
        width_matches = abs(actual_width - expected_width) < 0.01
        depth_matches = abs(actual_depth - expected_depth) < 0.01
        
        if not width_matches or not depth_matches:
            failed_rows.append({
                'row': idx + 2,
                'name': str(name)[:30],
                'type': fixture_type,
                'width': actual_width,
                'depth': actual_depth,
                'expected_width': expected_width,
                'expected_depth': expected_depth,
                'reason': f"Expected Width={expected_width}, Depth={expected_depth} but got Width={actual_width}, Depth={actual_depth}"
            })
    
    error_count = len(failed_rows)
    pass_count = total_rows - error_count
    
    if error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {total_rows} fixtures have correct dimensions for their Type",
            error_count=0,
            pass_count=total_rows,
            details=f"Validated dimensions for Shelf, Rod, Bar, and Pegboard types"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total fixtures with dimension errors: {error_count}/{total_rows}"]
        details_lines.append("\nFailed Records (showing first 10):")
        
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']} ({fail['type']}): {fail['name']} - {fail['reason']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {total_rows} fixtures have incorrect dimensions for their Type",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_y_not_equal_notch(df: pd.DataFrame) -> ValidationResult:
    """Validate that Y does not equal Notch.
    
    Requirement: Y field must NOT equal Notch field
    
    Args:
        df: DataFrame with 'Y' and 'Notch' columns
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Y_Not_Equal_Notch"
    
    # Check if required columns exist
    required_cols = ['Y', 'Notch']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message=f"Missing columns: {', '.join(missing_cols)}",
            error_count=0,
            pass_count=0,
            details="Cannot validate - required columns do not exist"
        )
    
    total_rows = len(df)
    failed_rows = []
    
    for idx, row in df.iterrows():
        y_val = row['Y']
        notch_val = row['Notch']
        name = row.get('Name', 'N/A')
        fixture_type = row.get('Type', 'N/A')
        
        # Convert to string for comparison
        y_str = str(y_val).strip()
        notch_str = str(notch_val).strip()
        
        # Check if Y equals Notch
        if y_str == notch_str and y_str != '' and y_str.lower() != 'nan':
            failed_rows.append({
                'row': idx + 2,
                'name': str(name)[:30],
                'type': fixture_type,
                'y': y_val,
                'notch': notch_val,
                'reason': f'Y ({y_val}) equals Notch ({notch_val})'
            })
    
    error_count = len(failed_rows)
    pass_count = total_rows - error_count
    
    if error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {total_rows} fixtures have Y != Notch",
            error_count=0,
            pass_count=total_rows,
            details=f"Validated that Y does not equal Notch for all records"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total fixtures where Y = Notch: {error_count}/{total_rows}"]
        details_lines.append("\nFailed Records (showing first 10):")
        
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']} ({fail['type']}): {fail['name']} - {fail['reason']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {total_rows} fixtures have Y = Notch (not allowed)",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_deck_shelf_y(df: pd.DataFrame) -> ValidationResult:
    """Validate that DECK Shelves have Y = 5.75.
    
    Requirement: If Type = 'Shelf' AND Name starts with 'DECK', then Y must = 5.75
    
    Args:
        df: DataFrame with 'Type', 'Name', and 'Y' columns
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Deck_Shelf_Y"
    
    # Check if required columns exist
    required_cols = ['Type', 'Name', 'Y']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message=f"Missing columns: {', '.join(missing_cols)}",
            error_count=0,
            pass_count=0,
            details="Cannot validate - required columns do not exist"
        )
    
    total_rows = len(df)
    failed_rows = []
    deck_shelf_count = 0
    
    for idx, row in df.iterrows():
        fixture_type = str(row['Type']).strip()
        name = str(row['Name']).strip()
        y_val = row['Y']
        
        # Check if this is a DECK Shelf
        is_shelf = fixture_type == 'Shelf'
        starts_with_deck = name.upper().startswith('DECK')
        
        if is_shelf and starts_with_deck:
            deck_shelf_count += 1
            
            # Check if Y is null/blank
            if pd.isna(y_val) or str(y_val).strip() == '':
                failed_rows.append({
                    'row': idx + 2,
                    'name': name[:30],
                    'y': '<NULL>',
                    'reason': 'Y is null or blank (expected 5.75)'
                })
                continue
            
            # Convert to float and check if equals 5.75
            try:
                y_float = float(str(y_val).strip())
                expected_y = 5.75
                
                # Check with small tolerance for floating point
                if abs(y_float - expected_y) >= 0.01:
                    failed_rows.append({
                        'row': idx + 2,
                        'name': name[:30],
                        'y': y_float,
                        'reason': f'Y = {y_float} (expected 5.75)'
                    })
            except (ValueError, TypeError):
                failed_rows.append({
                    'row': idx + 2,
                    'name': name[:30],
                    'y': y_val,
                    'reason': f'Cannot convert Y to number (expected 5.75)'
                })
    
    error_count = len(failed_rows)
    pass_count = deck_shelf_count - error_count
    
    if deck_shelf_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"No DECK Shelves found (validation skipped)",
            error_count=0,
            pass_count=total_rows,
            details="No fixtures with Type='Shelf' and Name starting with 'DECK'"
        )
    elif error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {deck_shelf_count} DECK Shelves have Y = 5.75",
            error_count=0,
            pass_count=deck_shelf_count,
            details=f"Validated {deck_shelf_count} DECK Shelf fixtures"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total DECK Shelves with incorrect Y: {error_count}/{deck_shelf_count}"]
        details_lines.append("\nFailed Records (showing first 10):")
        
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']}: {fail['name']} - {fail['reason']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {deck_shelf_count} DECK Shelves have Y != 5.75",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_shelf_z(df: pd.DataFrame) -> ValidationResult:
    """Validate that Shelves have correct Z values based on DECK/non-DECK.
    
    Requirements:
    - DECK Shelf: Z = 0.25
    - Non-DECK Shelf: Z = 1.25
    
    Args:
        df: DataFrame with 'Type', 'Name', and 'Z' columns
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Shelf_Z"
    
    # Check if required columns exist
    required_cols = ['Type', 'Name', 'Z']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message=f"Missing columns: {', '.join(missing_cols)}",
            error_count=0,
            pass_count=0,
            details="Cannot validate - required columns do not exist"
        )
    
    total_rows = len(df)
    failed_rows = []
    shelf_count = 0
    
    for idx, row in df.iterrows():
        fixture_type = str(row['Type']).strip()
        name = str(row['Name']).strip()
        z_val = row['Z']
        
        # Only validate Shelves
        if fixture_type != 'Shelf':
            continue
        
        shelf_count += 1
        
        # Determine if DECK or non-DECK shelf
        is_deck = name.upper().startswith('DECK')
        expected_z = 0.25 if is_deck else 1.25
        shelf_type = 'DECK Shelf' if is_deck else 'Non-DECK Shelf'
        
        # Check if Z is null/blank
        if pd.isna(z_val) or str(z_val).strip() == '':
            failed_rows.append({
                'row': idx + 2,
                'name': name[:30],
                'shelf_type': shelf_type,
                'z': '<NULL>',
                'expected_z': expected_z,
                'reason': f'Z is null or blank (expected {expected_z})'
            })
            continue
        
        # Convert to float and check
        try:
            z_float = float(str(z_val).strip())
            
            # Check with small tolerance for floating point
            if abs(z_float - expected_z) >= 0.01:
                failed_rows.append({
                    'row': idx + 2,
                    'name': name[:30],
                    'shelf_type': shelf_type,
                    'z': z_float,
                    'expected_z': expected_z,
                    'reason': f'{shelf_type}: Z = {z_float} (expected {expected_z})'
                })
        except (ValueError, TypeError):
            failed_rows.append({
                'row': idx + 2,
                'name': name[:30],
                'shelf_type': shelf_type,
                'z': z_val,
                'expected_z': expected_z,
                'reason': f'Cannot convert Z to number (expected {expected_z})'
            })
    
    error_count = len(failed_rows)
    pass_count = shelf_count - error_count
    
    if shelf_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"No Shelves found (validation skipped)",
            error_count=0,
            pass_count=total_rows,
            details="No fixtures with Type='Shelf'"
        )
    elif error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {shelf_count} Shelves have correct Z values (DECK=0.25, Non-DECK=1.25)",
            error_count=0,
            pass_count=shelf_count,
            details=f"Validated {shelf_count} Shelf fixtures"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total Shelves with incorrect Z: {error_count}/{shelf_count}"]
        details_lines.append("\nFailed Records (showing first 10):")
        
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']}: {fail['name']} - {fail['reason']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {shelf_count} Shelves have incorrect Z values",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_shelf_overhangs(df: pd.DataFrame) -> ValidationResult:
    """Validate that all Shelves have Left_Overhang, Right_Overhang, Front_Overhang = 0.
    
    Requirements:
    - For all Shelves: Left_Overhang = 0, Right_Overhang = 0, Front_Overhang = 0
    
    Args:
        df: DataFrame with 'Type', 'Left_Overhang', 'Right_Overhang', 'Front_Overhang' columns
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Shelf_Overhangs"
    
    # Check if required columns exist
    required_cols = ['Type', 'Left_Overhang', 'Right_Overhang', 'Front_Overhang']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message=f"Missing columns: {', '.join(missing_cols)}",
            error_count=0,
            pass_count=0,
            details="Cannot validate - required columns do not exist"
        )
    
    total_rows = len(df)
    failed_rows = []
    shelf_count = 0
    
    for idx, row in df.iterrows():
        fixture_type = str(row['Type']).strip()
        name = row.get('Name', 'N/A')
        
        # Only validate Shelves
        if fixture_type != 'Shelf':
            continue
        
        shelf_count += 1
        
        left_val = row['Left_Overhang']
        right_val = row['Right_Overhang']
        front_val = row['Front_Overhang']
        
        # Check each overhang field
        errors = []
        
        # Check Left_Overhang
        if pd.isna(left_val) or str(left_val).strip() == '':
            errors.append('Left_Overhang is null/blank')
        else:
            try:
                left_float = float(str(left_val).strip())
                if abs(left_float - 0) >= 0.01:
                    errors.append(f'Left_Overhang={left_float}')
            except (ValueError, TypeError):
                errors.append('Left_Overhang is not a number')
        
        # Check Right_Overhang
        if pd.isna(right_val) or str(right_val).strip() == '':
            errors.append('Right_Overhang is null/blank')
        else:
            try:
                right_float = float(str(right_val).strip())
                if abs(right_float - 0) >= 0.01:
                    errors.append(f'Right_Overhang={right_float}')
            except (ValueError, TypeError):
                errors.append('Right_Overhang is not a number')
        
        # Check Front_Overhang
        if pd.isna(front_val) or str(front_val).strip() == '':
            errors.append('Front_Overhang is null/blank')
        else:
            try:
                front_float = float(str(front_val).strip())
                if abs(front_float - 0) >= 0.01:
                    errors.append(f'Front_Overhang={front_float}')
            except (ValueError, TypeError):
                errors.append('Front_Overhang is not a number')
        
        if errors:
            failed_rows.append({
                'row': idx + 2,
                'name': str(name)[:30],
                'errors': ', '.join(errors)
            })
    
    error_count = len(failed_rows)
    pass_count = shelf_count - error_count
    
    if shelf_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"No Shelves found (validation skipped)",
            error_count=0,
            pass_count=total_rows,
            details="No fixtures with Type='Shelf'"
        )
    elif error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {shelf_count} Shelves have Left/Right/Front Overhangs = 0",
            error_count=0,
            pass_count=shelf_count,
            details=f"Validated {shelf_count} Shelf fixtures"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total Shelves with non-zero overhangs: {error_count}/{shelf_count}"]
        details_lines.append("\nFailed Records (showing first 10):")
        
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']}: {fail['name']} - {fail['errors']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {shelf_count} Shelves have non-zero Left/Right/Front Overhangs",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_shelf_back_overhang(df: pd.DataFrame) -> ValidationResult:
    """Validate that Shelves have correct Back_Overhang values based on DECK/non-DECK.
    
    Requirements:
    - DECK Shelf: Back_Overhang = 0
    - Non-DECK Shelf: Back_Overhang = 1.25
    
    Args:
        df: DataFrame with 'Type', 'Name', and 'Back_Overhang' columns
        
    Returns:
        ValidationResult with pass/fail status
    """
    check_name = "Shelf_Back_Overhang"
    
    # Check if required columns exist
    required_cols = ['Type', 'Name', 'Back_Overhang']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return ValidationResult(
            check_name=check_name,
            status="WARNING",
            message=f"Missing columns: {', '.join(missing_cols)}",
            error_count=0,
            pass_count=0,
            details="Cannot validate - required columns do not exist"
        )
    
    total_rows = len(df)
    failed_rows = []
    shelf_count = 0
    
    for idx, row in df.iterrows():
        fixture_type = str(row['Type']).strip()
        name = str(row['Name']).strip()
        back_overhang_val = row['Back_Overhang']
        
        # Only validate Shelves
        if fixture_type != 'Shelf':
            continue
        
        shelf_count += 1
        
        # Determine if DECK or non-DECK shelf
        is_deck = name.upper().startswith('DECK')
        expected_back = 0 if is_deck else 1.25
        shelf_type = 'DECK Shelf' if is_deck else 'Non-DECK Shelf'
        
        # Check if Back_Overhang is null/blank
        if pd.isna(back_overhang_val) or str(back_overhang_val).strip() == '':
            failed_rows.append({
                'row': idx + 2,
                'name': name[:30],
                'shelf_type': shelf_type,
                'back_overhang': '<NULL>',
                'expected_back': expected_back,
                'reason': f'Back_Overhang is null or blank (expected {expected_back})'
            })
            continue
        
        # Convert to float and check
        try:
            back_float = float(str(back_overhang_val).strip())
            
            # Check with small tolerance for floating point
            if abs(back_float - expected_back) >= 0.01:
                failed_rows.append({
                    'row': idx + 2,
                    'name': name[:30],
                    'shelf_type': shelf_type,
                    'back_overhang': back_float,
                    'expected_back': expected_back,
                    'reason': f'{shelf_type}: Back_Overhang = {back_float} (expected {expected_back})'
                })
        except (ValueError, TypeError):
            failed_rows.append({
                'row': idx + 2,
                'name': name[:30],
                'shelf_type': shelf_type,
                'back_overhang': back_overhang_val,
                'expected_back': expected_back,
                'reason': f'Cannot convert Back_Overhang to number (expected {expected_back})'
            })
    
    error_count = len(failed_rows)
    pass_count = shelf_count - error_count
    
    if shelf_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"No Shelves found (validation skipped)",
            error_count=0,
            pass_count=total_rows,
            details="No fixtures with Type='Shelf'"
        )
    elif error_count == 0:
        result = ValidationResult(
            check_name=check_name,
            status="PASS",
            message=f"All {shelf_count} Shelves have correct Back_Overhang values (DECK=0, Non-DECK=1.25)",
            error_count=0,
            pass_count=shelf_count,
            details=f"Validated {shelf_count} Shelf fixtures"
        )
    else:
        # Build detailed error message
        details_lines = [f"Total Shelves with incorrect Back_Overhang: {error_count}/{shelf_count}"]
        details_lines.append("\nFailed Records (showing first 10):")
        
        for fail in failed_rows[:10]:
            details_lines.append(
                f"  Row {fail['row']}: {fail['name']} - {fail['reason']}"
            )
        
        if len(failed_rows) > 10:
            details_lines.append(f"  ... and {len(failed_rows) - 10} more")
        
        result = ValidationResult(
            check_name=check_name,
            status="FAIL",
            message=f"{error_count} of {shelf_count} Shelves have incorrect Back_Overhang values",
            error_count=error_count,
            pass_count=pass_count,
            details='\n'.join(details_lines)
        )
    
    return result


def validate_fixture_data(fixture_rows: List[List[str]], df: pd.DataFrame = None) -> tuple[List[ValidationResult], dict]:
    """Run all fixture validations.
    
    Args:
        fixture_rows: List of Fixture rows from PSA
        df: Optional DataFrame with mapped/cleaned data for field-level checks
        
    Returns:
        Tuple of (validation_results, summary_dict)
    """
    print("[FIXTURE VALIDATOR] Starting validation checks...")
    
    validation_results = []
    
    # Validation 1: Field Count
    field_count_result = validate_field_count(fixture_rows)
    validation_results.append(field_count_result)
    print(f"[FIXTURE VALIDATOR] Field_Count: {field_count_result.status}")
    
    # Validation 2: Unique Names (if DataFrame provided)
    if df is not None:
        unique_name_result = validate_unique_names(df)
        validation_results.append(unique_name_result)
        print(f"[FIXTURE VALIDATOR] Unique_Name: {unique_name_result.status}")
        
        # Validation 3: Type Dimensions
        type_dimensions_result = validate_type_dimensions(df)
        validation_results.append(type_dimensions_result)
        print(f"[FIXTURE VALIDATOR] Type_Dimensions: {type_dimensions_result.status}")
        
        # Validation 4: Y Not Equal Notch
        y_notch_result = validate_y_not_equal_notch(df)
        validation_results.append(y_notch_result)
        print(f"[FIXTURE VALIDATOR] Y_Not_Equal_Notch: {y_notch_result.status}")
        
        # Validation 5: DECK Shelf Y Check
        deck_shelf_y_result = validate_deck_shelf_y(df)
        validation_results.append(deck_shelf_y_result)
        print(f"[FIXTURE VALIDATOR] Deck_Shelf_Y: {deck_shelf_y_result.status}")
        
        # Validation 6: Shelf Z Check
        shelf_z_result = validate_shelf_z(df)
        validation_results.append(shelf_z_result)
        print(f"[FIXTURE VALIDATOR] Shelf_Z: {shelf_z_result.status}")
        
        # Validation 7: Shelf Overhangs Check
        shelf_overhangs_result = validate_shelf_overhangs(df)
        validation_results.append(shelf_overhangs_result)
        print(f"[FIXTURE VALIDATOR] Shelf_Overhangs: {shelf_overhangs_result.status}")
        
        # Validation 8: Shelf Back_Overhang Check
        shelf_back_overhang_result = validate_shelf_back_overhang(df)
        validation_results.append(shelf_back_overhang_result)
        print(f"[FIXTURE VALIDATOR] Shelf_Back_Overhang: {shelf_back_overhang_result.status}")
    
    # TODO: Add more validations here as we build them
    
    # Calculate summary
    total_checks = len(validation_results)
    passed = sum(1 for r in validation_results if r.passed)
    failed = sum(1 for r in validation_results if not r.passed and r.status == 'FAIL')
    warnings = sum(1 for r in validation_results if r.status == 'WARNING')
    
    summary = {
        'total_checks': total_checks,
        'passed': passed,
        'failed': failed,
        'warnings': warnings,
        'overall_status': 'PASS' if failed == 0 else 'FAIL'
    }
    
    print(f"[FIXTURE VALIDATOR] Validation complete: {passed} passed, {failed} failed, {warnings} warnings")
    
    return validation_results, summary
