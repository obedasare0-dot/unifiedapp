"""HTML templates for the unified PSA processing UI."""

def get_home_page() -> str:
    """Return the home page HTML with upload form."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PSA Unified Processor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0053e2 0%, #00a8e1 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #0053e2;
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .badge {
            background: #ffc220;
            color: #000;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        
        .hint {
            background: #e0f2fe;
            border-left: 4px solid #0053e2;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            line-height: 1.6;
        }
        
        .upload-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .file-group {
            margin-bottom: 20px;
        }
        
        .file-label {
            display: block;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .required {
            color: #ea1100;
        }
        
        .optional {
            color: #6b7280;
            font-weight: normal;
            font-size: 12px;
        }
        
        .file-input-wrapper {
            position: relative;
        }
        
        input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px dashed #0053e2;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        input[type="file"]:hover {
            border-color: #0046c7;
            background: #f0f4ff;
        }
        
        .file-hint {
            font-size: 12px;
            color: #6b7280;
            margin-top: 5px;
            font-style: italic;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 14px 32px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            flex: 1;
            justify-content: center;
            min-width: 200px;
        }
        
        .btn-primary {
            background: #0053e2;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0046c7;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 83, 226, 0.3);
        }
        
        .btn-secondary {
            background: #2a8703;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #237002;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(42, 135, 3, 0.3);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .spinner {
            display: none;
            width: 16px;
            height: 16px;
            border: 2px solid transparent;
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }
        
        .btn:disabled .spinner {
            display: inline-block;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.85rem;
            color: #6b7280;
        }
        
        .success {
            background: #d1fae5;
            border-left-color: #10b981;
            color: #065f46;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                🗂️ PSA Unified Processor
                <span class="badge">MULTI-TABLE</span>
            </h1>
        </div>
        
        <div class="hint">
            <strong>Extract Product + Planogram data from PSA file.</strong><br>
            📁 <strong>PSA File</strong> (required) - ProSpace .psa file to process<br>
            📊 <strong>Excel Reference</strong> (optional) - Mod handoff file for department validation<br>
            <br>
            Choose action:<br>
            📊 <strong>View Report</strong> - Interactive validation dashboard in browser<br>
            💾 <strong>Download ZIP</strong> - Get Excel files (PSA_Data.xlsx + Validation_Report.xlsx)
        </div>
        
        <form
            class="upload-form"
            id="mainForm"
            method="post"
            enctype="multipart/form-data"
        >
            <div class="file-group">
                <label class="file-label">
                    📁 PSA File <span class="required">*</span>
                </label>
                <div class="file-input-wrapper">
                    <input
                        type="file"
                        name="psa_file"
                        id="psaFile"
                        accept=".psa"
                        required
                    />
                </div>
            </div>
            
            <div class="file-group">
                <label class="file-label">
                    📊 Excel Reference File <span class="optional">(optional)</span>
                </label>
                <div class="file-input-wrapper">
                    <input
                        type="file"
                        name="excel_file"
                        id="excelFile"
                        accept=".xlsx,.xls"
                    />
                </div>
                <div class="file-hint">Mod_Hand_Off.xlsx for department validation</div>
            </div>
            
            <div class="button-group">
                <button type="button" class="btn btn-secondary" onclick="viewReport()">
                    <span class="spinner"></span>
                    📊 View Report
                </button>
                <button type="button" class="btn btn-primary" onclick="downloadZip()">
                    <span class="spinner"></span>
                    💾 Download ZIP
                </button>
            </div>
        </form>
        
        <div id="hint" class="hint">
            Select files and choose: View Report (browser) or Download ZIP (Excel files).
        </div>
        
        <div class="footer">
            <p>💡 Tip: Upload Excel reference file to enable department validation check</p>
        </div>
    </div>
    
    <script>
        const form = document.getElementById('mainForm');
        const fileInput = document.getElementById('psaFile');
        const hint = document.getElementById('hint');
        const viewBtn = document.querySelector('.btn-secondary');
        const downloadBtn = document.querySelector('.btn-primary');
        
        function viewReport() {
            if (!fileInput.files.length) {
                alert('Please select a PSA file first!');
                return;
            }
            
            // Disable ONLY the View Report button and show spinner
            viewBtn.disabled = true;
            viewBtn.innerHTML = '<span class="spinner" style="display: inline-block;"></span> Loading Report...';
            hint.className = 'hint';
            hint.innerHTML = '⏳ Processing PSA file and generating report... Please wait.';
            
            // Submit to /view-report
            form.action = '/view-report';
            form.submit();
        }
        
        function downloadZip() {
            if (!fileInput.files.length) {
                alert('Please select a PSA file first!');
                return;
            }
            
            // Disable ONLY the Download ZIP button and show spinner
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<span class="spinner" style="display: inline-block;"></span> Downloading...';
            hint.className = 'hint';
            hint.innerHTML = '⏳ Processing PSA file... Please wait for download to start.';
            
            // Submit to /process
            form.action = '/process';
            form.submit();
            
            // Re-enable ONLY the download button after delay (keep file selected!)
            setTimeout(() => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<span class="spinner"></span>💾 Download ZIP';
                hint.className = 'hint success';
                hint.innerHTML = '<strong style="color: #10b981;">✓ ZIP file downloaded!</strong> You can now click "View Report" to see the validation dashboard, or upload new files.';
                
                // Reset hint after 8 seconds (but keep files selected)
                setTimeout(() => {
                    hint.className = 'hint';
                    hint.innerHTML = 'Files ready! Click "View Report" or "Download ZIP" again, or select new files.';
                }, 8000);
            }, 3000);
        }
    </script>
</body>
</html>
"""
