"""Dark-themed HTML templates for the unified PSA processing UI."""

def get_home_page() -> str:
    """Return the dark-themed home page HTML with upload form."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PSA Unified Processor - Walmart</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1f2e;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 700px;
            width: 100%;
        }
        
        .card {
            background: #242936;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
            padding: 40px;
            margin-bottom: 20px;
            border: 1px solid #2d3548;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #ffffff;
            font-size: 32px;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .subtitle {
            color: #8b92a8;
            font-size: 16px;
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
            display: inline-block;
            margin-top: 10px;
        }
        
        .hint {
            background: #1e2433;
            border-left: 4px solid #4a90e2;
            padding: 15px;
            margin-bottom: 25px;
            border-radius: 4px;
            font-size: 14px;
            color: #b4b9c8;
            line-height: 1.6;
        }
        
        .hint strong {
            color: #ffffff;
        }
        
        .upload-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .file-group {
            margin-bottom: 20px;
        }
        
        .file-label {
            display: block;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .required {
            color: #ff6b6b;
        }
        
        .optional {
            color: #8b92a8;
            font-weight: normal;
            font-size: 12px;
        }
        
        .file-input-wrapper {
            position: relative;
        }
        
        input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px dashed #4a90e2;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            background: #1e2433;
            color: #b4b9c8;
        }
        
        input[type="file"]:hover {
            border-color: #5ba3f5;
            background: #252b3d;
        }
        
        .file-hint {
            font-size: 12px;
            color: #8b92a8;
            margin-top: 5px;
            font-style: italic;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }
        
        .btn {
            flex: 1;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary {
            background: #4a90e2;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5ba3f5;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
        }
        
        .btn-secondary {
            background: #2a8703;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #349a04;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(42, 135, 3, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn:disabled:hover {
            transform: none;
            box-shadow: none;
        }
        
        .spinner {
            display: none;
            width: 16px;
            height: 16px;
            border: 2px solid #ffffff;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        
        .btn.loading .spinner {
            display: inline-block;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .hint.success {
            background: #1e3a1e;
            border-left-color: #2a8703;
            color: #7dd957;
        }
        
        .hint.error {
            background: #3a1e1e;
            border-left-color: #ea1100;
            color: #ff8080;
        }
        
        .footer {
            text-align: center;
            color: #8b92a8;
            font-size: 14px;
            margin-top: 20px;
            background: #242936;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #2d3548;
        }
        
        .footer p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <h1>🗂️ PSA Unified Processor</h1>
                <p class="subtitle">Extract & Validate Product + Planogram Data</p>
                <span class="badge">MULTI-TABLE</span>
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
        </div>
        
        <div id="hint" class="hint">
            Select files and choose: View Report (browser) or Download ZIP (Excel files).
        </div>
        
        <div class="footer">
            <p>💡 Tip: Upload Excel reference file to enable department validation check</p>
        </div>
    </div>
    
    <script>
        function setLoading(button, isLoading) {
            if (isLoading) {
                button.classList.add('loading');
                button.disabled = true;
            } else {
                button.classList.remove('loading');
                button.disabled = false;
            }
        }
        
        function viewReport() {
            const form = document.getElementById('mainForm');
            const psaFile = document.getElementById('psaFile').files[0];
            const hint = document.getElementById('hint');
            const button = event.target;
            
            if (!psaFile) {
                hint.className = 'hint error';
                hint.innerHTML = '<strong style="color: #ff8080;">⚠️ Please select a PSA file first!</strong>';
                return;
            }
            
            hint.className = 'hint';
            hint.innerHTML = '⏳ Processing PSA file and generating validation report...';
            setLoading(button, true);
            
            const formData = new FormData(form);
            
            fetch('/view-report', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                document.open();
                document.write(html);
                document.close();
            })
            .catch(error => {
                setLoading(button, false);
                hint.className = 'hint error';
                hint.innerHTML = `<strong style="color: #ff8080;">❌ Error: ${error.message}</strong><br>Please try again or check the file format.`;
            });
        }
        
        function downloadZip() {
            const form = document.getElementById('mainForm');
            const psaFile = document.getElementById('psaFile').files[0];
            const hint = document.getElementById('hint');
            const button = event.target;
            
            if (!psaFile) {
                hint.className = 'hint error';
                hint.innerHTML = '<strong style="color: #ff8080;">⚠️ Please select a PSA file first!</strong>';
                return;
            }
            
            hint.className = 'hint';
            hint.innerHTML = '⏳ Processing PSA file and generating ZIP archive...';
            setLoading(button, true);
            
            const formData = new FormData(form);
            
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) throw new Error('Processing failed');
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'PSA_Export.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                setLoading(button, false);
                hint.className = 'hint success';
                hint.innerHTML = '<strong style="color: #7dd957;">✓ ZIP file downloaded!</strong> You can now click "View Report" to see the validation dashboard, or upload new files.';
                
                // Reset hint after 8 seconds (but keep files selected)
                setTimeout(() => {
                    hint.className = 'hint';
                    hint.innerHTML = 'Files ready! Click "View Report" or "Download ZIP" again, or select new files.';
                }, 8000);
            })
            .catch(error => {
                setLoading(button, false);
                hint.className = 'hint error';
                hint.innerHTML = `<strong style="color: #ff8080;">❌ Error: ${error.message}</strong><br>Please try again or check the file format.`;
            });
        }
    </script>
</body>
</html>
    """
