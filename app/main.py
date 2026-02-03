"""Unified PSA Processing App - Product + Planogram tables."""
import io
import traceback

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse

# Track import errors
import_errors = []

try:
    from app.services.psa_processor import process_psa_file
except Exception as e:
    import_errors.append(f"psa_processor: {str(e)}")
    process_psa_file = None

try:
    from app.services.excel_exporter import create_excel_export
except Exception as e:
    import_errors.append(f"excel_exporter: {str(e)}")
    create_excel_export = None

try:
    from app.web.templates import get_home_page
except Exception as e:
    import_errors.append(f"templates: {str(e)}")
    get_home_page = None

try:
    from app.web.validation_dashboard import get_validation_dashboard
except Exception as e:
    import_errors.append(f"validation_dashboard: {str(e)}")
    get_validation_dashboard = None

app = FastAPI(title="PSA Unified Processor")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the upload page."""
    print("[DEBUG] Home page accessed")
    if get_home_page is None:
        return f"<h1>Error: templates module failed to import</h1><pre>{import_errors}</pre>"
    return get_home_page()

@app.get("/test")
async def test():
    """Test endpoint to verify server is working."""
    print("[DEBUG] Test endpoint accessed")
    return {"status": "working", "message": "Server is running!"}

@app.get("/routes")
async def list_routes():
    """List all registered routes for debugging."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else [],
                "name": route.name if hasattr(route, 'name') else None
            })
    return {"routes": routes, "total": len(routes)}

@app.get("/debug")
async def debug_info():
    """Show debug information about imports and configuration."""
    return {
        "import_errors": import_errors,
        "modules_loaded": {
            "psa_processor": process_psa_file is not None,
            "excel_exporter": create_excel_export is not None,
            "templates": get_home_page is not None,
            "validation_dashboard": get_validation_dashboard is not None
        },
        "status": "ok" if len(import_errors) == 0 else "errors"
    }


@app.post("/view-report", response_class=HTMLResponse)
async def view_report(
    psa_file: UploadFile = File(...),
    excel_file: UploadFile = File(None),
) -> str:
    """Upload PSA and view validation report in browser.
    
    Args:
        psa_file: PSA file (required)
        excel_file: Excel reference file for department validation (optional)
    """
    
    # Check for import errors
    if process_psa_file is None or get_validation_dashboard is None:
        return f"""<html><body>
        <h1>Import Error</h1>
        <p>Required modules failed to load:</p>
        <pre>{import_errors}</pre>
        </body></html>"""
    
    try:
        print("="*80)
        print("[API] POST /view-report endpoint called!")
        print("="*80)
        print(f"[API] Received PSA file: {psa_file.filename}")
        psa_bytes = await psa_file.read()
        print(f"[API] Read {len(psa_bytes)} bytes from uploaded PSA file")
        
        # Read Excel reference file if provided
        excel_bytes = None
        if excel_file and excel_file.filename:
            print(f"[API] Received Excel file: {excel_file.filename}")
            excel_bytes = await excel_file.read()
            print(f"[API] Read {len(excel_bytes)} bytes from Excel file")
        else:
            print("[API] No Excel reference file provided - department validation will be skipped")
        
        # Process PSA file (extract Product + Planogram)
        print(f"[API] Processing PSA file for web report...")
        data = process_psa_file(psa_bytes, excel_reference_bytes=excel_bytes)
        
        # Generate HTML dashboard
        print(f"[API] Generating validation dashboard HTML...")
        html = get_validation_dashboard(data)
        
        print(f"[API] Returning HTML dashboard ({len(html)} bytes)")
        return html
        
    except Exception as e:
        print("="*80)
        print(f"[ERROR] Failed to generate report: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        # Return detailed error HTML instead of raising
        error_html = f"""
        <!DOCTYPE html>
        <html><head><title>Error</title></head>
        <body style="font-family: monospace; padding: 20px; background: #1a1a1a; color: #ff6b6b;">
        <h1>❌ Error Processing PSA File</h1>
        <h2>Error Type: {type(e).__name__}</h2>
        <pre>{str(e)}</pre>
        <h3>Traceback:</h3>
        <pre>{traceback.format_exc()}</pre>
        </body></html>
        """
        return error_html


@app.post("/process")
async def process(
    psa_file: UploadFile = File(...),
    excel_file: UploadFile = File(None),
) -> StreamingResponse:
    """Upload PSA and get ZIP with Product + Planogram data + Validation report.
    
    Args:
        psa_file: PSA file (required)
        excel_file: Excel reference file for department validation (optional)
    """
    
    # Check for import errors
    if process_psa_file is None or create_excel_export is None:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Import error",
                "details": import_errors
            }
        )
    
    try:
        print("="*80)
        print("[API] POST /process endpoint called!")
        print("="*80)
        print(f"[API] Received PSA file: {psa_file.filename}")
        psa_bytes = await psa_file.read()
        print(f"[API] Read {len(psa_bytes)} bytes from uploaded PSA file")
        
        # Read Excel reference file if provided
        excel_bytes = None
        if excel_file and excel_file.filename:
            print(f"[API] Received Excel file: {excel_file.filename}")
            excel_bytes = await excel_file.read()
            print(f"[API] Read {len(excel_bytes)} bytes from Excel file")
        else:
            print("[API] No Excel reference file provided - department validation will be skipped")
        
        # Process PSA file (extract Product + Planogram)
        print(f"[API] Processing PSA file...")
        data = process_psa_file(psa_bytes, excel_reference_bytes=excel_bytes)
        
        # Generate ZIP with Excel files
        print(f"[API] Generating Excel exports...")
        zip_bytes = create_excel_export(data)
        
        print(f"[API] Returning ZIP ({len(zip_bytes)} bytes)")
        
        # Return ZIP file
        headers = {"Content-Disposition": "attachment; filename=PSA_Export.zip"}
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers=headers
        )
    except Exception as e:
        print("="*80)
        print(f"[ERROR] Failed to process PSA file: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        # Return detailed error as JSON
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
