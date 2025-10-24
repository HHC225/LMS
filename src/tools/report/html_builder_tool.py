"""
HTML Report Builder Tool
Converts structured JSON data into professional HTML reports
"""
import json
import re
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from fastmcp import Context

from src.tools.base import BaseTool
from configs.report import ReportConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HTMLBuilderTool(BaseTool):
    """
    Tool to build HTML reports from structured JSON data
    """
    
    def __init__(self):
        super().__init__(
            name="build_report_from_json",
            description="Build final HTML report from structured JSON data"
        )
        self.config = ReportConfig
    
    async def execute(
        self,
        report_json: Dict[str, Any],
        ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Execute HTML report building
        
        Args:
            report_json: Structured JSON data following the fixed schema
            ctx: MCP context for logging
            
        Returns:
            Dictionary containing the report file path and status
        """
        try:
            await self.log_execution(ctx, "Building HTML report from JSON data")
            
            # Validate JSON structure
            if self.config.REPORT_VALIDATE_JSON:
                self._validate_report_json(report_json)
            
            # Build HTML report
            output_path = await self._build_html_report(report_json)
            
            logger.info(f"Successfully generated HTML report: {output_path}")
            
            return {
                "status": "success",
                "file_path": str(output_path),
                "report_title": report_json.get("report_title", "Untitled"),
                "report_type": report_json.get("report_type", "General"),
                "severity": report_json.get("severity", "Medium")
            }
            
        except Exception as e:
            error_msg = f"Error building HTML report: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if ctx:
                await ctx.error(error_msg)
            return {
                "status": "error",
                "error_message": error_msg
            }
    
    def _validate_report_json(self, report_json: Dict[str, Any]) -> None:
        """Validate JSON structure"""
        required_fields = [
            "report_title", "report_type", "severity",
            "strategic_summary", "key_findings", "metadata"
        ]
        
        missing_fields = [field for field in required_fields if field not in report_json]
        if missing_fields:
            raise ValueError(f"Missing required fields in JSON: {missing_fields}")
    
    async def _build_html_report(self, report_data: Dict[str, Any]) -> Path:
        """
        Build HTML report from JSON data and templates
        
        Args:
            report_data: Structured report data in JSON format
            
        Returns:
            Path to the generated HTML file
        """
        # Ensure output directory exists
        self.config.REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        html_template = self._load_template("report_template.html")
        css_template = self._load_template("report_styles.css")
        js_template = self._load_template("report_script.js")
        
        # Generate report content
        report_html = self._generate_report_content(report_data)
        
        # Replace placeholders in HTML
        html_content = html_template.replace("{{REPORT_CONTENT}}", report_html)
        html_content = html_content.replace("{{REPORT_TITLE}}", report_data.get("report_title", "IT Report"))
        html_content = html_content.replace("{{STYLES}}", css_template)
        html_content = html_content.replace("{{SCRIPTS}}", js_template)
        html_content = html_content.replace("{{REPORT_DATA}}", json.dumps(report_data, ensure_ascii=False, indent=2))
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_type = report_data.get("report_type", "report").replace(" ", "_").lower()
        output_filename = f"{report_type}_{timestamp}.html"
        output_path = self.config.REPORT_OUTPUT_DIR / output_filename
        
        # Write HTML file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_path
    
    def _load_template(self, filename: str) -> str:
        """Load template file content"""
        template_path = self.config.REPORT_TEMPLATES_DIR / filename
        
        if not template_path.exists():
            logger.error(f"Template file not found: {template_path}")
            raise FileNotFoundError(f"Template file not found: {filename}")
        
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _generate_report_content(self, data: Dict[str, Any]) -> str:
        """Generate HTML content from report data"""
        html_parts = []
        
        # Header Info
        severity = data.get("severity", "medium").lower()
        html_parts.extend([
            '<div class="report-header-info">',
            f'<span class="severity-badge severity-{severity}">{severity.upper()}</span>',
            f'<span class="report-type">{data.get("report_type", "Report")}</span>',
            '</div>'
        ])
        
        # Strategic Summary Section
        strategic_summary = data.get("strategic_summary", {})
        html_parts.extend([
            '<section class="report-section summary-section" data-aos="fade-up">',
            '<h2>Strategic Summary</h2>',
            '<div class="summary-grid">',
            '<div class="glass-card">',
            '<div class="card-content">',
            '<h3>Overview</h3>',
            f'<p>{self._format_content(strategic_summary.get("overview", "No overview provided"))}</p>',
            '</div>',
            '</div>',
            '<div class="glass-card">',
            '<div class="card-content">',
            '<h3>Business Implications</h3>',
            f'<p>{self._format_content(strategic_summary.get("business_implications", "Not specified"))}</p>',
            '</div>',
            '</div>',
            '<div class="glass-card">',
            '<div class="card-content">',
            '<h3>Next Steps Summary</h3>',
            f'<p class="status-value">{self._format_content(strategic_summary.get("next_steps_summary", "Unknown"))}</p>',
            '</div>',
            '</div>',
            '</div>'
        ])
        
        # Key Takeaways
        key_takeaways = strategic_summary.get("key_takeaways", [])
        if key_takeaways:
            html_parts.extend([
                '<div class="glass-card" style="margin-top: 1rem;">',
                '<div class="card-content">',
                '<h3>Key Takeaways</h3>',
                '<ul class="key-takeaways-list">'
            ])
            for takeaway in key_takeaways:
                html_parts.append(f'<li>{self._format_content(takeaway)}</li>')
            html_parts.extend([
                '</ul>',
                '</div>',
                '</div>'
            ])
        
        html_parts.append('</section>')
        
        # Key Findings Section
        key_findings = data.get("key_findings", {})
        if key_findings:
            html_parts.extend([
                '<section class="report-section analysis-section" data-aos="fade-up">',
                '<h2>Key Findings</h2>'
            ])
            
            # Root Cause
            root_cause = key_findings.get("root_cause")
            if root_cause:
                html_parts.extend([
                    '<div class="glass-card analysis-block">',
                    '<div class="card-content">',
                    '<h3>Root Cause</h3>',
                    f'<p>{self._format_content(str(root_cause))}</p>',
                    '</div>',
                    '</div>'
                ])
            
            # Key Events
            key_events = key_findings.get("key_events", [])
            if key_events:
                html_parts.extend([
                    '<div class="glass-card detail-block">',
                    '<div class="card-content">',
                    '<h3>Key Events</h3>',
                    '<ul class="key-events-list">'
                ])
                for event in key_events:
                    html_parts.append(f'<li>{self._format_content(str(event))}</li>')
                html_parts.extend([
                    '</ul>',
                    '</div>',
                    '</div>'
                ])
            
            # Affected Systems
            affected_systems = key_findings.get("affected_systems", [])
            if affected_systems:
                html_parts.extend([
                    '<div class="glass-card detail-block">',
                    '<div class="card-content">',
                    '<h3>Affected Systems</h3>',
                    '<ul class="affected-systems-list">'
                ])
                for system in affected_systems:
                    html_parts.append(f'<li>{self._format_content(str(system))}</li>')
                html_parts.extend([
                    '</ul>',
                    '</div>',
                    '</div>'
                ])
            
            html_parts.append('</section>')
        
        # Metrics & Charts Section (Optional)
        metrics = data.get("metrics")
        if metrics and metrics.get("charts"):
            html_parts.extend([
                '<section class="report-section charts-section" data-aos="fade-up">',
                '<h2>Metrics & Analytics</h2>',
                '<div class="charts-grid">'
            ])
            
            for chart in metrics.get("charts", []):
                chart_id = self._sanitize_chart_id(chart.get("id", f"chart-{len(html_parts)}"))
                chart_title = chart.get("title", "Chart")
                
                html_parts.extend([
                    '<div class="glass-card chart-card">',
                    '<div class="card-content">',
                    f'<h3>{self._format_content(chart_title)}</h3>',
                    '<div class="chart-container">',
                    f'<canvas id="{chart_id}"></canvas>',
                    '</div>',
                    '</div>',
                    '</div>'
                ])
            
            html_parts.extend([
                '</div>',
                '</section>'
            ])
        
        # Metadata Section
        metadata = data.get("metadata", {})
        html_parts.extend([
            '<section class="report-section metadata-section" data-aos="fade-up">',
            '<h2>Report Information</h2>',
            '<div class="glass-card">',
            '<div class="card-content">',
            '<div class="metadata-grid">'
        ])
        
        metadata_items = [
            ("Reported Date", metadata.get("reported_date", "Not specified")),
        ]
        
        for label, value in metadata_items:
            html_parts.extend([
                '<div class="metadata-item">',
                f'<span class="metadata-label">{label}</span>',
                f'<span class="metadata-value">{value}</span>',
                '</div>'
            ])
        
        html_parts.append('</div>')
        
        # Tags
        tags = metadata.get("tags", [])
        if tags:
            html_parts.extend([
                '<div class="tags-container">',
                *[f'<span class="tag">{tag}</span>' for tag in tags],
                '</div>'
            ])
        
        html_parts.extend([
            '</div>',
            '</div>',
            '</section>'
        ])
        
        return "\n".join(html_parts)
    
    @staticmethod
    def _sanitize_chart_id(chart_id: str) -> str:
        """Sanitize chart ID to be valid HTML id"""
        # Remove special characters except hyphens and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', chart_id)
        # Ensure it starts with a letter
        if not sanitized[0].isalpha():
            sanitized = 'chart-' + sanitized
        return sanitized
    
    @staticmethod
    def _format_content(content: str) -> str:
        """Format content with basic markdown-like syntax"""
        # Convert **bold** to <strong>
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        
        # Convert newlines to <br>
        content = content.replace("\n", "<br>")
        
        return content
