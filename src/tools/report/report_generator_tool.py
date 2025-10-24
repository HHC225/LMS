"""
Report Generator Tool
Generates structured IT reports from raw content
"""
from typing import Dict, Any
from fastmcp import Context
from pydantic import BaseModel, Field

from src.tools.base import BaseTool
from configs.report import ReportConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportInput(BaseModel):
    """Universal input model for report generation"""
    content: str = Field(
        description="The raw input content that needs to be converted into a report. "
                   "This can be a Slack message, JIRA ticket, investigation results, "
                   "email thread, meeting notes, or any other IT-related content."
    )
    source_type: str = Field(
        default="general",
        description="Optional hint about the source type (e.g., 'slack', 'jira', 'email', 'investigation'). "
                   "This helps in better analysis but is not required."
    )
    context: str = Field(
        default="",
        description="Additional context or background information that might be helpful for generating the report."
    )


class ReportGeneratorTool(BaseTool):
    """
    Tool to generate structured IT reports from raw content
    """
    
    def __init__(self):
        super().__init__(
            name="generate_report",
            description="Generate comprehensive IT report from any input content"
        )
        self.config = ReportConfig
    
    async def execute(
        self,
        input_data: ReportInput,
        ctx: Context = None
    ) -> str:
        """
        Execute report generation
        
        Args:
            input_data: Universal report input containing the content to be analyzed
            ctx: MCP context for logging
            
        Returns:
            Detailed instructions with the actual content for LLM to analyze
        """
        try:
            await self.log_execution(ctx, f"Generating report for content type: {input_data.source_type}")
            
            # Validate content length
            if len(input_data.content) > self.config.REPORT_MAX_CONTENT_LENGTH:
                raise ValueError(
                    f"Content length ({len(input_data.content)}) exceeds maximum allowed "
                    f"({self.config.REPORT_MAX_CONTENT_LENGTH})"
                )
            
            # Build detailed analysis prompt with the actual content
            # The JSON schema is defined in the wrapper's docstring
            prompt = f"""📊 REPORT GENERATION REQUEST

**SOURCE TYPE:** {input_data.source_type}

**CONTENT TO ANALYZE:**
{input_data.content}

**ADDITIONAL CONTEXT:** {input_data.context if input_data.context else "None provided"}

---

🎯 **YOUR TASK:**
Analyze the above content and generate a comprehensive IT report following the EXACT JSON schema specified in the tool description.

⚠️ **CRITICAL REQUIREMENTS:**
1. Return ONLY the JSON object - no explanatory text before or after
2. Follow the exact schema with: report_title, report_type, severity, strategic_summary, key_findings, metadata
3. Use the Report Generation Guidelines from the tool description
4. Assess severity accurately based on business impact (Critical/High/Medium/Low)
5. Make the key_takeaways understandable to non-technical executives

📝 **IMPORTANT:**
- If information is missing, make reasonable assumptions
- Fill ALL required fields
- Use markdown formatting within strings (e.g., **bold**)
- strategic_summary must include: overview, key_takeaways, business_implications, next_steps_summary
- key_findings must include: root_cause, key_events, affected_systems

After you return the JSON, You must call build_report_from_json tool and create HTML report.

🚀 Generate the JSON now:"""
            
            logger.info(f"Analysis prompt prepared for {input_data.source_type} content ({len(input_data.content)} chars)")
            
            return prompt
            
        except Exception as e:
            error_msg = f"Error in report generation: {str(e)}"
            logger.error(error_msg)
            if ctx:
                await ctx.error(error_msg)
            return f"ERROR: {error_msg}"
