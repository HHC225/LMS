# Report Generator Tool

Generate comprehensive IT reports from raw content such as Slack messages, JIRA tickets, investigation results, and more.

## 📋 Overview

The Report Generator tool converts unstructured IT content into professional, structured HTML reports. It uses AI to analyze raw input and generate executive summaries, detailed analysis, action items, and recommendations.

### Key Features

- **Universal Input**: Accepts any IT-related content (Slack threads, JIRA tickets, logs, emails, etc.)
- **Structured Analysis**: AI-powered content analysis with severity assessment
- **Professional Output**: Beautiful HTML reports with glassmorphism design
- **Executive Summaries**: Key takeaways for leadership and stakeholders
- **Action Tracking**: Prioritized action items with assignees and deadlines
- **Self-Contained**: HTML files include all CSS/JS (no external dependencies)

## 🎯 Use Cases

### Incident Reports
Convert incident communication into formal incident reports:
- Root cause analysis
- Timeline of events
- Impact assessment
- Remediation steps

### Investigation Summaries
Document technical investigations:
- Findings and evidence
- Technical details
- Risk assessment
- Recommendations

### Bug Analysis
Transform bug reports into comprehensive analysis:
- Reproduction steps
- Affected systems
- Priority assessment
- Fix recommendations

### Meeting Notes
Convert meeting discussions into actionable reports:
- Key decisions
- Action items with owners
- Follow-up tasks
- Next steps

## 🚀 Quick Start

### Basic Workflow

The Report Generator uses a **semi-automated process**:

1. **Call `generate_report`**: Provide raw content to analyze
2. **LLM generates JSON**: Following the fixed schema (strategic_summary, key_findings, metadata)
3. **Auto-build HTML**: LLM automatically calls `build_report_from_json` with the generated JSON

```
Raw Content → generate_report → LLM analyzes → JSON Structure → build_report_from_json → HTML Report
                                    (automatic)
```

### Step 1: Generate Report

Call the `generate_report` tool with your content:

**Input Parameters**:
- `content` (required): The raw text to analyze
- `source_type` (optional): Hint about source ("slack", "jira", "email", "investigation")
- `context` (optional): Additional background information

**Example**:
```json
{
  "input_data": {
    "content": "Database connection pool exhausted at 14:23 UTC. Users experiencing 500 errors. Root cause: connection leak in UserService.java line 234. Fixed by adding proper connection.close() in finally block.",
    "source_type": "slack",
    "context": "Production incident on 2025-10-16"
  }
}
```

### Step 2: Provide Structured JSON

After calling `generate_report`, the LLM must respond with a JSON object following this **exact schema**:

```json
{
  "report_title": "Clear, concise title summarizing the event",
  "report_type": "Type of report (e.g., Incident Analysis, Security Alert, System Outage Postmortem)",
  "severity": "low | medium | high | critical",
  "strategic_summary": {
    "overview": "A 2-3 sentence executive summary. What happened and what is the current state?",
    "key_takeaways": [
      "The single most important finding or conclusion.",
      "Another critical piece of information a leader needs to know.",
      "A third key insight, if applicable."
    ],
    "business_implications": "How does this event affect the business? (e.g., potential revenue loss, customer trust, operational delays)",
    "next_steps_summary": "A high-level summary of what will happen next (e.g., 'A full post-mortem is scheduled', 'Security protocols will be reviewed'). Not a task list."
  },
  "key_findings": {
    "root_cause": "The determined root cause or the leading hypothesis, explained in simple terms.",
    "key_events": [
      "A chronological list of the most significant events that occurred."
    ],
    "affected_systems": [
      "List of primary systems, services, or user groups that were impacted."
    ]
  },
  "metadata": {
    "reported_date": "When the event was first reported or detected (ISO 8601 format)",
    "tags": ["relevant", "tags", "for", "categorization"]
  }
}
```

**Note**: The LLM automatically calls `build_report_from_json` after generating this JSON.

### Step 3: HTML Report Auto-Generated

After you provide the structured JSON, the `build_report_from_json` tool is automatically called to generate the HTML report.

**Output**:
```json
{
  "status": "success",
  "file_path": "/path/to/output/reports/incident_analysis_20251016_143022.html",
  "report_title": "Database Connection Pool Exhaustion",
  "report_type": "Incident Analysis",
  "severity": "high"
}
```

