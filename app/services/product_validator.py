from __future__ import annotations

import io
import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    error_count: int = 0
    pass_count: int = 0
    details: str = ""


class DataValidator:
    """Validates Product data with multiple checks.
    
    Designed to handle up to 90+ validation checks in a clean, maintainable way.
    """
    
    def __init__(self, df: pd.DataFrame, excel_reference_bytes: Optional[bytes] = None):
        self.df = df
        self.excel_reference_bytes = excel_reference_bytes
        self.results: List[ValidationResult] = []
    
    def run_all_checks(self) -> List[ValidationResult]:
        """Run all validation checks and return results."""
        self.results = []
        
        # Run each check
        self.check_relay_id_uniformity()
        self.check_upc_length()
        self.check_order_type_invalid_values()
        self.check_peg_hole_x_vs_width()
        self.check_peg_hole_2x_position()
        self.check_height_inches_invalid()
        self.check_width_inches_invalid()
        self.check_depth_inches_invalid()
        self.check_squeeze_high_must_equal_one()
        self.check_expand_wide_must_equal_one()
        self.check_expand_high_must_equal_one()
        self.check_squeeze_deep_must_equal_one()
        self.check_squeeze_wide_must_equal_one()
        self.check_expand_deep_must_equal_one()
        self.check_front_overhang_inches_less_than_one()
        self.check_peg_id_required_when_peg_holes_exist()
        self.check_alt_upc_must_be_null()
        
        # Run Has_Alt_UPC validation against Excel reference (if provided)
        if self.excel_reference_bytes:
            self.check_has_alt_upc_against_excel_reference()
        
        # TODO: Add more checks here as we build them (73 more to go!)
        # etc...
        
        return self.results
    
    def check_relay_id_uniformity(self) -> ValidationResult:
        """Check if Relay_ID is uniform across all UPCs.
        
        Better approach than avg():
        - Count unique Relay_IDs
        - If only 1 unique value → PASS
        - If multiple values → FAIL and show which UPCs differ
        """
        check_name = "Relay_ID Uniformity"
        
        if 'Relay_ID' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Relay_ID column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Get unique Relay_IDs
        unique_relay_ids = self.df['Relay_ID'].dropna().unique()
        
        if len(unique_relay_ids) == 0:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="No Relay_ID values found",
                error_count=0,
                pass_count=0,
                details="All Relay_ID values are null/empty"
            )
        elif len(unique_relay_ids) == 1:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All UPCs have uniform Relay_ID: {unique_relay_ids[0]}",
                error_count=0,
                pass_count=len(self.df),
                details=f"Total UPCs checked: {len(self.df)}"
            )
        else:
            # Multiple Relay_IDs found - FAIL
            # Count how many UPCs have each Relay_ID
            relay_counts = self.df['Relay_ID'].value_counts()
            
            # Find the expected value (most common)
            expected_relay_id = relay_counts.index[0]
            
            # Find UPCs that don't match
            error_rows = self.df[self.df['Relay_ID'] != expected_relay_id]
            error_count = len(error_rows)
            
            # Create detailed error message
            details_lines = [
                f"Expected Relay_ID: {expected_relay_id} ({relay_counts.iloc[0]} UPCs)",
                f"Found {len(unique_relay_ids)} different Relay_IDs:"
            ]
            for relay_id, count in relay_counts.items():
                details_lines.append(f"  - {relay_id}: {count} UPCs")
            
            # Show sample of problematic UPCs
            if 'UPC' in self.df.columns and error_count > 0:
                sample_upcs = error_rows['UPC'].head(5).tolist()
                details_lines.append(f"\nSample UPCs with different Relay_ID:")
                for upc in sample_upcs:
                    upc_relay = error_rows[error_rows['UPC'] == upc]['Relay_ID'].iloc[0]
                    details_lines.append(f"  - UPC {upc}: Relay_ID = {upc_relay}")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Non-uniform Relay_IDs found: {len(unique_relay_ids)} different values",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_upc_length(self) -> ValidationResult:
        """Check if all UPCs are exactly 13 characters long.
        
        UPCs should be 13-digit numbers (EAN-13/GTIN-13).
        Checks for:
        - Missing UPCs (null/empty)
        - UPCs shorter than 13 digits
        - UPCs longer than 13 digits
        - Leading/trailing zeros are preserved and counted
        """
        check_name = "UPC Length (13 digits)"
        
        if 'UPC' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="UPC column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert UPC to string to check length (preserves leading zeros)
        upc_series = self.df['UPC'].astype(str)
        
        # Find problematic UPCs
        null_upcs = self.df[self.df['UPC'].isna()]
        invalid_length_upcs = self.df[upc_series.str.len() != 13]
        
        total_errors = len(null_upcs) + len(invalid_length_upcs)
        
        if total_errors == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} UPCs are exactly 13 digits",
                error_count=0,
                pass_count=len(self.df),
                details="All UPCs meet the 13-digit requirement"
            )
        else:
            # Build detailed error report
            details_lines = []
            
            # Report null/empty UPCs
            if len(null_upcs) > 0:
                details_lines.append(f"Null/Empty UPCs: {len(null_upcs)}")
                if 'Item_Number' in self.df.columns or 'Item_1_Description' in self.df.columns:
                    sample = null_upcs.head(3)
                    for idx, row in sample.iterrows():
                        item_info = row.get('Item_Number', 'N/A')
                        desc = row.get('Item_1_Description', 'N/A')
                        details_lines.append(f"  - Row {idx}: Item {item_info} ({desc})")
            
            # Report invalid length UPCs
            if len(invalid_length_upcs) > 0:
                details_lines.append(f"\nInvalid Length UPCs: {len(invalid_length_upcs)}")
                
                # Group by length
                length_counts = upc_series[upc_series.str.len() != 13].str.len().value_counts().sort_index()
                details_lines.append("Length distribution:")
                for length, count in length_counts.items():
                    details_lines.append(f"  - {int(length)} digits: {count} UPCs")
                
                # Show samples
                details_lines.append("\nSample invalid UPCs:")
                sample = invalid_length_upcs.head(5)
                for idx, row in sample.iterrows():
                    upc = str(row['UPC'])
                    upc_len = len(upc)
                    item_info = row.get('Item_Number', 'N/A')
                    details_lines.append(f"  - '{upc}' ({upc_len} digits) - Item {item_info}")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {total_errors} UPCs with incorrect length (expected 13 digits)",
                error_count=total_errors,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_order_type_invalid_values(self) -> ValidationResult:
        """Check if Order_Type contains invalid values (exact match).
        
        Invalid Order_Type values (exact match):
        - '03', '07', '43', '3', '7'
        
        These values should be flagged as errors.
        All other values are acceptable.
        """
        check_name = "Order_Type Invalid Values"
        
        if 'Order_Type' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Order_Type column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Define invalid values (exact match)
        invalid_values = ['03', '07', '43', '3', '7']
        
        # Convert Order_Type to string for comparison
        order_type_series = self.df['Order_Type'].astype(str)
        
        # Find rows with invalid Order_Type values
        error_mask = order_type_series.isin(invalid_values)
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have valid Order_Type values",
                error_count=0,
                pass_count=len(self.df),
                details=f"No invalid values found. Checked against: {', '.join(invalid_values)}"
            )
        else:
            # Build detailed error report
            details_lines = [
                f"Found {error_count} products with invalid Order_Type values",
                f"Invalid values to avoid: {', '.join(invalid_values)}",
                ""
            ]
            
            # Count occurrences of each invalid value
            invalid_value_counts = order_type_series[error_mask].value_counts()
            details_lines.append("Distribution of invalid values:")
            for value, count in invalid_value_counts.items():
                details_lines.append(f"  - Order_Type '{value}': {count} products")
            
            # Show sample of problematic products
            details_lines.append("\nSample products with invalid Order_Type:")
            sample = error_rows.head(5)
            for idx, row in sample.iterrows():
                order_type = str(row['Order_Type'])
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Order_Type = '{order_type}' | {desc}"
                )
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products with invalid Order_Type values ({', '.join(invalid_values)})",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_peg_hole_x_vs_width(self) -> ValidationResult:
        """Check if Peg_Hole_X is less than Width_Inches.
        
        Business Rule:
        - Peg hole X-position must be within the product width
        - If Peg_Hole_X >= Width_Inches → FAIL (peg hole exceeds width)
        - If Peg_Hole_X < Width_Inches → PASS
        
        Special Cases (PASS/Skip):
        - Null or empty values → PASS (skip check)
        - Zero values → PASS (skip check)
        - Only validate when both values are > 0
        """
        check_name = "Peg_Hole_X vs Width"
        
        # Check if required columns exist
        missing_cols = []
        if 'Peg_Hole_X' not in self.df.columns:
            missing_cols.append('Peg_Hole_X')
        if 'Width_Inches' not in self.df.columns:
            missing_cols.append('Width_Inches')
        
        if missing_cols:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message=f"Required columns not found: {', '.join(missing_cols)}",
                error_count=0,
                pass_count=len(self.df),
                details="Cannot perform check without required columns"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric, treating errors as NaN
        peg_hole_x = pd.to_numeric(self.df['Peg_Hole_X'], errors='coerce')
        width = pd.to_numeric(self.df['Width_Inches'], errors='coerce')
        
        # Only check rows where both values are > 0 (skip null/0)
        valid_mask = (peg_hole_x > 0) & (width > 0)
        
        # Among valid rows, find where Peg_Hole_X >= Width
        error_mask = valid_mask & (peg_hole_x >= width)
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        # Count how many rows were actually checked
        checked_count = valid_mask.sum()
        skipped_count = len(self.df) - checked_count
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All products have Peg_Hole_X < Width",
                error_count=0,
                pass_count=len(self.df),
                details=f"Checked {checked_count} products (skipped {skipped_count} with null/zero values)"
            )
        else:
            # Build detailed error report
            details_lines = [
                f"Found {error_count} products where Peg_Hole_X >= Width",
                f"Total checked: {checked_count} products",
                f"Skipped: {skipped_count} products (null or zero values)",
                ""
            ]
            
            # Show sample of problematic products
            details_lines.append("Sample products with Peg_Hole_X >= Width:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                peg_x = row['Peg_Hole_X']
                width_val = row['Width_Inches']
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]  # Truncate description
                
                details_lines.append(
                    f"  - UPC {upc}: Peg_Hole_X={peg_x}, Width={width_val} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Peg_Hole_X >= Width (should be less than)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_peg_hole_2x_position(self) -> ValidationResult:
        """Check if Peg_Hole_2X is positioned correctly between Peg_Holes and Width.
        
        Business Rule:
        - Second peg hole X-position must be between first peg hole and product width
        - If Peg_Hole_2X is 0 or null → PASS (skip check)
        - If Peg_Hole_2X > 0 → Must satisfy: Peg_Holes < Peg_Hole_2X < Width
        
        Special Cases (PASS/Skip):
        - Peg_Hole_2X is null or 0 → PASS (no second peg hole)
        """
        check_name = "Peg_Hole_2X Position"
        
        # Check if required columns exist
        missing_cols = []
        if 'Peg_Hole_2X' not in self.df.columns:
            missing_cols.append('Peg_Hole_2X')
        if 'Peg_Holes' not in self.df.columns:
            missing_cols.append('Peg_Holes')
        if 'Width_Inches' not in self.df.columns:
            missing_cols.append('Width_Inches')
        
        if missing_cols:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message=f"Required columns not found: {', '.join(missing_cols)}",
                error_count=0,
                pass_count=len(self.df),
                details="Cannot perform check without required columns"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric, treating errors as NaN
        peg_hole_2x = pd.to_numeric(self.df['Peg_Hole_2X'], errors='coerce')
        peg_holes = pd.to_numeric(self.df['Peg_Holes'], errors='coerce')
        width = pd.to_numeric(self.df['Width_Inches'], errors='coerce')
        
        # Only check rows where Peg_Hole_2X > 0 (skip null/0)
        valid_mask = peg_hole_2x > 0
        
        # Among valid rows, check if: Peg_Holes < Peg_Hole_2X < Width
        # FAIL if: Peg_Hole_2X <= Peg_Holes OR Peg_Hole_2X >= Width
        error_mask = valid_mask & (~((peg_holes < peg_hole_2x) & (peg_hole_2x < width)))
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        # Count how many rows were actually checked
        checked_count = valid_mask.sum()
        skipped_count = len(self.df) - checked_count
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All products have correct Peg_Hole_2X positioning",
                error_count=0,
                pass_count=len(self.df),
                details=f"Checked {checked_count} products with Peg_Hole_2X > 0 (skipped {skipped_count} with null/zero values)"
            )
        else:
            # Build detailed error report
            details_lines = [
                f"Found {error_count} products where Peg_Hole_2X is NOT between Peg_Holes and Width",
                f"Expected: Peg_Holes < Peg_Hole_2X < Width",
                f"Total checked: {checked_count} products",
                f"Skipped: {skipped_count} products (Peg_Hole_2X is null or zero)",
                ""
            ]
            
            # Show sample of problematic products
            details_lines.append("Sample products with incorrect Peg_Hole_2X positioning:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                peg_hole_val = row['Peg_Holes']
                peg_2x_val = row['Peg_Hole_2X']
                width_val = row['Width_Inches']
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]  # Truncate description
                
                # Determine the specific issue
                issue = ""
                if pd.notna(peg_hole_val) and peg_2x_val <= peg_hole_val:
                    issue = "(2nd peg <= 1st peg)"
                elif pd.notna(width_val) and peg_2x_val >= width_val:
                    issue = "(2nd peg >= width)"
                elif pd.isna(peg_hole_val) or pd.isna(width_val):
                    issue = "(missing Peg_Holes or Width)"
                
                details_lines.append(
                    f"  - UPC {upc}: Peg_Holes={peg_hole_val}, Peg_Hole_2X={peg_2x_val}, Width={width_val} {issue}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Peg_Hole_2X positioning is incorrect",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_height_inches_invalid(self) -> ValidationResult:
        """Check if Height_Inches has invalid values.
        
        Business Rules - FAIL if:
        1. Height_Inches is null or empty
        2. Height_Inches = 0
        3. Height_Inches = 1
        4. Height_Inches = 2 AND Width_Inches = 2 AND Depth_Inches = 2 (all three = 2)
        """
        check_name = "Height_Inches Invalid Values"
        
        if 'Height_Inches' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Height_Inches column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        height = pd.to_numeric(self.df['Height_Inches'], errors='coerce')
        width = pd.to_numeric(self.df.get('Width_Inches', pd.Series([None] * len(self.df))), errors='coerce')
        depth = pd.to_numeric(self.df.get('Depth_Inches', pd.Series([None] * len(self.df))), errors='coerce')
        
        # Build error conditions
        null_or_zero = height.isna() | (height == 0)
        equals_one = height == 1
        all_equal_two = (height == 2) & (width == 2) & (depth == 2)
        
        # Combine all error conditions
        error_mask = null_or_zero | equals_one | all_equal_two
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have valid Height_Inches values",
                error_count=0,
                pass_count=len(self.df),
                details="No invalid Height_Inches values found"
            )
        else:
            # Categorize errors
            null_zero_count = null_or_zero.sum()
            equals_one_count = equals_one.sum()
            all_two_count = all_equal_two.sum()
            
            details_lines = [
                f"Found {error_count} products with invalid Height_Inches",
                "",
                "Error breakdown:"
            ]
            
            if null_zero_count > 0:
                details_lines.append(f"  - Null or Zero: {null_zero_count} products")
            if equals_one_count > 0:
                details_lines.append(f"  - Equals 1: {equals_one_count} products")
            if all_two_count > 0:
                details_lines.append(f"  - All dimensions = 2 (H=2, W=2, D=2): {all_two_count} products")
            
            # Show samples
            details_lines.append("\nSample products with invalid Height_Inches:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                h = row.get('Height_Inches', 'N/A')
                w = row.get('Width_Inches', 'N/A')
                d = row.get('Depth_Inches', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                
                # Determine issue
                issue = ""
                if pd.isna(h) or h == 0:
                    issue = "null/zero"
                elif h == 1:
                    issue = "equals 1"
                elif h == 2 and w == 2 and d == 2:
                    issue = "all dims = 2"
                
                details_lines.append(
                    f"  - UPC {upc}: H={h}, W={w}, D={d} ({issue})"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products with invalid Height_Inches",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_width_inches_invalid(self) -> ValidationResult:
        """Check if Width_Inches has invalid values.
        
        Business Rules - FAIL if:
        1. Width_Inches is null or empty
        2. Width_Inches = 0
        3. Width_Inches = 1
        4. Width_Inches = 2 AND Height_Inches = 2 AND Depth_Inches = 2 (all three = 2)
        """
        check_name = "Width_Inches Invalid Values"
        
        if 'Width_Inches' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Width_Inches column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        width = pd.to_numeric(self.df['Width_Inches'], errors='coerce')
        height = pd.to_numeric(self.df.get('Height_Inches', pd.Series([None] * len(self.df))), errors='coerce')
        depth = pd.to_numeric(self.df.get('Depth_Inches', pd.Series([None] * len(self.df))), errors='coerce')
        
        # Build error conditions
        null_or_zero = width.isna() | (width == 0)
        equals_one = width == 1
        all_equal_two = (width == 2) & (height == 2) & (depth == 2)
        
        # Combine all error conditions
        error_mask = null_or_zero | equals_one | all_equal_two
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have valid Width_Inches values",
                error_count=0,
                pass_count=len(self.df),
                details="No invalid Width_Inches values found"
            )
        else:
            # Categorize errors
            null_zero_count = null_or_zero.sum()
            equals_one_count = equals_one.sum()
            all_two_count = all_equal_two.sum()
            
            details_lines = [
                f"Found {error_count} products with invalid Width_Inches",
                "",
                "Error breakdown:"
            ]
            
            if null_zero_count > 0:
                details_lines.append(f"  - Null or Zero: {null_zero_count} products")
            if equals_one_count > 0:
                details_lines.append(f"  - Equals 1: {equals_one_count} products")
            if all_two_count > 0:
                details_lines.append(f"  - All dimensions = 2 (H=2, W=2, D=2): {all_two_count} products")
            
            # Show samples
            details_lines.append("\nSample products with invalid Width_Inches:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                h = row.get('Height_Inches', 'N/A')
                w = row.get('Width_Inches', 'N/A')
                d = row.get('Depth_Inches', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                
                # Determine issue
                issue = ""
                if pd.isna(w) or w == 0:
                    issue = "null/zero"
                elif w == 1:
                    issue = "equals 1"
                elif h == 2 and w == 2 and d == 2:
                    issue = "all dims = 2"
                
                details_lines.append(
                    f"  - UPC {upc}: H={h}, W={w}, D={d} ({issue})"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products with invalid Width_Inches",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_depth_inches_invalid(self) -> ValidationResult:
        """Check if Depth_Inches has invalid values.
        
        Business Rules - FAIL if:
        1. Depth_Inches is null or empty
        2. Depth_Inches = 0
        3. Depth_Inches = 1
        4. Depth_Inches = 2 AND Height_Inches = 2 AND Width_Inches = 2 (all three = 2)
        """
        check_name = "Depth_Inches Invalid Values"
        
        if 'Depth_Inches' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Depth_Inches column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        depth = pd.to_numeric(self.df['Depth_Inches'], errors='coerce')
        height = pd.to_numeric(self.df.get('Height_Inches', pd.Series([None] * len(self.df))), errors='coerce')
        width = pd.to_numeric(self.df.get('Width_Inches', pd.Series([None] * len(self.df))), errors='coerce')
        
        # Build error conditions
        null_or_zero = depth.isna() | (depth == 0)
        equals_one = depth == 1
        all_equal_two = (depth == 2) & (height == 2) & (width == 2)
        
        # Combine all error conditions
        error_mask = null_or_zero | equals_one | all_equal_two
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have valid Depth_Inches values",
                error_count=0,
                pass_count=len(self.df),
                details="No invalid Depth_Inches values found"
            )
        else:
            # Categorize errors
            null_zero_count = null_or_zero.sum()
            equals_one_count = equals_one.sum()
            all_two_count = all_equal_two.sum()
            
            details_lines = [
                f"Found {error_count} products with invalid Depth_Inches",
                "",
                "Error breakdown:"
            ]
            
            if null_zero_count > 0:
                details_lines.append(f"  - Null or Zero: {null_zero_count} products")
            if equals_one_count > 0:
                details_lines.append(f"  - Equals 1: {equals_one_count} products")
            if all_two_count > 0:
                details_lines.append(f"  - All dimensions = 2 (H=2, W=2, D=2): {all_two_count} products")
            
            # Show samples
            details_lines.append("\nSample products with invalid Depth_Inches:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                h = row.get('Height_Inches', 'N/A')
                w = row.get('Width_Inches', 'N/A')
                d = row.get('Depth_Inches', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                
                # Determine issue
                issue = ""
                if pd.isna(d) or d == 0:
                    issue = "null/zero"
                elif d == 1:
                    issue = "equals 1"
                elif h == 2 and w == 2 and d == 2:
                    issue = "all dims = 2"
                
                details_lines.append(
                    f"  - UPC {upc}: H={h}, W={w}, D={d} ({issue})"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products with invalid Depth_Inches",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_squeeze_high_must_equal_one(self) -> ValidationResult:
        """Check if Squeeze_High equals exactly 1.
        
        Business Rule:
        - Squeeze_High MUST equal 1
        - Null, 0, or any other value → FAIL
        """
        check_name = "Squeeze_High Must Equal 1"
        
        if 'Squeeze_High' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Squeeze_High column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        squeeze_high = pd.to_numeric(self.df['Squeeze_High'], errors='coerce')
        
        # Find rows where Squeeze_High != 1 (includes null, 0, and any other value)
        error_mask = squeeze_high != 1
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Squeeze_High = 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize the different invalid values
            null_count = squeeze_high.isna().sum()
            zero_count = (squeeze_high == 0).sum()
            other_values = squeeze_high[~squeeze_high.isin([0, 1]) & squeeze_high.notna()].unique()
            
            details_lines = [
                f"Found {error_count} products where Squeeze_High ≠ 1",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if zero_count > 0:
                details_lines.append(f"  - Equals 0: {zero_count} products")
            if len(other_values) > 0:
                other_count = len(squeeze_high[squeeze_high.isin(other_values)])
                details_lines.append(f"  - Other values: {other_count} products ({', '.join(map(str, other_values[:5]))}...)")
            
            # Show samples
            details_lines.append("\nSample products with Squeeze_High ≠ 1:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                sq_high = row.get('Squeeze_High', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Squeeze_High = {sq_high} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Squeeze_High ≠ 1 (must be exactly 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_expand_wide_must_equal_one(self) -> ValidationResult:
        """Check if Expand_Wide equals exactly 1.
        
        Business Rule:
        - Expand_Wide MUST equal 1
        - Null, 0, or any other value → FAIL (strict)
        """
        check_name = "Expand_Wide Must Equal 1"
        
        if 'Expand_Width' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Expand_Width column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        expand_wide = pd.to_numeric(self.df['Expand_Width'], errors='coerce')
        
        # Find rows where Expand_Wide != 1 (includes null, 0, and any other value)
        error_mask = expand_wide != 1
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Expand_Wide = 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize the different invalid values
            null_count = expand_wide.isna().sum()
            zero_count = (expand_wide == 0).sum()
            other_values = expand_wide[~expand_wide.isin([0, 1]) & expand_wide.notna()].unique()
            
            details_lines = [
                f"Found {error_count} products where Expand_Wide ≠ 1",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if zero_count > 0:
                details_lines.append(f"  - Equals 0: {zero_count} products")
            if len(other_values) > 0:
                other_count = len(expand_wide[expand_wide.isin(other_values)])
                details_lines.append(f"  - Other values: {other_count} products ({', '.join(map(str, other_values[:5]))}...)")
            
            # Show samples
            details_lines.append("\nSample products with Expand_Wide ≠ 1:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                exp_wide = row.get('Expand_Width', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Expand_Wide = {exp_wide} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Expand_Wide ≠ 1 (must be exactly 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_expand_high_must_equal_one(self) -> ValidationResult:
        """Check if Expand_High equals exactly 1.
        
        Business Rule:
        - Expand_High MUST equal 1
        - Null, 0, or any other value → FAIL (strict)
        """
        check_name = "Expand_High Must Equal 1"
        
        if 'Expand_High' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Expand_High column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        expand_high = pd.to_numeric(self.df['Expand_High'], errors='coerce')
        
        # Find rows where Expand_High != 1
        error_mask = expand_high != 1
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Expand_High = 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize the different invalid values
            null_count = expand_high.isna().sum()
            zero_count = (expand_high == 0).sum()
            other_values = expand_high[~expand_high.isin([0, 1]) & expand_high.notna()].unique()
            
            details_lines = [
                f"Found {error_count} products where Expand_High ≠ 1",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if zero_count > 0:
                details_lines.append(f"  - Equals 0: {zero_count} products")
            if len(other_values) > 0:
                other_count = len(expand_high[expand_high.isin(other_values)])
                details_lines.append(f"  - Other values: {other_count} products ({', '.join(map(str, other_values[:5]))}...)")
            
            # Show samples
            details_lines.append("\nSample products with Expand_High ≠ 1:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                val = row.get('Expand_High', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Expand_High = {val} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Expand_High ≠ 1 (must be exactly 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_squeeze_deep_must_equal_one(self) -> ValidationResult:
        """Check if Squeeze_Deep equals exactly 1.
        
        Business Rule:
        - Squeeze_Deep MUST equal 1
        - Null, 0, or any other value → FAIL (strict)
        """
        check_name = "Squeeze_Deep Must Equal 1"
        
        if 'Squeeze_Deep' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Squeeze_Deep column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        squeeze_deep = pd.to_numeric(self.df['Squeeze_Deep'], errors='coerce')
        
        # Find rows where Squeeze_Deep != 1
        error_mask = squeeze_deep != 1
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Squeeze_Deep = 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize the different invalid values
            null_count = squeeze_deep.isna().sum()
            zero_count = (squeeze_deep == 0).sum()
            other_values = squeeze_deep[~squeeze_deep.isin([0, 1]) & squeeze_deep.notna()].unique()
            
            details_lines = [
                f"Found {error_count} products where Squeeze_Deep ≠ 1",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if zero_count > 0:
                details_lines.append(f"  - Equals 0: {zero_count} products")
            if len(other_values) > 0:
                other_count = len(squeeze_deep[squeeze_deep.isin(other_values)])
                details_lines.append(f"  - Other values: {other_count} products ({', '.join(map(str, other_values[:5]))}...)")
            
            # Show samples
            details_lines.append("\nSample products with Squeeze_Deep ≠ 1:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                val = row.get('Squeeze_Deep', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Squeeze_Deep = {val} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Squeeze_Deep ≠ 1 (must be exactly 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_squeeze_wide_must_equal_one(self) -> ValidationResult:
        """Check if Squeeze_Wide equals exactly 1.
        
        Business Rule:
        - Squeeze_Wide MUST equal 1
        - Null, 0, or any other value → FAIL (strict)
        """
        check_name = "Squeeze_Wide Must Equal 1"
        
        if 'Squeeze_Width' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Squeeze_Width column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        squeeze_wide = pd.to_numeric(self.df['Squeeze_Width'], errors='coerce')
        
        # Find rows where Squeeze_Wide != 1
        error_mask = squeeze_wide != 1
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Squeeze_Wide = 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize the different invalid values
            null_count = squeeze_wide.isna().sum()
            zero_count = (squeeze_wide == 0).sum()
            other_values = squeeze_wide[~squeeze_wide.isin([0, 1]) & squeeze_wide.notna()].unique()
            
            details_lines = [
                f"Found {error_count} products where Squeeze_Wide ≠ 1",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if zero_count > 0:
                details_lines.append(f"  - Equals 0: {zero_count} products")
            if len(other_values) > 0:
                other_count = len(squeeze_wide[squeeze_wide.isin(other_values)])
                details_lines.append(f"  - Other values: {other_count} products ({', '.join(map(str, other_values[:5]))}...)")
            
            # Show samples
            details_lines.append("\nSample products with Squeeze_Wide ≠ 1:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                val = row.get('Squeeze_Width', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Squeeze_Wide = {val} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Squeeze_Wide ≠ 1 (must be exactly 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_expand_deep_must_equal_one(self) -> ValidationResult:
        """Check if Expand_Deep equals exactly 1.
        
        Business Rule:
        - Expand_Deep MUST equal 1
        - Null, 0, or any other value → FAIL (strict)
        """
        check_name = "Expand_Deep Must Equal 1"
        
        if 'Expand_Deep' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Expand_Deep column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        expand_deep = pd.to_numeric(self.df['Expand_Deep'], errors='coerce')
        
        # Find rows where Expand_Deep != 1
        error_mask = expand_deep != 1
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Expand_Deep = 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize the different invalid values
            null_count = expand_deep.isna().sum()
            zero_count = (expand_deep == 0).sum()
            other_values = expand_deep[~expand_deep.isin([0, 1]) & expand_deep.notna()].unique()
            
            details_lines = [
                f"Found {error_count} products where Expand_Deep ≠ 1",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if zero_count > 0:
                details_lines.append(f"  - Equals 0: {zero_count} products")
            if len(other_values) > 0:
                other_count = len(expand_deep[expand_deep.isin(other_values)])
                details_lines.append(f"  - Other values: {other_count} products ({', '.join(map(str, other_values[:5]))}...)")
            
            # Show samples
            details_lines.append("\nSample products with Expand_Deep ≠ 1:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                val = row.get('Expand_Deep', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Expand_Deep = {val} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Expand_Deep ≠ 1 (must be exactly 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_front_overhang_inches_less_than_one(self) -> ValidationResult:
        """Check if Front_Overhang_Inches is less than 1.
        
        Business Rule:
        - Front_Overhang_Inches MUST be < 1
        - FAIL if: Front_Overhang_Inches >= 1 OR Front_Overhang_Inches is null
        - PASS if: Front_Overhang_Inches < 1 (including 0 and negative values)
        """
        check_name = "Front_Overhang_Inches Less Than 1"
        
        # Check if column exists (note: might be mapped from a Field_N)
        # Assuming the column doesn't exist in our current mapping, check common variants
        if 'Front_Overhang_Inches' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Front_Overhang_Inches column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset (may need to be mapped from Field_N)"
            )
            self.results.append(result)
            return result
        
        # Convert to numeric
        front_overhang = pd.to_numeric(self.df['Front_Overhang_Inches'], errors='coerce')
        
        # Find rows where Front_Overhang_Inches >= 1 OR is null
        null_mask = front_overhang.isna()
        gte_one_mask = front_overhang >= 1
        error_mask = null_mask | gte_one_mask
        
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Front_Overhang_Inches < 1",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement"
            )
        else:
            # Categorize errors
            null_count = null_mask.sum()
            gte_one_count = gte_one_mask.sum()
            
            details_lines = [
                f"Found {error_count} products where Front_Overhang_Inches >= 1 or is null",
                "",
                "Error breakdown:"
            ]
            
            if null_count > 0:
                details_lines.append(f"  - Null/Empty: {null_count} products")
            if gte_one_count > 0:
                details_lines.append(f"  - Greater than or equal to 1: {gte_one_count} products")
                # Show value distribution for >= 1
                values_gte_one = front_overhang[gte_one_mask].unique()[:5]
                details_lines.append(f"    Sample values: {', '.join(map(str, values_gte_one))}")
            
            # Show samples
            details_lines.append("\nSample products with Front_Overhang_Inches >= 1 or null:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                val = row.get('Front_Overhang_Inches', 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                issue = "null" if pd.isna(val) else f"= {val} (>= 1)"
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Front_Overhang_Inches {issue} | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products where Front_Overhang_Inches >= 1 or is null (must be < 1)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_peg_id_required_when_peg_holes_exist(self) -> ValidationResult:
        """Check if Peg_ID exists when peg hole positions are defined.
        
        Business Rule:
        - If ANY of (Peg_Hole_X, Peg_Hole_Y, Peg_Hole_2X, Peg_Hole_2Y) is not null AND > 0
        - Then Peg_ID must NOT be null
        - FAIL if peg holes exist but Peg_ID is null
        """
        check_name = "Peg_ID Required When Peg Holes Exist"
        
        # Check if required columns exist
        required_cols = ['Peg_Hole_X', 'Peg_Hole_Y', 'Peg_Hole_2X', 'Peg_Hole_2Y', 'Peg_ID']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        
        if missing_cols:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message=f"Required columns not found: {', '.join(missing_cols)}",
                error_count=0,
                pass_count=len(self.df),
                details="Cannot perform check without required columns"
            )
            self.results.append(result)
            return result
        
        # Convert peg hole columns to numeric
        peg_hole_x = pd.to_numeric(self.df['Peg_Hole_X'], errors='coerce')
        peg_hole_y = pd.to_numeric(self.df['Peg_Hole_Y'], errors='coerce')
        peg_hole_2x = pd.to_numeric(self.df['Peg_Hole_2X'], errors='coerce')
        peg_hole_2y = pd.to_numeric(self.df['Peg_Hole_2Y'], errors='coerce')
        
        # Check if ANY peg hole value is not null AND > 0
        has_peg_hole_x = (peg_hole_x.notna()) & (peg_hole_x > 0)
        has_peg_hole_y = (peg_hole_y.notna()) & (peg_hole_y > 0)
        has_peg_hole_2x = (peg_hole_2x.notna()) & (peg_hole_2x > 0)
        has_peg_hole_2y = (peg_hole_2y.notna()) & (peg_hole_2y > 0)
        
        # ANY of the peg holes exist (OR condition)
        has_any_peg_hole = has_peg_hole_x | has_peg_hole_y | has_peg_hole_2x | has_peg_hole_2y
        
        # Check if Peg_ID is null
        peg_id_is_null = self.df['Peg_ID'].isna() | (self.df['Peg_ID'].astype(str).str.strip() == '')
        
        # FAIL: Has peg holes but Peg_ID is null
        error_mask = has_any_peg_hole & peg_id_is_null
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        # Count products that were checked
        products_with_peg_holes = has_any_peg_hole.sum()
        products_without_peg_holes = (~has_any_peg_hole).sum()
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All products with peg holes have Peg_ID defined",
                error_count=0,
                pass_count=len(self.df),
                details=f"Products with peg holes: {products_with_peg_holes}, all have Peg_ID\nProducts without peg holes: {products_without_peg_holes}"
            )
        else:
            details_lines = [
                f"Found {error_count} products with peg holes but missing Peg_ID",
                f"Total products with peg holes: {products_with_peg_holes}",
                f"Products without peg holes: {products_without_peg_holes}",
                ""
            ]
            
            # Show samples
            details_lines.append("Sample products with peg holes but missing Peg_ID:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                # Get values and convert to numeric for comparison
                peg_x_val = pd.to_numeric(row.get('Peg_Hole_X'), errors='coerce')
                peg_y_val = pd.to_numeric(row.get('Peg_Hole_Y'), errors='coerce')
                peg_2x_val = pd.to_numeric(row.get('Peg_Hole_2X'), errors='coerce')
                peg_2y_val = pd.to_numeric(row.get('Peg_Hole_2Y'), errors='coerce')
                peg_id = row.get('Peg_ID', 'null')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                
                # Show which peg holes exist
                peg_info = []
                if pd.notna(peg_x_val) and peg_x_val > 0:
                    peg_info.append(f"X={peg_x_val}")
                if pd.notna(peg_y_val) and peg_y_val > 0:
                    peg_info.append(f"Y={peg_y_val}")
                if pd.notna(peg_2x_val) and peg_2x_val > 0:
                    peg_info.append(f"2X={peg_2x_val}")
                if pd.notna(peg_2y_val) and peg_2y_val > 0:
                    peg_info.append(f"2Y={peg_2y_val}")
                
                peg_info_str = ", ".join(peg_info)
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Peg holes ({peg_info_str}), Peg_ID=null"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products with peg holes but missing Peg_ID",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_alt_upc_must_be_null(self) -> ValidationResult:
        """Check if Has_Alt_UPC is null.
        
        Business Rule:
        - Has_Alt_UPC MUST be null
        - Any non-null value → FAIL
        """
        check_name = "Has_Alt_UPC Must Be Null"
        
        # Check for Has_Alt_UPC column (mapped from Field_130)
        if 'Has_Alt_UPC' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Has_Alt_UPC column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset (should be mapped from Field_130)"
            )
            self.results.append(result)
            return result
        
        col_name = 'Has_Alt_UPC'
        
        # Find rows where Has_Alt_UPC is NOT null (including non-empty strings)
        has_alt_upc_series = self.df[col_name].astype(str)
        error_mask = self.df[col_name].notna() & (has_alt_upc_series.str.strip() != '') & (has_alt_upc_series.str.lower() != 'nan')
        error_rows = self.df[error_mask]
        error_count = len(error_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {len(self.df)} products have Has_Alt_UPC = null",
                error_count=0,
                pass_count=len(self.df),
                details="All products meet the requirement (Has_Alt_UPC is null/empty)"
            )
        else:
            # Get unique non-null values
            unique_values = self.df[col_name][error_mask].unique()[:10]
            
            details_lines = [
                f"Found {error_count} products where Has_Alt_UPC is NOT null",
                f"Has_Alt_UPC should always be null/empty",
                "",
                f"Sample Has_Alt_UPC values found: {', '.join(map(str, unique_values))}",
                ""
            ]
            
            # Show samples
            details_lines.append("Sample products with non-null Has_Alt_UPC:")
            sample = error_rows.head(10)
            for idx, row in sample.iterrows():
                has_alt_upc_val = row.get(col_name, 'N/A')
                upc = row.get('UPC', 'N/A')
                item_num = row.get('Item_Number', 'N/A')
                desc = row.get('Item_1_Description', 'N/A')[:30]
                
                details_lines.append(
                    f"  - UPC {upc} (Item {item_num}): Has_Alt_UPC = '{has_alt_upc_val}' | {desc}"
                )
            
            if len(error_rows) > 10:
                details_lines.append(f"  ... and {len(error_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Found {error_count} products with non-null Has_Alt_UPC (must be null)",
                error_count=error_count,
                pass_count=len(self.df) - error_count,
                details="\n".join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_has_alt_upc_against_excel_reference(self) -> ValidationResult:
        """Validate Has_Alt_UPC against Excel reference file.
        
        Business Rule:
        - If ANY product has Has_Alt_UPC populated (not null), then the Excel reference
          Has_Alt_UPC MUST be "no" for this check to pass.
        - Excel file has one row per Department/Category with Has_Alt_UPC value
        - Product table doesn't have Dept/Cat, so we check if Excel says "no" for the dept/cat
        
        Returns:
            ValidationResult with PASS/FAIL status
        """
        check_name = "Has_Alt_UPC Match Against Reference File"
        
        if not self.excel_reference_bytes:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Excel reference file not provided - skipping validation",
                error_count=0,
                pass_count=0,
                details="Upload an Excel reference file to enable this validation"
            )
            self.results.append(result)
            return result
        
        try:
            # Read Excel file from bytes
            excel_df = pd.read_excel(io.BytesIO(self.excel_reference_bytes), sheet_name='handoff')
            
            # Check if required columns exist in Excel
            if 'Has_Alt_UPC' not in excel_df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message="Has_Alt_UPC column not found in Excel reference file",
                    error_count=1,
                    details=f"Excel columns: {list(excel_df.columns)}"
                )
                self.results.append(result)
                return result
            
            # Check if Has_Alt_UPC column exists in product data
            if 'Has_Alt_UPC' not in self.df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="WARNING",
                    message="Has_Alt_UPC column not found in product data",
                    error_count=0,
                    details="Cannot validate - Has_Alt_UPC column missing from product table"
                )
                self.results.append(result)
                return result
            
            # Count products with Has_Alt_UPC populated
            products_with_alt_upc = self.df[self.df['Has_Alt_UPC'].notna() & (self.df['Has_Alt_UPC'].astype(str).str.strip() != '')]
            total_products_with_alt_upc = len(products_with_alt_upc)
            
            # If no products have Has_Alt_UPC, check passes
            if total_products_with_alt_upc == 0:
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message="No products have Has_Alt_UPC populated (all null/empty)",
                    error_count=0,
                    pass_count=len(self.df),
                    details="All products have Has_Alt_UPC = null, so this check passes"
                )
                self.results.append(result)
                return result
            
            # Products DO have Has_Alt_UPC - check if Excel says "no" for ALL dept/cat
            excel_has_alt_upc_values = excel_df['Has_Alt_UPC'].astype(str).str.strip().str.lower().unique()
            
            # Check if ALL Excel Has_Alt_UPC values are "no"
            non_no_values = [v for v in excel_has_alt_upc_values if v != 'no']
            
            if non_no_values:
                # Excel has some value other than "no" - FAIL
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message=f"{total_products_with_alt_upc} products have Has_Alt_UPC populated, but Excel Has_Alt_UPC is NOT 'no' (found: {', '.join(non_no_values)})",
                    error_count=total_products_with_alt_upc,
                    pass_count=0,
                    details=f"Product Has_Alt_UPC must be null when Excel Has_Alt_UPC != 'no'. Found Excel values: {', '.join(excel_has_alt_upc_values)}"
                )
            else:
                # Excel says "no" for all dept/cat - PASS
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message=f"All {total_products_with_alt_upc} products with Has_Alt_UPC are valid (Excel Has_Alt_UPC = 'no')",
                    error_count=0,
                    pass_count=total_products_with_alt_upc,
                    details=f"Validated {total_products_with_alt_upc} products with Has_Alt_UPC against Excel reference"
                )
            
            self.results.append(result)
            return result
        
        except Exception as e:
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"Error reading Excel reference file: {str(e)}",
                error_count=1,
                details="Check that the Excel file format is correct and contains a 'handoff' sheet"
            )
            self.results.append(result)
            return result
    
    def get_summary(self) -> dict:
        """Get summary of all validation results."""
        total_checks = len(self.results)
        passed = sum(1 for r in self.results if r.status == 'PASS')
        failed = sum(1 for r in self.results if r.status == 'FAIL')
        warnings = sum(1 for r in self.results if r.status == 'WARNING')
        total_errors = sum(r.error_count for r in self.results)
        
        return {
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'total_errors': total_errors,
            'overall_status': 'PASS' if failed == 0 else 'FAIL'
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert validation results to a DataFrame for reporting."""
        if not self.results:
            return pd.DataFrame()
        
        data = [
            {
                'Check Name': r.check_name,
                'Status': r.status,
                'Pass Count': r.pass_count,
                'Error Count': r.error_count,
                'Message': r.message,
                'Details': r.details
            }
            for r in self.results
        ]
        
        return pd.DataFrame(data)


def validate_product_data(df: pd.DataFrame) -> Tuple[List[ValidationResult], dict]:
    """Convenience function to validate product data.
    
    Args:
        df: DataFrame with product data
    
    Returns:
        Tuple of (validation_results, summary_dict)
    """
    validator = DataValidator(df)
    results = validator.run_all_checks()
    summary = validator.get_summary()
    
    return results, summary