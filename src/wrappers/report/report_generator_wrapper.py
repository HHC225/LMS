"""
Report Generator Wrapper for MCP Registration
"""
from fastmcp import Context
from src.tools.report.report_generator_tool import ReportGeneratorTool, ReportInput

# Initialize tool instance
_report_generator_tool = ReportGeneratorTool()


async def generate_report(
    input_data: ReportInput,
    ctx: Context = None
) -> str:
    """
    Generate a comprehensive IT report from any input content.
    
    This tool analyzes the provided content and creates a structured, professional IT report
    in HTML format. The report includes strategic summary, key findings, and metadata.
    
    **CRITICAL: You must ALWAYS return your response in the EXACT JSON format specified below. 
    Do not deviate from this structure. No explanatory text before or after the JSON.**
    
    **REQUIRED JSON SCHEMA:**
    ```json
    {
      "report_title": "Clear, concise title summarizing the event",
      "report_type": "Type of report (e.g., Incident Analysis, Security Alert, System Outage Postmortem)",
      "severity": "Low | Medium | High | Critical",
      "strategic_summary": {
        "overview": "A 2-3 sentence executive summary. What happened and what is the current state?",
        "key_takeaways": [
          "The single most important finding or conclusion.",
          "Another critical piece of information a leader needs to know.",
          "More than a third key insight, if applicable."
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
      },
      "metrics": {
        "charts": [
          {
            "id": "unique-chart-id",
            "title": "Chart Title",
            "chartType": "line|bar|pie|doughnut|radar",
            "data": {
              "labels": ["Label1", "Label2", "Label3"],
              "datasets": [
                {
                  "label": "Dataset Name",
                  "values": [value1, value2, value3]
                }
              ]
            },
            "options": {}
          }
        ]
      }
    }
    ```
    
    **OPTIONAL - Metrics Field:**
    The "metrics" field is OPTIONAL and should only be included when the input content contains
    numerical data, trends, or measurable metrics.
    
    - **When to include**: Performance data, statistics, trends, time series, percentages, counts
    - **When to omit**: Pure text content with no numerical data
    - **Chart Types**:
      * "line": Time series data, trends over time
      * "bar": Comparisons between categories
      * "pie": Percentage distribution, composition (values should sum meaningfully)
      * "doughnut": Similar to pie chart, modern appearance
      * "radar": Multi-dimensional comparisons
    - **Multiple Charts**: You can include multiple charts in the "charts" array
    - **Multiple Datasets**: Each chart can have multiple datasets for comparison
    
    **REPORT GENERATION GUIDELINES:**
    
    1. **Synthesize, Don't Just List**: Your main task is analysis. Transform raw data (logs, messages) 
       into meaningful insights.
    
    2. **Focus on the 'So What?'**: Always answer the implicit question, "Why does this matter to the 
       business and its leaders?". The business_implications field is crucial.
    
    3. **Prioritize Clarity**: Use plain language. The key_takeaways should be understandable by a 
       non-technical CEO in 30 seconds.
    
    4. **Assess Severity Accurately**: Base severity on the actual or potential business impact.
       - **Critical**: Major financial loss, data breach, reputational damage, complete service outage.
       - **High**: Significant user-facing disruption, core business function impaired, risk of escalation.
       - **Medium**: Internal system issues, moderate user inconvenience with workarounds, minor performance degradation.
       - **Low**: Cosmetic issues, isolated problems, no significant business impact.
    
    5. **Maintain Objectivity**: Clearly state facts and separate them from hypotheses or assumptions.
    
    **INPUT CONTENT TYPES YOU MAY RECEIVE:**
    - **Slack Messages**: Team communications about issues or requests
    - **JIRA Tickets**: Bug reports, feature requests, or task descriptions
    - **Investigation Results**: Findings from technical investigations or audits
    - **Email Threads**: Customer complaints or internal discussions
    - **Meeting Notes**: Key decisions or issues from meetings
    - **Log Files**: Error logs or system monitoring data
    - **Support Tickets**: Customer reported issues
    
    **IMPORTANT NOTES:**
    - If information is missing or unclear, make reasonable assumptions and note them in the report
    - Always fill ALL fields in the JSON structure, even if you need to indicate "Not specified" or "Unknown"
    - Ensure the JSON is valid and properly formatted
    - Use markdown formatting within string values for better readability (e.g., **bold**, bullet points)
    - For timeline, use clear temporal markers if dates are not available
    
    **After you return the JSON, this tool will automatically:**
    1. Validate the JSON structure
    2. Generate a professional HTML report with glassmorphism design
    3. Save it to the output directory
    4. Return the file path
    
    **Remember: Your response must be ONLY the JSON object, nothing else.**

    **Very Important:** You must call html_builder tool after generating this JSON to create the final HTML report.
    
    Args:
        input_data: Universal report input containing the content to be analyzed
        ctx: MCP context for logging
        
    Returns:
        Instructions for the LLM to generate structured JSON, which will then be 
        automatically converted to an HTML report
    """
    return await _report_generator_tool.execute(
        input_data=input_data,
        ctx=ctx
    )