## 📊 JSON Schema Reference

### Required Fields

#### `report_title` (string)
Clear, concise title summarizing the event.

**Example**: `"Database Connection Pool Exhaustion"`

#### `report_type` (string)
Type of report being generated.

**Examples**: 
- `"Incident Analysis"`
- `"Security Alert"`
- `"Bug Investigation"`
- `"System Outage Postmortem"`

#### `severity` (string)
Impact level: `"low"`, `"medium"`, `"high"`, or `"critical"` (all lowercase)

**Guidelines**:
- **critical**: Major financial loss, data breach, complete service outage
- **high**: Significant user-facing disruption, core business function impaired
- **medium**: Internal system issues, moderate user inconvenience
- **low**: Cosmetic issues, isolated problems

#### `strategic_summary` (object)
Executive-focused summary with four sub-fields:

- `overview` (string): 2-3 sentence executive summary of what happened and current state
- `key_takeaways` (array of strings): 2-3 most important findings for leadership
- `business_implications` (string): Impact on business (revenue, trust, operations)
- `next_steps_summary` (string): High-level summary of next actions (not a task list)

#### `key_findings` (object)
Detailed findings with three sub-fields:

- `root_cause` (string): Root cause analysis or leading hypothesis
- `key_events` (array of strings): Chronological list of significant events
- `affected_systems` (array of strings): Impacted systems, services, or user groups

#### `metadata` (object)
Report metadata with two sub-fields:

- `reported_date` (string): When reported or detected (ISO 8601 format preferred)
- `tags` (array of strings): Categorization tags

## 🎨 Report Output

### HTML Report Features

Generated reports include:

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Glassmorphism UI**: Modern, professional appearance
- **Color-Coded Severity**: Visual indicators for severity levels
- **Priority Badges**: Action items show priority levels
- **Effort Indicators**: Recommendations show effort estimates
- **Print-Friendly**: Optimized for printing or PDF export
- **Self-Contained**: No external dependencies or CDN links

### Report Sections

1. **Header**: Title, severity badge, report type
2. **Strategic Summary**: Overview, key takeaways, business implications, next steps
3. **Key Findings**: Root cause, key events timeline, affected systems
4. **Metadata**: Reported date, categorization tags

### File Location

Reports are saved to: `output/reports/{report_type}_{timestamp}.html`

**Example**: `output/reports/incident_analysis_20251016_143022.html`

## 💡 Best Practices

### Content Analysis

1. **Be Specific**: Extract concrete facts and data points
2. **Assess Accurately**: Base severity on actual business impact
3. **Stay Objective**: Separate facts from assumptions
4. **Focus on Action**: Provide clear, actionable recommendations

### Writing Guidelines

1. **Strategic Summary**: Make it understandable by non-technical leaders in 30 seconds
2. **Key Takeaways**: Focus on business impact and critical insights (2-3 items max)
3. **Key Events**: Use chronological order with timestamps when available
4. **Root Cause**: Explain in simple terms that non-technical stakeholders can understand

### Common Pitfalls

❌ **Don't**:
- Use vague language ("might be", "could be")
- Miss required JSON fields
- Over-inflate or under-assess severity
- Write overly technical summaries for executives
- Include too many key takeaways (keep to 2-3)

✅ **Do**:
- Use concrete, specific language
- Fill all required JSON fields
- Assess severity based on business impact
- Write strategic summaries for C-level understanding
- Focus on business implications and outcomes

## 🔧 Configuration

### Settings

Report Generator settings are in `configs/report.py`:

```python
class ReportConfig:
    # Enable/disable tool
    ENABLE_REPORT_GENERATOR: bool = True
    
    # Output directory
    REPORT_OUTPUT_DIR: Path = OUTPUT_DIR / "reports"
    
    # Templates directory
    REPORT_TEMPLATES_DIR: Path = BASE_DIR / "src/tools/report/templates"
    
    # Max content length (characters)
    REPORT_MAX_CONTENT_LENGTH: int = 50000
    
    # Enable JSON validation
    REPORT_VALIDATE_JSON: bool = True
    
    # Report format
    REPORT_DEFAULT_FORMAT: str = "html"
```

### Environment Variables

Override settings via environment variables:

```bash
# Disable report generator
export ENABLE_REPORT_GENERATOR=false

# Change max content length
export REPORT_MAX_CONTENT_LENGTH=100000

# Disable JSON validation (not recommended)
export REPORT_VALIDATE_JSON=false
```

