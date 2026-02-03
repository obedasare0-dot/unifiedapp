# Phase 2 Testing Guide - Multi-Tab Excel

## ✅ Phase 2 Complete!

**What Changed:**
- Before: 3 separate Excel files (Product_Data.xlsx, Planogram_Data.xlsx, Validation_Report.xlsx)
- Now: 2 files in ZIP:
  - **PSA_Data.xlsx** (multi-tab workbook with Product + Planogram sheets)
  - **Validation_Report.xlsx** (combined 26 checks)

---

## 🚀 How to Test

### Step 1: Launch the App

**Option A: Double-click**
```
LAUNCH_APP.bat
```

**Option B: Command Line**
```bash
cd "C:\Users\O0A03ZR\OneDrive - Walmart Inc\PROJECT DOCS\FLOORPLANNING\BUILD_APP\UNIFIED_APP"
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Open Browser
Navigate to: **http://localhost:8000**

You should see:
- Title: "🗂️ PSA Unified Processor" with "MULTI-TABLE" badge
- Blue gradient background (Walmart colors)
- Upload form with file picker

### Step 3: Upload Test File
Use the test PSA file:
```
Example_2_Test.psa
```
(Already in the UNIFIED_APP folder)

### Step 4: Download ZIP
1. Click "Choose File" → Select Example_2_Test.psa
2. Click "Process & Download ZIP"
3. Wait for processing (you'll see spinner)
4. ZIP file downloads automatically: **PSA_Export.zip**

### Step 5: Extract and Verify

Extract **PSA_Export.zip** - you should get **2 files**:

#### File 1: PSA_Data.xlsx (Multi-Tab Workbook)

**Open it and check:**

✅ **Sheet 1: Product**
- 26 rows of data
- 46 columns with clean names:
  - UPC, Item_Number, Order_Type, Height_Inches, Width_Inches, etc.
- Blue header row (Walmart blue #0053E2)
- White text on headers

✅ **Sheet 2: Planogram**
- 1 row of data (Example 2 has 1 Planogram record)
- 22 columns with smart-mapped names:
  - Table_Name, Modular_Description, Width_Inches, Offset, Department, etc.
- Blue header row
- Yellow highlighting on columns H, I, J, K (smart-mapped fields)

#### File 2: Validation_Report.xlsx (Combined Checks)

**Open it and check 3 sheets:**

✅ **Summary Sheet**
- Total Checks Run: 26
- Breakdown:
  - Product checks: 17
  - Planogram checks: 9
- Passed: X
- Failed: Y
- Warnings: Z

✅ **Failed Checks Sheet**
- Shows only failed checks (if any)
- Prefixed with [Product] or [Planogram]
- Details with row numbers

✅ **All Checks Sheet**
- All 26 checks listed
- Color-coded:
  - Green = PASS
  - Red = FAIL
  - Yellow = WARNING
- Each check prefixed with table name:
  - [Product] Relay_ID Uniformity
  - [Product] UPC Length
  - ...
  - [Planogram] Print Fields Populated
  - [Planogram] Footage Equals Width_Feet
  - ...

---

## 🎯 What to Look For

### Multi-Tab Excel Works?
- [ ] PSA_Data.xlsx has 2 sheets (Product + Planogram)
- [ ] Both sheets have styled blue headers
- [ ] Planogram sheet has yellow highlights on columns H-K
- [ ] Data is correct and clean

### Combined Validation Works?
- [ ] Validation_Report.xlsx shows 26 total checks
- [ ] Checks are prefixed with [Product] or [Planogram]
- [ ] Summary shows correct breakdown (17 + 9 = 26)
- [ ] All Checks sheet shows both table's checks

### UI Updates?
- [ ] UI mentions "PSA_Data.xlsx" (not separate files)
- [ ] Success message shows multi-tab structure
- [ ] Footer shows "2 sheets" in description

---

## ⚠️ Common Issues

### Issue: "ModuleNotFoundError"
**Solution:** Dependencies already installed in your global Python (they worked for other apps)

### Issue: "Port already in use"
**Solution:** Stop other apps or change port in LAUNCH_APP.bat

### Issue: "Can't find app"
**Solution:** Make sure you're in the UNIFIED_APP folder when launching

---

## 🎉 Success Criteria

Phase 2 is successful if:
- ✅ ZIP downloads with 2 files (not 3)
- ✅ PSA_Data.xlsx has 2 sheets
- ✅ Product sheet has 26 rows, 46 columns
- ✅ Planogram sheet has 1 row, 22 columns
- ✅ Validation_Report.xlsx shows 26 combined checks
- ✅ All styling and colors are correct

---

## 📊 Expected Console Output

When you upload, the terminal should show:
```
================================================================================
PSA PROCESSOR: Starting multi-table extraction
================================================================================
[PRODUCT] Starting extraction...
[PRODUCT] Extracted 26 records
[PRODUCT] Created DataFrame with 274 columns
[PRODUCT] Cleaned to 46 columns
[PRODUCT] Running validation checks...
[PRODUCT] Validation complete: X passed, Y failed
[SUCCESS] Product: 26 rows, 46 columns
[PLANOGRAM] Starting extraction...
[PLANOGRAM] Extracted 1 records
[PLANOGRAM] Smart-mapped 1 rows with 22 fields each
[PLANOGRAM] Created DataFrame with columns: ...
[PLANOGRAM] Running validation checks...
[PLANOGRAM] Validation complete: X passed, Y failed
[SUCCESS] Planogram: 1 rows, 22 columns
================================================================================
PSA PROCESSOR: Extraction complete
================================================================================
[EXPORTER] Creating multi-tab Excel file...
[EXPORTER] Added Product sheet (26 rows, 46 columns)
[EXPORTER] Added Planogram sheet (1 rows, 22 columns)
[EXPORTER] Created PSA_Data.xlsx with 2 sheets
[EXPORTER] Created Validation_Report.xlsx with 26 total checks
[EXPORTER] Generated ZIP with 2 files: PSA_Data.xlsx + Validation_Report.xlsx
```

---

**Ready to test!** 🐶🎾
