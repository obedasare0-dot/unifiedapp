"""Validation Dashboard HTML Template."""

from typing import List, Dict, Any
from app.services.product_validator import ValidationResult


def get_validation_dashboard(data: Dict[str, Any]) -> str:
    """Generate interactive HTML dashboard for validation results.
    
    Args:
        data: Dict from psa_processor containing:
            - product_df, product_validation, product_summary
            - planogram_df, planogram_validation, planogram_summary
    
    Returns:
        HTML string for validation dashboard
    """
    
    # Calculate combined stats
    total_checks = 0
    total_passed = 0
    total_failed = 0
    total_warnings = 0
    total_records = 0
    
    if data['product_df'] is not None:
        total_records += len(data['product_df'])
    if data['planogram_df'] is not None:
        total_records += len(data['planogram_df'])
    if data.get('fixture_df') is not None:
        total_records += len(data['fixture_df'])
    
    if data['product_summary']:
        total_checks += data['product_summary']['total_checks']
        total_passed += data['product_summary']['passed']
        total_failed += data['product_summary']['failed']
        total_warnings += data['product_summary']['warnings']
    
    if data['planogram_summary']:
        total_checks += data['planogram_summary']['total_checks']
        total_passed += data['planogram_summary']['passed']
        total_failed += data['planogram_summary']['failed']
        total_warnings += data['planogram_summary']['warnings']
    
    if data.get('fixture_summary'):
        total_checks += data['fixture_summary']['total_checks']
        total_passed += data['fixture_summary']['passed']
        total_failed += data['fixture_summary']['failed']
        total_warnings += data['fixture_summary']['warnings']
    
    # Determine overall status
    if total_failed > 0:
        overall_status = "FAIL"
        status_color = "#ea1100"  # Walmart red
        status_bg = "#fff0f0"
    elif total_warnings > 0:
        overall_status = "WARNING"
        status_color = "#995213"  # Walmart spark dark
        status_bg = "#fffbeb"
    else:
        overall_status = "PASS"
        status_color = "#2a8703"  # Walmart green
        status_bg = "#f0fdf4"
    
    # Generate Product checks HTML
    product_checks_html = _generate_table_checks_html(
        "Product",
        data['product_validation'],
        data['product_summary']
    )
    
    # Generate Planogram checks HTML
    planogram_checks_html = _generate_table_checks_html(
        "Planogram",
        data['planogram_validation'],
        data['planogram_summary']
    )
    
    # Generate Fixture checks HTML
    fixture_checks_html = _generate_table_checks_html(
        "Fixture",
        data.get('fixture_validation', []),
        data.get('fixture_summary', {'total_checks': 0, 'passed': 0, 'failed': 0, 'warnings': 0})
    )
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Validation Report - PSA Processor</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #1a1f2e;
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .header {{
                background: #242936;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
                border: 1px solid #2d3548;
            }}
            
            h1 {{
                color: #ffffff;
                font-size: 32px;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: #8b92a8;
                font-size: 16px;
            }}
            
            .summary-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .card {{
                background: #242936;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
                text-align: center;
                border: 1px solid #2d3548;
            }}
            
            .card-title {{
                color: #8b92a8;
                font-size: 14px;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .card-value {{
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .card-label {{
                color: #999;
                font-size: 12px;
            }}
            
            .card.status {{
                background: {status_bg};
                border: 2px solid {status_color};
            }}
            
            .card.status .card-value {{
                color: {status_color};
            }}
            
            .card.passed .card-value {{
                color: #2a8703;
            }}
            
            .card.failed .card-value {{
                color: #ea1100;
            }}
            
            .card.warnings .card-value {{
                color: #995213;
            }}
            
            .card.records .card-value {{
                color: #0053e2;
            }}
            
            .section {{
                background: #242936;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
                overflow: hidden;
                border: 1px solid #2d3548;
            }}
            
            .section-header {{
                background: #2d3548;
                color: white;
                padding: 20px 30px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                user-select: none;
                transition: background 0.3s;
            }}
            
            .section-header:hover {{
                background: #363d54;
            }}
            
            .section-title {{
                font-size: 20px;
                font-weight: 600;
            }}
            
            .section-badge {{
                background: rgba(255, 255, 255, 0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
            }}
            
            .section-content {{
                padding: 30px;
                display: none;
            }}
            
            .section.expanded .section-content {{
                display: block;
            }}
            
            .section.expanded .toggle-icon::before {{
                content: '▼';
            }}
            
            .toggle-icon::before {{
                content: '▶';
                display: inline-block;
                transition: transform 0.3s;
            }}
            
            .check-item {{
                border-left: 4px solid #e5e7eb;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 4px;
                background: #f9fafb;
            }}
            
            .check-item.pass {{
                border-left-color: #2a8703;
                background: #f0fdf4;
            }}
            
            .check-item.fail {{
                border-left-color: #ea1100;
                background: #fff0f0;
            }}
            
            .check-item.warning {{
                border-left-color: #ffc220;
                background: #fffbeb;
            }}
            
            .check-name {{
                font-weight: 600;
                font-size: 16px;
                margin-bottom: 8px;
            }}
            
            .check-name.pass {{
                color: #2a8703;
            }}
            
            .check-name.fail {{
                color: #ea1100;
            }}
            
            .check-name.warning {{
                color: #995213;
            }}
            
            .check-status {{
                display: inline-block;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                margin-left: 10px;
            }}
            
            .check-status.pass {{
                background: #2a8703;
                color: white;
            }}
            
            .check-status.fail {{
                background: #ea1100;
                color: white;
            }}
            
            .check-status.warning {{
                background: #ffc220;
                color: #000;
            }}
            
            .check-message {{
                color: #b4b9c8;
                margin-top: 5px;
                font-size: 14px;
            }}
            
            .check-details {{
                margin-top: 10px;
                font-size: 13px;
                color: #8b92a8;
            }}
            
            .error-count {{
                font-weight: 600;
                color: #ea1100;
            }}
            
            .back-button {{
                display: inline-block;
                background: #4a90e2;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
                transition: all 0.3s;
            }}
            
            .back-button:hover {{
                background: #5ba3f5;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
            }}
            
            .footer {{
                text-align: center;
                padding: 20px;
            }}
            
            .summary-stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .stat-box {{
                background: #f9fafb;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #0053e2;
            }}
            
            .stat-label {{
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }}
            
            .hidden {{
                display: none;
            }}
            
            .toggle-arrow.rotated {{
                transform: rotate(180deg);
            }}
            
            .check-detail-item {{
                background: #1e2433;
                border-left: 4px solid #2d3548;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 4px;
            }}
            
            .check-detail-item.pass {{
                border-left-color: #2a8703;
                background: #1e3a1e;
            }}
            
            .check-detail-item.fail {{
                border-left-color: #ea1100;
                background: #3a1e1e;
            }}
            
            .check-detail-item.warning {{
                border-left-color: #ffc220;
                background: #3a351e;
            }}
            
            .check-detail-name {{
                font-weight: 600;
                font-size: 15px;
                margin-bottom: 5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #ffffff;
            }}
            
            .check-detail-badge {{
                display: inline-block;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            
            .check-detail-badge.pass {{
                background: #2a8703;
                color: white;
            }}
            
            .check-detail-badge.fail {{
                background: #ea1100;
                color: white;
            }}
            
            .check-detail-badge.warning {{
                background: #ffc220;
                color: #000;
            }}
            
            .check-detail-message {{
                color: #b4b9c8;
                font-size: 14px;
                margin-top: 8px;
            }}
            
            .check-detail-info {{
                color: #8b92a8;
                font-size: 13px;
                margin-top: 8px;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Validation Report</h1>
                <p class="subtitle">PSA Multi-Table Validation Results</p>
            </div>
            
            <div class="summary-cards">
                <div class="card status">
                    <div class="card-title">Overall Status</div>
                    <div class="card-value">{overall_status}</div>
                    <div class="card-label">Validation Result</div>
                </div>
                
                <div class="card passed">
                    <div class="card-title">Passed</div>
                    <div class="card-value">{total_passed}</div>
                    <div class="card-label">Checks Passed</div>
                </div>
                
                <div class="card failed">
                    <div class="card-title">Failed</div>
                    <div class="card-value">{total_failed}</div>
                    <div class="card-label">Checks Failed</div>
                </div>
                
                <div class="card warnings">
                    <div class="card-title">Warnings</div>
                    <div class="card-value">{total_warnings}</div>
                    <div class="card-label">Warnings Found</div>
                </div>
                
                <div class="card records">
                    <div class="card-title">Records</div>
                    <div class="card-value">{total_records}</div>
                    <div class="card-label">Total Processed</div>
                </div>
            </div>
            
            {product_checks_html}
            
            {planogram_checks_html}
            
            {fixture_checks_html}
            
            <div class="footer">
                <a href="/" class="back-button">← Back to Upload</a>
            </div>
        </div>
        
        <script>
            // Toggle sections
            document.querySelectorAll('.section-header').forEach(header => {{
                header.addEventListener('click', () => {{
                    header.parentElement.classList.toggle('expanded');
                }});
            }});
            
            // Auto-expand failed sections
            document.querySelectorAll('.section').forEach(section => {{
                const hasFailed = section.querySelector('.check-item.fail');
                if (hasFailed) {{
                    section.classList.add('expanded');
                }}
            }});
        </script>
    </body>
    </html>
    """


def _generate_all_checks_list(validation_results: List[ValidationResult]) -> str:
    """Generate HTML list of all individual validation checks with details.
    
    Args:
        validation_results: List of ValidationResult objects
        
    Returns:
        HTML string with all checks listed
    """
    if not validation_results:
        return "<p style='text-align: center; color: #8b92a8;'>No validation checks run.</p>"
    
    checks_html = ""
    for i, result in enumerate(validation_results, 1):
        status_class = result.status.lower()
        
        checks_html += f"""<div class="check-detail-item {status_class}">
            <div class="check-detail-name">
                <span>{i}. {result.check_name}</span>
                <span class="check-detail-badge {status_class}">{result.status}</span>
            </div>
            <div class="check-detail-message">{result.message}</div>"""
        
        # Add counts if applicable
        if result.error_count > 0 or result.pass_count > 0:
            checks_html += f"""<div class="check-detail-info">Passed: {result.pass_count} | Failed: {result.error_count}</div>"""
        
        # Add details if available
        if result.details and result.details.strip():
            # Truncate if too long
            details_text = result.details if len(result.details) < 300 else result.details[:300] + "..."
            checks_html += f"""<div class="check-detail-info">{details_text}</div>"""
        
        checks_html += "</div>"
    
    return checks_html


def _generate_table_checks_html(table_name: str, validation_results: List[ValidationResult], summary: Dict[str, int]) -> str:
    """Generate HTML for a table's validation summary."""
    
    if not validation_results or not summary:
        return ""
    
    # Calculate pass rate
    pass_rate = 0
    if summary['total_checks'] > 0:
        pass_rate = (summary['passed'] / summary['total_checks']) * 100
    
    # Determine status color
    if summary['failed'] > 0:
        status_color = "#ea1100"
        status_text = "NEEDS ATTENTION"
        status_icon = "⚠️"
    elif summary['warnings'] > 0:
        status_color = "#995213"
        status_text = "WARNING"
        status_icon = "⚠️"
    else:
        status_color = "#2a8703"
        status_text = "ALL PASSED"
        status_icon = "✅"
    
    # Get failed check names (just the names, not full details)
    failed_checks = [r.check_name for r in validation_results if r.status == "FAIL"]
    failed_list = ""
    if failed_checks:
        failed_list = "<ul style='margin: 10px 0; padding-left: 20px;'>"
        for check in failed_checks[:5]:  # Show max 5
            failed_list += f"<li style='color: #ea1100; margin: 5px 0;'>{check}</li>"
        if len(failed_checks) > 5:
            failed_list += f"<li style='color: #8b92a8; margin: 5px 0;'>... and {len(failed_checks) - 5} more</li>"
        failed_list += "</ul>"
    
    # Generate detailed checks list (collapsible)
    all_checks_html = _generate_all_checks_list(validation_results)
    
    return f"""
    <div class="section">
        <div class="section-header">
            <div>
                <span class="section-title">{table_name} Validation</span>
            </div>
            <div>
                <span class="section-badge">{summary['total_checks']} checks | {summary['passed']} passed | {summary['failed']} failed</span>
                <span class="toggle-icon"></span>
            </div>
        </div>
        <div class="section-content">
            <div style="text-align: center; padding: 20px; background: #1e2433; border-radius: 8px; margin-bottom: 20px; border: 1px solid #2d3548;">
                <div style="font-size: 48px; margin-bottom: 10px;">{status_icon}</div>
                <div style="font-size: 24px; font-weight: 600; color: {status_color}; margin-bottom: 5px;">{status_text}</div>
                <div style="font-size: 18px; color: #8b92a8;">{pass_rate:.1f}% Pass Rate</div>
            </div>
            
            <div class="summary-stats">
                <div class="stat-box">
                    <div class="stat-value" style="color: #4a90e2;">{summary['total_checks']}</div>
                    <div class="stat-label">Total Checks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #2a8703;">{summary['passed']}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #ea1100;">{summary['failed']}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color: #995213;">{summary['warnings']}</div>
                    <div class="stat-label">Warnings</div>
                </div>
            </div>
            
            {f'''<div style="margin-top: 20px; padding: 15px; background: #fff0f0; border-left: 4px solid #ea1100; border-radius: 4px;">
                <div style="font-weight: 600; margin-bottom: 10px; color: #ea1100;">Failed Checks:</div>
                {failed_list}
            </div>''' if failed_checks else ''}
            
            <div style="margin-top: 20px; padding: 15px; background: #e0f2fe; border-left: 4px solid #0053e2; border-radius: 4px; text-align: center;">
                <div style="color: #0053e2; font-size: 14px;">
                    📊 <strong>Full validation details available in Excel download</strong><br>
                    <span style="font-size: 12px; color: #8b92a8;">Download the ZIP file to see complete check results and row-level details</span>
                </div>
            </div>
            
            <!-- Collapsible All Checks Section -->
            <div style="margin-top: 20px;">
                <button 
                    onclick="this.parentElement.querySelector('.all-checks-content').classList.toggle('hidden'); this.querySelector('.toggle-arrow').classList.toggle('rotated');" 
                    style="
                        width: 100%;
                        padding: 12px 20px;
                        background: #f3f4f6;
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 600;
                        color: #374151;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        transition: all 0.3s;
                    "
                    onmouseover="this.style.background='#e5e7eb';"
                    onmouseout="this.style.background='#f3f4f6';"
                >
                    <span>📋 View All {summary['total_checks']} Validation Checks</span>
                    <span class="toggle-arrow" style="transition: transform 0.3s; display: inline-block;">▼</span>
                </button>
                <div class="all-checks-content hidden" style="margin-top: 10px;">
                    {all_checks_html}
                </div>
            </div>
        </div>
    </div>
    """