## 📝 Examples

### Example 1: Slack Incident Thread

**Input**:
```json
{
  "input_data": {
    "content": "@channel Production alert! Payment service is down. Users can't complete purchases. Started at 10:45 AM. DevOps investigating.\n\nUpdate: Found the issue. Redis cache expired and service didn't handle it gracefully. Deploying fix now.\n\nResolved: Fix deployed at 11:20 AM. Payments working again. Will do full postmortem tomorrow.",
    "source_type": "slack",
    "context": "Production incident from #alerts channel"
  }
}
```

**Generated Report**: Incident analysis with:
- Strategic summary focused on business impact (35 minutes of payment downtime)
- Key events timeline (10:45 alert, 11:00 root cause identified, 11:20 resolved)
- Root cause: Redis cache expiration without graceful degradation
- Affected systems: Payment service, checkout flow
- Next steps: Full postmortem scheduled

### Example 2: JIRA Bug Report

**Input**:
```json
{
  "input_data": {
    "content": "Bug: Users can't upload files larger than 5MB. Error: 'Request Entity Too Large'. Steps: 1) Login 2) Go to upload page 3) Select 10MB file 4) Click upload. Expected: File uploads. Actual: Error message. Browser: Chrome 118. Affects: All users.",
    "source_type": "jira",
    "context": "Bug reported by customer support"
  }
}
```

**Generated Report**: Bug analysis with:
- Strategic summary highlighting user experience impact
- Root cause: File size limit configuration (5MB cap)
- Key events: Bug discovery, user impact assessment
- Affected systems: File upload service, all user types
- Business implications: User frustration, potential data loss

### Example 3: Investigation Results

**Input**:
```json
{
  "input_data": {
    "content": "Security audit findings: 1) API keys in Git history (3 instances). 2) Missing rate limiting on public endpoints. 3) Old dependencies with known CVEs. Recommendations: Rotate all API keys, implement rate limiting, update dependencies.",
    "source_type": "investigation",
    "context": "Security audit completed 2025-10-15"
  }
}
```

**Generated Report**: Security analysis with:
- Critical severity assessment due to exposed credentials
- Strategic summary of security risks and business exposure
- Key findings: 3 exposed API keys, missing rate limiting, vulnerable dependencies
- Business implications: Potential data breach, API abuse risk
- Affected systems: Authentication service, public APIs, third-party integrations

## 🛠️ Troubleshooting

### Issue: "Missing required fields in JSON"

**Cause**: The JSON response is missing one or more required fields.

**Solution**: Ensure your JSON includes all required fields:
- `report_title`, `report_type`, `severity`
- `strategic_summary` (with `overview`, `key_takeaways`, `business_implications`, `next_steps_summary`)
- `key_findings` (with `root_cause`, `key_events`, `affected_systems`)
- `metadata` (with `reported_date`, `tags`)

### Issue: "Content length exceeds maximum"

**Cause**: Input content is too long (default: 50,000 characters).

**Solution**: 
- Summarize the content before submitting
- Increase `REPORT_MAX_CONTENT_LENGTH` in config
- Split into multiple reports

### Issue: "Template file not found"

**Cause**: Template files are missing from `src/tools/report/templates/`.

**Solution**: Verify these files exist:
- `report_template.html`
- `report_styles.css`
- `report_script.js`

### Issue: Invalid JSON format

**Cause**: JSON response has syntax errors or incorrect structure.

**Solution**:
- Validate JSON using a JSON validator
- Check for missing commas, brackets, or quotes
- Ensure all strings are properly escaped

## 📚 Related Documentation

- [Sequential Thinking](sequential-thinking.md) - For analyzing complex incidents
- [Planning Tool](planning.md) - For creating remediation plans
- [Slack Tools](slack-tools.md) - For retrieving incident threads
- [Troubleshooting Guide](troubleshooting.md) - General troubleshooting

## 🔗 See Also

- **Example Reports**: Check `output/reports/` for generated examples
- **Templates**: Review `src/tools/report/templates/` for customization
- **Configuration**: See `configs/report.py` for all settings

---

**Need help?** Open an issue on [GitHub](https://github.com/HHC225/Local_MCP_Server/issues) or check the [Troubleshooting Guide](troubleshooting.md).
