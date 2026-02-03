# PSA UNIFIED APP - Single UI for Multi-Table Processing

**Created:** 2026-01-28  
**Status:** 🚧 IN DEVELOPMENT - Phase 1  
**Goal:** Combine Product + Planogram apps into a single unified application

---

## 📦 **Project Structure**

```
UNIFIED_APP/
├── PRODUCT_BACKUP/          # ✅ Original Product app (Port 8000)
├── PLANOGRAM_BACKUP/        # ✅ Original Planogram app (Port 8001)
└── (Phase 1+)               # 🚧 New unified app files will go here
```

---

## 🎯 **Project Vision**

### **User Workflow:**
1. **Upload:** ONE .psa file via web UI
2. **Process:** Extract Product + Planogram tables automatically
3. **Choose:**
   - 📥 **Download ZIP** → Get Excel files
   - 📊 **View Report** → See validation in browser

### **Output: ZIP File (2 Excel files)**

**File 1: PSA_Data.xlsx** (Multi-tab workbook)
```
📊 PSA_Data.xlsx
├── Sheet 1: Product        (26 rows, 46 remapped columns)
├── Sheet 2: Planogram      (X rows, 22 smart-mapped columns)
└── (Future: Performance, Fixture, Position, Segment, Project)
```

**File 2: Validation_Report.xlsx** (Combined validation)
```
📋 Validation_Report.xlsx
├── Summary Sheet           (Total: 26 checks from both tables)
│   - Product: 17 checks
│   - Planogram: 9 checks
├── Failed Checks Sheet     (All failures across all tables)
└── All Checks Sheet        (Complete list with pass/fail status)
```

### **Web Report View (Interactive)**
Clicking "View Report" shows:
- ✅ Summary dashboard (Green/Red/Yellow cards)
- ✅ Expandable sections per table
- ✅ Failed row details with highlighting
- ✅ Download ZIP button still available

---

## 📋 **Development Phases**

### ✅ **Phase 0: Backup (COMPLETE)**
- [x] Copy PRODUCT app → PRODUCT_BACKUP
- [x] Copy PLANOGRAM app → PLANOGRAM_BACKUP
- [x] Original apps remain untouched

### ✅ **Phase 1: Merge Apps (COMPLETE)**
**Status:** DONE

**Tasks:**
1. Create unified app structure
   ```
   app/
   ├── main.py                 # Single FastAPI app
   ├── services/
   │   ├── psa_processor.py    # Process PSA → extract all tables
   │   ├── product_service.py  # Product extraction + validation
   │   ├── planogram_service.py# Planogram extraction + validation
   │   ├── excel_builder.py    # Build multi-tab Excel
   │   └── validation_merger.py# Merge validation results
   └── web/
       └── templates.py        # Unified UI
   ```

2. Combine validation logic
   - Merge Product validator (17 checks)
   - Merge Planogram validator (9 checks)
   - Create unified validation report (26 checks)

3. Test that merged app works
   - Upload PSA → Extract both tables
   - Verify all 26 validation checks run
   - Download ZIP with both Excel files

**Outcome:**
- ✅ Single app on Port 8000
- ✅ Upload PSA → Process both tables
- ✅ Both tables extracted and validated
- ✅ Combined validation report (26 checks)

---

### ✅ **Phase 2: Multi-Tab Excel (COMPLETE)**
**Status:** DONE

**Tasks:**
- [x] Create single Excel workbook with multiple sheets
  - Sheet 1: Product data (styled, 46 columns)
  - Sheet 2: Planogram data (styled, 22 columns)
- [x] Apply Walmart styling to all sheets
- [x] Update ZIP to contain:
  - PSA_Data.xlsx (multi-tab)
  - Validation_Report.xlsx (combined checks)

**Outcome:**
- ✅ Single PSA_Data.xlsx with 2 sheets
- ✅ Clean, styled headers on each sheet (Walmart blue)
- ✅ Yellow highlights on Planogram smart-mapped columns
- ✅ Validation_Report.xlsx shows combined 26 checks

---

### 🔮 **Phase 3: Web Report View**
**Status:** PLANNED

**Tasks:**
1. Create interactive HTML validation report
2. Add "View Report" button to UI
3. Display validation results in browser:
   - Summary cards (# passed, # failed, # warnings)
   - Collapsible sections per table
   - Failed row details with color coding
4. Keep "Download ZIP" button for Excel downloads

**Expected Outcome:**
- User can view validation results in browser
- Still can download Excel files
- Interactive, user-friendly report

---

## 🔧 **Technical Stack**

- **Backend:** FastAPI 0.115.6
- **Server:** Uvicorn 0.34.0
- **Data Processing:** Pandas 2.2.3
- **Excel:** OpenPyXL 3.1.5
- **Frontend:** HTMX (inline), Walmart color scheme
- **Port:** 8000 (unified app)

---

## 📚 **Current Apps (Backups)**

### **PRODUCT_BACKUP/**
- Extracts Product table (26 rows, 46 columns)
- 17 validation checks
- Returns ZIP with Product_Data.xlsx + Validation_Report.xlsx
- Port 8000 (original)

### **PLANOGRAM_BACKUP/**
- Extracts Planogram table (X rows, 22 smart-mapped columns)
- 9 validation checks
- Returns ZIP with Planogram_Data.xlsx + Validation_Report.xlsx
- Port 8001 (original)

---

## 🚀 **Getting Started (After Phase 1)**

```bash
# Navigate to unified app
cd UNIFIED_APP

# Install dependencies
pip install -r requirements.txt

# Launch app
python -m uvicorn app.main:app --reload --port 8000

# Open browser
http://localhost:8000
```

---

## 📝 **Notes**

- Original PRODUCT and PLANOGRAM apps are preserved in their respective folders
- UNIFIED_APP is the new workspace for development
- All changes happen in UNIFIED_APP, originals stay untouched
- Phase 1 & 2 complete - ready for testing!

---

## 🐶 **Development Log**

**2026-01-28:**
- ✅ Created UNIFIED_APP folder
- ✅ Backed up PRODUCT app → PRODUCT_BACKUP
- ✅ Backed up PLANOGRAM app → PLANOGRAM_BACKUP
- ✅ Phase 1: Merged apps into unified structure
- ✅ Phase 2: Created multi-tab Excel output

---

**Next:** Phase 3 - Web Report View (interactive HTML validation dashboard)
