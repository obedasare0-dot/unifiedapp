"""Enhanced HTML templates for PSA processing UI."""

def get_home_page() -> str:
    """Return enhanced home page with professional styling."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PSA Processor - Walmart</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            min-height: 100vh;
        }
        
        .top-header {
            background: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 16px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-left h1 {
            font-size: 20px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 4px;
        }
        
        .header-left .subtitle {
            font-size: 14px;
            color: #8b949e;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .user-email {
            font-size: 13px;
            color: #8b949e;
            margin-right: 8px;
        }
        
        .status-badge {
            background: #1f6feb;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 32px;
        }
        
        .page-title {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .page-title h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 56px;
            font-weight: 700;
            background: linear-gradient(135deg, #0071e3 0%, #00a3ff 50%, #ffc220 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
            letter-spacing: -1px;
            text-shadow: 0 0 40px rgba(0, 163, 255, 0.3);
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .page-title .description {
            font-size: 16px;
            color: #8b949e;
        }
        
        .steps-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px 0 60px 0;
            gap: 60px;
        }
        
        .step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            position: relative;
        }
        
        .step:not(:last-child)::after {
            content: '';
            position: absolute;
            top: 25px;
            left: calc(100% + 10px);
            width: 40px;
            height: 2px;
            background: #30363d;
        }
        
        .step-circle {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 600;
            border: 3px solid;
        }
        
        .step-circle.orange {
            border-color: #f85149;
            background: rgba(248, 81, 73, 0.1);
            color: #ff7b72;
        }
        
        .step-circle.blue {
            border-color: #1f6feb;
            background: rgba(31, 111, 235, 0.1);
            color: #58a6ff;
        }
        
        .step-circle.green {
            border-color: #3fb950;
            background: rgba(63, 185, 80, 0.1);
            color: #56d364;
        }
        
        .step-label {
            text-align: center;
        }
        
        .step-title {
            font-size: 14px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 4px;
        }
        
        .step-subtitle {
            font-size: 11px;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .step-subtitle.orange {
            color: #ff7b72;
        }
        
        .step-subtitle.blue {
            color: #58a6ff;
        }
        
        .step-subtitle.green {
            color: #56d364;
        }
        
        .main-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 24px;
        }
        
        .card-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #30363d;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 8px;
        }
        
        .card-description {
            font-size: 14px;
            color: #8b949e;
            line-height: 1.6;
        }
        
        .upload-section {
            margin-bottom: 24px;
        }
        
        .file-group {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            transition: border-color 0.2s;
        }
        
        .file-group:hover {
            border-color: #58a6ff;
        }
        
        .file-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .file-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .file-icon.psa {
            background: rgba(248, 81, 73, 0.15);
            color: #ff7b72;
        }
        
        .file-icon.excel {
            background: rgba(63, 185, 80, 0.15);
            color: #56d364;
        }
        
        .file-info {
            flex: 1;
        }
        
        .file-label {
            font-size: 15px;
            font-weight: 600;
            color: #f0f6fc;
            margin-bottom: 4px;
        }
        
        .required-badge {
            display: inline-block;
            background: rgba(248, 81, 73, 0.15);
            color: #ff7b72;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 8px;
            text-transform: uppercase;
        }
        
        .optional-badge {
            display: inline-block;
            background: rgba(139, 148, 158, 0.15);
            color: #8b949e;
            font-size: 10px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 8px;
            text-transform: uppercase;
        }
        
        .file-hint {
            font-size: 13px;
            color: #8b949e;
        }
        
        input[type="file"] {
            width: 100%;
            padding: 12px;
            background: #0d1117;
            border: 2px dashed #30363d;
            border-radius: 6px;
            color: #8b949e;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }
        
        input[type="file"]:hover {
            border-color: #58a6ff;
            background: rgba(88, 166, 255, 0.05);
        }
        
        .button-group {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }
        
        .btn {
            flex: 1;
            padding: 14px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-primary {
            background: #1f6feb;
            color: white;
        }
        
        .btn-primary:hover:not(:disabled) {
            background: #388bfd;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3);
        }
        
        .btn-secondary {
            background: #238636;
            color: white;
        }
        
        .btn-secondary:hover:not(:disabled) {
            background: #2ea043;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(46, 160, 67, 0.3);
        }
        
        .spinner {
            display: none;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        .btn.loading .spinner {
            display: inline-block;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .hint-box {
            background: rgba(88, 166, 255, 0.1);
            border: 1px solid rgba(88, 166, 255, 0.3);
            border-left: 4px solid #58a6ff;
            padding: 16px;
            border-radius: 6px;
            margin-top: 24px;
            font-size: 14px;
            color: #8b949e;
        }
        
        .hint-box.success {
            background: rgba(86, 211, 100, 0.1);
            border-color: rgba(86, 211, 100, 0.3);
            border-left-color: #56d364;
        }
        
        .hint-box.error {
            background: rgba(255, 123, 114, 0.1);
            border-color: rgba(255, 123, 114, 0.3);
            border-left-color: #ff7b72;
        }
        
        .footer {
            text-align: center;
            padding: 24px;
            font-size: 13px;
            color: #6e7681;
        }
        
        .footer a {
            color: #58a6ff;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <!-- Top Header -->
    <div class="top-header">
        <div class="header-left">
            <h1>🗂️ PSA Unified Processor</h1>
            <div class="subtitle">ProSpace Analytics • Multi-Table Validation</div>
        </div>
        <div class="header-right">
            <span class="user-email">o0a03zr@homeoffice.wal-mart.com</span>
            <span class="status-badge">Ready</span>
        </div>
    </div>
    
    <!-- Main Container -->
    <div class="container">
        <!-- Page Title -->
        <div class="page-title">
            <h1>Data Processing Center</h1>
            <p class="description">Extract, validate, and analyze your PSA files in 3 simple steps</p>
        </div>
        
        <!-- Step Progression -->
        <div class="steps-container">
            <div class="step">
                <div class="step-circle orange">1</div>
                <div class="step-label">
                    <div class="step-title">Upload Files</div>
                    <div class="step-subtitle orange">Required</div>
                </div>
            </div>
            
            <div class="step">
                <div class="step-circle blue">2</div>
                <div class="step-label">
                    <div class="step-title">Process Data</div>
                    <div class="step-subtitle blue">Automated</div>
                </div>
            </div>
            
            <div class="step">
                <div class="step-circle green">3</div>
                <div class="step-label">
                    <div class="step-title">View Results</div>
                    <div class="step-subtitle green">Download</div>
                </div>
            </div>
        </div>
        
        <!-- Main Upload Card -->
        <div class="main-card">
            <div class="card-header">
                <div class="card-title">📁 File Upload</div>
                <div class="card-description">
                    Upload your PSA file and optional Excel reference for comprehensive validation.
                    The system will automatically extract Product, Planogram, and Fixture tables, run 37 validation checks (21 Product + 8 Planogram + 8 Fixture), and generate detailed reports.
                </div>
            </div>
            
            <form id="mainForm" method="post" enctype="multipart/form-data">
                <div class="upload-section">
                    <!-- PSA File Upload -->
                    <div class="file-group">
                        <div class="file-header">
                            <div class="file-icon psa">📄</div>
                            <div class="file-info">
                                <div class="file-label">
                                    PSA File
                                    <span class="required-badge">Required</span>
                                </div>
                                <div class="file-hint">ProSpace .psa file containing Product, Planogram, and Fixture data</div>
                            </div>
                        </div>
                        <input type="file" name="psa_file" id="psaFile" accept=".psa" required />
                    </div>
                    
                    <!-- Excel Reference Upload -->
                    <div class="file-group">
                        <div class="file-header">
                            <div class="file-icon excel">📊</div>
                            <div class="file-info">
                                <div class="file-label">
                                    Excel Reference File
                                    <span class="optional-badge">Optional</span>
                                </div>
                                <div class="file-hint">Mod_Hand_Off.xlsx for Department, Category, and Has_Alt_UPC validation</div>
                            </div>
                        </div>
                        <input type="file" name="excel_file" id="excelFile" accept=".xlsx,.xls" />
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="button-group">
                    <button type="button" class="btn btn-secondary" onclick="viewReport()">
                        <span class="spinner"></span>
                        <span>📊 View Report</span>
                    </button>
                    <button type="button" class="btn btn-primary" onclick="downloadZip()">
                        <span class="spinner"></span>
                        <span>💾 Download ZIP</span>
                    </button>
                </div>
            </form>
            
            <!-- Status Hint -->
            <div id="hint" class="hint-box">
                💡 <strong>Tip:</strong> Upload the Excel reference file to enable advanced validation checks (Department, Category, Has_Alt_UPC).
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>PSA Processor v2.1 • Extracts Product + Planogram + Fixture tables • 37 validation checks • Built for Walmart</p>
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
            const button = event.target.closest('button');
            
            if (!psaFile) {
                hint.className = 'hint-box error';
                hint.innerHTML = '<strong>⚠️ Error:</strong> Please select a PSA file first!';
                return;
            }
            
            hint.className = 'hint-box';
            hint.innerHTML = '⏳ Processing PSA file and generating validation report...';
            setLoading(button, true);
            
            const formData = new FormData(form);
            
            fetch('view-report', {
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
                hint.className = 'hint-box error';
                hint.innerHTML = `<strong>❌ Error:</strong> ${error.message}<br>Please try again or check the file format.`;
            });
        }
        
        function downloadZip() {
            const form = document.getElementById('mainForm');
            const psaFile = document.getElementById('psaFile').files[0];
            const hint = document.getElementById('hint');
            const button = event.target.closest('button');
            
            if (!psaFile) {
                hint.className = 'hint-box error';
                hint.innerHTML = '<strong>⚠️ Error:</strong> Please select a PSA file first!';
                return;
            }
            
            hint.className = 'hint-box';
            hint.innerHTML = '⏳ Processing PSA file and generating ZIP archive...';
            setLoading(button, true);
            
            const formData = new FormData(form);
            
            fetch('process', {
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
                hint.className = 'hint-box success';
                hint.innerHTML = '<strong>✓ Success!</strong> ZIP file downloaded. You can now click "View Report" to see the validation dashboard, or upload new files.';
                
                setTimeout(() => {
                    hint.className = 'hint-box';
                    hint.innerHTML = '💡 <strong>Tip:</strong> Upload the Excel reference file to enable advanced validation checks.';
                }, 8000);
            })
            .catch(error => {
                setLoading(button, false);
                hint.className = 'hint-box error';
                hint.innerHTML = `<strong>❌ Error:</strong> ${error.message}<br>Please try again or check the file format.`;
            });
        }
    </script>
</body>
</html>
    """
