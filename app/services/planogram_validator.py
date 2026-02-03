"""Data validator for Planogram data quality checks."""
from __future__ import annotations

import pandas as pd
import io
from dataclasses import dataclass
from typing import List, Optional


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
    """Validates Planogram data with multiple quality checks."""
    
    def __init__(self, df: pd.DataFrame, excel_reference_bytes: Optional[bytes] = None):
        self.df = df
        self.excel_reference_bytes = excel_reference_bytes
        self.results: List[ValidationResult] = []
    
    def run_all_checks(self) -> List[ValidationResult]:
        """Run all validation checks and return results."""
        self.results = []
        
        # Run each check
        self.check_print_fields_populated()
        self.check_footage_equals_width_feet()
        self.check_drawing_id_not_null()
        self.check_effective_date_not_null()
        self.check_offset_not_null()
        self.check_notch_bar_width_not_null()
        self.check_department_not_null()
        self.check_category_not_null()
        self.check_modular_description_alphanumeric()
        
        # Run department and category validation against Excel reference (if provided)
        if self.excel_reference_bytes:
            self.check_department_against_excel_reference()
            self.check_category_against_excel_reference()
        
        return self.results
    
    def get_summary(self) -> dict:
        """Get summary of validation results."""
        passed = sum(1 for r in self.results if r.status == 'PASS')
        failed = sum(1 for r in self.results if r.status == 'FAIL')
        warnings = sum(1 for r in self.results if r.status == 'WARNING')
        
        return {
            'total_checks': len(self.results),
            'passed': passed,
            'failed': failed,
            'warnings': warnings
        }
    
    def check_print_fields_populated(self) -> ValidationResult:
        """Check if ALL Print fields (Print_1, Print_2, Print_3, Print_4) are populated.
        
        Requirement: ALL 4 Print fields must have explicit values (not empty/null).
        If ANY of the 4 fields is empty in a row, flag as FAIL.
        
        Returns:
            ValidationResult with status PASS/FAIL and details
        """
        check_name = "Print Fields Populated (ALL 4 Required)"
        
        print_fields = ['Print_1', 'Print_2', 'Print_3', 'Print_4']
        
        # Check if all Print columns exist
        missing_columns = [col for col in print_fields if col not in self.df.columns]
        if missing_columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message=f"Missing columns: {', '.join(missing_columns)}",
                error_count=0,
                pass_count=0,
                details="Cannot validate - columns do not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Check each row for empty Print fields
        failed_rows = []
        
        for idx, row in self.df.iterrows():
            empty_fields = []
            for field in print_fields:
                value = row[field]
                # Check if empty (None, empty string, or just whitespace)
                if pd.isna(value) or str(value).strip() == '':
                    empty_fields.append(field)
            
            if empty_fields:
                # This row has at least one empty Print field - FAIL
                failed_rows.append({
                    'row': idx + 2,  # +2 because Excel is 1-indexed and has header
                    'empty_fields': ', '.join(empty_fields),
                    'table_name': row.get('Table_Name', 'N/A')
                })
        
        # Build result
        total_rows = len(self.df)
        pass_count = total_rows - len(failed_rows)
        error_count = len(failed_rows)
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {total_rows} records have all 4 Print fields populated",
                error_count=0,
                pass_count=total_rows,
                details=f"Checked: Print_1, Print_2, Print_3, Print_4"
            )
        else:
            # Build details message
            details_lines = [f"Total records with missing Print fields: {error_count}/{total_rows}"]
            details_lines.append("\nFailed Records:")
            
            # Show first 10 failures
            for fail in failed_rows[:10]:
                details_lines.append(
                    f"  Row {fail['row']} ({fail['table_name']}): Missing {fail['empty_fields']}"
                )
            
            if len(failed_rows) > 10:
                details_lines.append(f"  ... and {len(failed_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"{error_count} of {total_rows} records missing Print field values",
                error_count=error_count,
                pass_count=pass_count,
                details='\n'.join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_department_against_excel_reference(self) -> ValidationResult:
        """Validate that all Planogram Department values exist in Excel reference file.
        
        Requirement: ALL planogram departments must exist in the Excel reference file.
        If any department is missing from Excel, the check fails.
        
        Returns:
            ValidationResult with PASS/FAIL status
        """
        check_name = "Department Match Against Reference File"
        
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
            
            # Check if Department column exists in Excel
            if 'Department' not in excel_df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message="Department column not found in Excel reference file",
                    error_count=1,
                    details=f"Excel columns: {list(excel_df.columns)}"
                )
                self.results.append(result)
                return result
            
            # Check if Department column exists in planogram data
            if 'Department' not in self.df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="WARNING",
                    message="Department column not found in planogram data",
                    error_count=0,
                    details="Cannot validate - Department column missing from planogram"
                )
                self.results.append(result)
                return result
            
            # Get valid departments from Excel (convert to strings and strip leading zeros)
            valid_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in excel_df['Department'].astype(str).unique()
            )
            
            # Get unique departments from planogram (strip leading zeros)
            planogram_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in self.df['Department'].astype(str).unique()
            )
            
            # Check if all planogram departments exist in Excel
            missing_departments = planogram_departments - valid_departments
            
            total_planogram_depts = len(planogram_departments)
            
            if missing_departments:
                error_count = len(missing_departments)
                pass_count = total_planogram_depts - error_count
                
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message=f"Planogram contains {error_count} department(s) not in reference file: {', '.join(sorted(missing_departments))}",
                    error_count=error_count,
                    pass_count=pass_count,
                    details=f"Valid departments in Excel: {', '.join(sorted(valid_departments))}"
                )
            else:
                # All departments match!
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message=f"All {total_planogram_depts} planogram department(s) match reference file: {', '.join(sorted(planogram_departments))}",
                    error_count=0,
                    pass_count=total_planogram_depts,
                    details=f"Validated against {len(valid_departments)} reference department(s) from Excel"
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
    
    def check_category_against_excel_reference(self) -> ValidationResult:
        """Validate that all Planogram Category values exist in Excel reference file.
        
        Requirement: ALL planogram categories must exist in the Excel reference file.
        If any category is missing from Excel, the check fails.
        
        Returns:
            ValidationResult with PASS/FAIL status
        """
        check_name = "Category Match Against Reference File"
        
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
            
            # Check if Category column exists in Excel
            if 'Category' not in excel_df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message="Category column not found in Excel reference file",
                    error_count=1,
                    details=f"Excel columns: {list(excel_df.columns)}"
                )
                self.results.append(result)
                return result
            
            # Check if Category column exists in planogram data
            if 'Category' not in self.df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="WARNING",
                    message="Category column not found in planogram data",
                    error_count=0,
                    details="Cannot validate - Category column missing from planogram"
                )
                self.results.append(result)
                return result
            
            # Get valid categories from Excel (convert to strings and strip leading zeros)
            valid_categories = set(
                str(cat).lstrip('0') or '0' 
                for cat in excel_df['Category'].astype(str).unique()
            )
            
            # Get unique categories from planogram (strip leading zeros)
            planogram_categories = set(
                str(cat).lstrip('0') or '0' 
                for cat in self.df['Category'].astype(str).unique()
            )
            
            # Check if all planogram categories exist in Excel
            missing_categories = planogram_categories - valid_categories
            
            total_planogram_cats = len(planogram_categories)
            
            if missing_categories:
                error_count = len(missing_categories)
                pass_count = total_planogram_cats - error_count
                
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message=f"Planogram contains {error_count} category(ies) not in reference file: {', '.join(sorted(missing_categories))}",
                    error_count=error_count,
                    pass_count=pass_count,
                    details=f"Valid categories in Excel: {', '.join(sorted(valid_categories))}"
                )
            else:
                # All categories match!
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message=f"All {total_planogram_cats} planogram category(ies) match reference file: {', '.join(sorted(planogram_categories))}",
                    error_count=0,
                    pass_count=total_planogram_cats,
                    details=f"Validated against {len(valid_categories)} reference category(ies) from Excel"
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
    
    def check_footage_equals_width_feet(self) -> ValidationResult:
        """Check if Footage equals Width_Feet.
        
        Footage is a string (e.g., '028') that should equal Width_Feet when converted to float.
        Example: Footage='028' → 28.0, Width_Feet='28.0' → 28.0 (PASS)
        """
        check_name = "Footage Equals Width_Feet"
        
        if 'Footage' not in self.df.columns or 'Width_Feet' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Missing required columns (Footage or Width_Feet)",
                error_count=0,
                pass_count=0,
                details="Cannot validate - columns do not exist"
            )
            self.results.append(result)
            return result
        
        failed_rows = []
        
        for idx, row in self.df.iterrows():
            footage_val = row['Footage']
            width_feet_val = row['Width_Feet']
            
            # Skip if either is null/empty
            if pd.isna(footage_val) or pd.isna(width_feet_val):
                failed_rows.append({
                    'row': idx + 2,
                    'footage': str(footage_val),
                    'width_feet': str(width_feet_val),
                    'reason': 'One or both values are null'
                })
                continue
            
            try:
                # Convert to float (handles leading zeros)
                footage_float = float(str(footage_val).strip())
                width_feet_float = float(str(width_feet_val).strip())
                
                # Compare with small tolerance for floating point
                if abs(footage_float - width_feet_float) > 0.01:
                    failed_rows.append({
                        'row': idx + 2,
                        'footage': footage_float,
                        'width_feet': width_feet_float,
                        'reason': f'{footage_float} != {width_feet_float}'
                    })
            except (ValueError, TypeError):
                failed_rows.append({
                    'row': idx + 2,
                    'footage': str(footage_val),
                    'width_feet': str(width_feet_val),
                    'reason': 'Cannot convert to number'
                })
        
        total_rows = len(self.df)
        error_count = len(failed_rows)
        pass_count = total_rows - error_count
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {total_rows} records have matching Footage and Width_Feet",
                error_count=0,
                pass_count=total_rows
            )
        else:
            details_lines = [f"Total mismatches: {error_count}/{total_rows}"]
            details_lines.append("\nFailed Records:")
            for fail in failed_rows[:10]:
                details_lines.append(
                    f"  Row {fail['row']}: Footage={fail['footage']}, Width_Feet={fail['width_feet']} ({fail['reason']})"
                )
            if len(failed_rows) > 10:
                details_lines.append(f"  ... and {len(failed_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"{error_count} of {total_rows} records have mismatched Footage/Width_Feet",
                error_count=error_count,
                pass_count=pass_count,
                details='\n'.join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_department_against_excel_reference(self) -> ValidationResult:
        """Validate that all Planogram Department values exist in Excel reference file.
        
        Requirement: ALL planogram departments must exist in the Excel reference file.
        If any department is missing from Excel, the check fails.
        
        Returns:
            ValidationResult with PASS/FAIL status
        """
        check_name = "Department Match Against Reference File"
        
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
            
            # Check if Department column exists in Excel
            if 'Department' not in excel_df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message="Department column not found in Excel reference file",
                    error_count=1,
                    details=f"Excel columns: {list(excel_df.columns)}"
                )
                self.results.append(result)
                return result
            
            # Check if Department column exists in planogram data
            if 'Department' not in self.df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="WARNING",
                    message="Department column not found in planogram data",
                    error_count=0,
                    details="Cannot validate - Department column missing from planogram"
                )
                self.results.append(result)
                return result
            
            # Get valid departments from Excel (convert to strings and strip leading zeros)
            valid_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in excel_df['Department'].astype(str).unique()
            )
            
            # Get unique departments from planogram (strip leading zeros)
            planogram_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in self.df['Department'].astype(str).unique()
            )
            
            # Check if all planogram departments exist in Excel
            missing_departments = planogram_departments - valid_departments
            
            total_planogram_depts = len(planogram_departments)
            
            if missing_departments:
                error_count = len(missing_departments)
                pass_count = total_planogram_depts - error_count
                
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message=f"Planogram contains {error_count} department(s) not in reference file: {', '.join(sorted(missing_departments))}",
                    error_count=error_count,
                    pass_count=pass_count,
                    details=f"Valid departments in Excel: {', '.join(sorted(valid_departments))}"
                )
            else:
                # All departments match!
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message=f"All {total_planogram_depts} planogram department(s) match reference file: {', '.join(sorted(planogram_departments))}",
                    error_count=0,
                    pass_count=total_planogram_depts,
                    details=f"Validated against {len(valid_departments)} reference department(s) from Excel"
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
    
    def check_drawing_id_not_null(self) -> ValidationResult:
        """Check if Drawing_ID is not null."""
        return self._check_field_not_null('Drawing_ID')
    
    def check_effective_date_not_null(self) -> ValidationResult:
        """Check if Effective_Date is not null."""
        return self._check_field_not_null('Effective_Date')
    
    def check_offset_not_null(self) -> ValidationResult:
        """Check if Offset is not null."""
        return self._check_field_not_null('Offset')
    
    def check_notch_bar_width_not_null(self) -> ValidationResult:
        """Check if Notch_Bar_Width is not null."""
        return self._check_field_not_null('Notch_Bar_Width')
    
    def check_department_not_null(self) -> ValidationResult:
        """Check if Department is not null."""
        return self._check_field_not_null('Department')
    
    def check_category_not_null(self) -> ValidationResult:
        """Check if Category is not null."""
        return self._check_field_not_null('Category')
    
    def _check_field_not_null(self, field_name: str) -> ValidationResult:
        """Generic method to check if a field is not null/empty.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            ValidationResult
        """
        check_name = f"{field_name} Not Null"
        
        if field_name not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message=f"{field_name} column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        # Find null/empty rows
        null_mask = self.df[field_name].isna() | (self.df[field_name].astype(str).str.strip() == '')
        null_rows = self.df[null_mask]
        
        total_rows = len(self.df)
        error_count = len(null_rows)
        pass_count = total_rows - error_count
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {total_rows} records have {field_name} populated",
                error_count=0,
                pass_count=total_rows
            )
        else:
            # Get row numbers
            failed_row_numbers = [idx + 2 for idx in null_rows.index][:10]
            
            details_lines = [f"Total null/empty {field_name}: {error_count}/{total_rows}"]
            details_lines.append(f"\nFailed Rows: {', '.join(map(str, failed_row_numbers))}")
            if error_count > 10:
                details_lines.append(f"... and {error_count - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"{error_count} of {total_rows} records have null/empty {field_name}",
                error_count=error_count,
                pass_count=pass_count,
                details='\n'.join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_department_against_excel_reference(self) -> ValidationResult:
        """Validate that all Planogram Department values exist in Excel reference file.
        
        Requirement: ALL planogram departments must exist in the Excel reference file.
        If any department is missing from Excel, the check fails.
        
        Returns:
            ValidationResult with PASS/FAIL status
        """
        check_name = "Department Match Against Reference File"
        
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
            
            # Check if Department column exists in Excel
            if 'Department' not in excel_df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message="Department column not found in Excel reference file",
                    error_count=1,
                    details=f"Excel columns: {list(excel_df.columns)}"
                )
                self.results.append(result)
                return result
            
            # Check if Department column exists in planogram data
            if 'Department' not in self.df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="WARNING",
                    message="Department column not found in planogram data",
                    error_count=0,
                    details="Cannot validate - Department column missing from planogram"
                )
                self.results.append(result)
                return result
            
            # Get valid departments from Excel (convert to strings and strip leading zeros)
            valid_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in excel_df['Department'].astype(str).unique()
            )
            
            # Get unique departments from planogram (strip leading zeros)
            planogram_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in self.df['Department'].astype(str).unique()
            )
            
            # Check if all planogram departments exist in Excel
            missing_departments = planogram_departments - valid_departments
            
            total_planogram_depts = len(planogram_departments)
            
            if missing_departments:
                error_count = len(missing_departments)
                pass_count = total_planogram_depts - error_count
                
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message=f"Planogram contains {error_count} department(s) not in reference file: {', '.join(sorted(missing_departments))}",
                    error_count=error_count,
                    pass_count=pass_count,
                    details=f"Valid departments in Excel: {', '.join(sorted(valid_departments))}"
                )
            else:
                # All departments match!
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message=f"All {total_planogram_depts} planogram department(s) match reference file: {', '.join(sorted(planogram_departments))}",
                    error_count=0,
                    pass_count=total_planogram_depts,
                    details=f"Validated against {len(valid_departments)} reference department(s) from Excel"
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
    
    def check_modular_description_alphanumeric(self) -> ValidationResult:
        """Check if Modular_Description contains only letters and numbers (no special characters).
        
        Allowed: A-Z, a-z, 0-9, spaces
        Not allowed: @, #, $, %, &, *, etc.
        """
        check_name = "Modular_Description Alphanumeric Only"
        
        if 'Modular_Description' not in self.df.columns:
            result = ValidationResult(
                check_name=check_name,
                status="WARNING",
                message="Modular_Description column not found",
                error_count=0,
                pass_count=0,
                details="Column does not exist in dataset"
            )
            self.results.append(result)
            return result
        
        import re
        failed_rows = []
        
        for idx, row in self.df.iterrows():
            value = row['Modular_Description']
            
            # Skip if null/empty
            if pd.isna(value) or str(value).strip() == '':
                continue
            
            value_str = str(value)
            
            # Check if contains only alphanumeric characters and spaces
            if not re.match(r'^[A-Za-z0-9\s]+$', value_str):
                # Find the special characters
                special_chars = re.findall(r'[^A-Za-z0-9\s]', value_str)
                failed_rows.append({
                    'row': idx + 2,
                    'value': value_str[:50],  # Truncate if long
                    'special_chars': ', '.join(set(special_chars))
                })
        
        total_rows = len(self.df)
        error_count = len(failed_rows)
        pass_count = total_rows - error_count
        
        if error_count == 0:
            result = ValidationResult(
                check_name=check_name,
                status="PASS",
                message=f"All {total_rows} records have alphanumeric Modular_Description",
                error_count=0,
                pass_count=total_rows
            )
        else:
            details_lines = [f"Total records with special characters: {error_count}/{total_rows}"]
            details_lines.append("\nFailed Records (showing first 10):")
            for fail in failed_rows[:10]:
                details_lines.append(
                    f"  Row {fail['row']}: '{fail['value']}...' (special chars: {fail['special_chars']})"
                )
            if len(failed_rows) > 10:
                details_lines.append(f"  ... and {len(failed_rows) - 10} more")
            
            result = ValidationResult(
                check_name=check_name,
                status="FAIL",
                message=f"{error_count} of {total_rows} records have special characters in Modular_Description",
                error_count=error_count,
                pass_count=pass_count,
                details='\n'.join(details_lines)
            )
        
        self.results.append(result)
        return result
    
    def check_department_against_excel_reference(self) -> ValidationResult:
        """Validate that all Planogram Department values exist in Excel reference file.
        
        Requirement: ALL planogram departments must exist in the Excel reference file.
        If any department is missing from Excel, the check fails.
        
        Returns:
            ValidationResult with PASS/FAIL status
        """
        check_name = "Department Match Against Reference File"
        
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
            
            # Check if Department column exists in Excel
            if 'Department' not in excel_df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message="Department column not found in Excel reference file",
                    error_count=1,
                    details=f"Excel columns: {list(excel_df.columns)}"
                )
                self.results.append(result)
                return result
            
            # Check if Department column exists in planogram data
            if 'Department' not in self.df.columns:
                result = ValidationResult(
                    check_name=check_name,
                    status="WARNING",
                    message="Department column not found in planogram data",
                    error_count=0,
                    details="Cannot validate - Department column missing from planogram"
                )
                self.results.append(result)
                return result
            
            # Get valid departments from Excel (convert to strings and strip leading zeros)
            valid_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in excel_df['Department'].astype(str).unique()
            )
            
            # Get unique departments from planogram (strip leading zeros)
            planogram_departments = set(
                str(dept).lstrip('0') or '0' 
                for dept in self.df['Department'].astype(str).unique()
            )
            
            # Check if all planogram departments exist in Excel
            missing_departments = planogram_departments - valid_departments
            
            total_planogram_depts = len(planogram_departments)
            
            if missing_departments:
                error_count = len(missing_departments)
                pass_count = total_planogram_depts - error_count
                
                result = ValidationResult(
                    check_name=check_name,
                    status="FAIL",
                    message=f"Planogram contains {error_count} department(s) not in reference file: {', '.join(sorted(missing_departments))}",
                    error_count=error_count,
                    pass_count=pass_count,
                    details=f"Valid departments in Excel: {', '.join(sorted(valid_departments))}"
                )
            else:
                # All departments match!
                result = ValidationResult(
                    check_name=check_name,
                    status="PASS",
                    message=f"All {total_planogram_depts} planogram department(s) match reference file: {', '.join(sorted(planogram_departments))}",
                    error_count=0,
                    pass_count=total_planogram_depts,
                    details=f"Validated against {len(valid_departments)} reference department(s) from Excel"
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
