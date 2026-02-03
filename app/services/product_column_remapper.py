from __future__ import annotations

import pandas as pd


def get_column_mapping() -> dict[str, str]:
    """
    Returns the mapping of Field_N columns to meaningful business names.
    
    This mapping is based on known PSA field positions and business requirements.
    """
    return {
        "Field_0": "Table_Name",
        "Field_2": "Item_Number",
        "Field_3": "Item_1_Description",
        "Field_12": "Manufacturer",
        "Field_17": "Y_Nesting",
        "Field_18": "Z_Nesting",
        "Field_19": "Peg_Holes",
        "Field_20": "Peg_Hole_X",
        "Field_21": "Peg_Hole_Y",
        "Field_23": "Peg_Hole_2X",
        "Field_24": "Peg_Hole_2Y",
        "Field_30": "Peg_ID",
        "Field_44": "Shape_ID",
        "Field_45": "Bitmap_ID_Override",
        "Field_46": "Tray_Width",
        "Field_47": "Tray_Height",
        "Field_48": "Tray_Depth",
        "Field_49": "Tray_Wide",
        "Field_50": "Tray_High",
        "Field_51": "Tray_Deep",
        "Field_52": "Tray_Total_#",
        "Field_54": "Case_Width",
        "Field_55": "Case_Height",
        "Field_56": "Case_Depth",
        "Field_60": "Case_Pack",
        "Field_62": "Display_Width",
        "Field_63": "Display_Height",
        "Field_64": "Display_Depth",
        "Field_70": "Alternate_Width",
        "Field_71": "Alternate_Height",
        "Field_72": "Alternate_Depth",
        "Field_118": "Order_Type",
        "Field_130": "Has_Alt_UPC",
        "Field_206": "Relay_ID",
        "Field_224": "Squeeze_Width",
        "Field_225": "Squeeze_High",
        "Field_226": "Squeeze_Deep",
        "Field_227": "Expand_Width",
        "Field_228": "Expand_High",
        "Field_229": "Expand_Deep",
        "Field_237": "Front_Overhang_Inches",
    }


def remap_and_clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remap Field_N columns to meaningful names and remove unmapped Field_N columns.
    
    Args:
        df: DataFrame with raw PSA data (contains Field_0, UPC, Field_2, Width_Inches, etc.)
    
    Returns:
        DataFrame with remapped columns and Field_N columns removed.
        Result contains only meaningful column names (46 columns).
    """
    # Apply column renaming
    mapping = get_column_mapping()
    df_remapped = df.rename(columns=mapping)
    
    # Keep only columns that don't start with 'Field_'
    # This removes all unmapped Field_N columns
    columns_to_keep = [col for col in df_remapped.columns if not col.startswith('Field_')]
    
    return df_remapped[columns_to_keep]
