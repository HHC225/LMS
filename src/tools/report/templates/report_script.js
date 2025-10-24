document.addEventListener('DOMContentLoaded', function() {
    try {
        const dataElement = document.getElementById('reportData');
        const reportData = JSON.parse(dataElement.textContent);
        renderReport(reportData);
    } catch (error) {
        console.error('Failed to render report:', error);
    }
    document.getElementById('timestamp').textContent = new Date().toLocaleString();
});

// Convert markdown text to HTML
function parseMarkdown(text) {
    if (!text) return '';
    
    // **bold** -> <strong>bold</strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // *italic* -> <em>italic</em>
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // `code` -> <code>code</code>
    text = text.replace(/`(.+?)`/g, '<code>$1</code>');
    
    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

function renderReport(data) {
    // Header
    document.getElementById('report-type-badge').textContent = data.report_type;
    document.getElementById('report-title-heading').textContent = data.report_title;
    document.getElementById('reported-date-meta').textContent = new Date(data.metadata.reported_date).toLocaleDateString();

    // Key Takeaways - Apply markdown parsing
    const takeawaysList = document.getElementById('key-takeaways-list');
    takeawaysList.innerHTML = data.strategic_summary.key_takeaways.map(item => 
        `<li>${parseMarkdown(item)}</li>`
    ).join('');

    // Severity
    const severityCard = document.getElementById('severity-card');
    const severityText = document.getElementById('severity-text');
    severityText.textContent = data.severity;
    severityCard.classList.add(`severity-${data.severity}`);

    // Business Implications - Apply markdown parsing
    document.getElementById('business-implications-text').innerHTML = parseMarkdown(data.strategic_summary.business_implications);

    // Findings - Apply markdown parsing
    document.getElementById('root-cause-text').innerHTML = parseMarkdown(data.key_findings.root_cause);
    document.getElementById('next-steps-summary-text').innerHTML = parseMarkdown(data.strategic_summary.next_steps_summary);
    
    const affectedSystemsList = document.getElementById('affected-systems-list');
    affectedSystemsList.innerHTML = data.key_findings.affected_systems.map(item => 
        `<li>${parseMarkdown(item)}</li>`
    ).join('');

    // Key Events - Apply markdown parsing
    const keyEventsList = document.getElementById('key-events-list');
    keyEventsList.innerHTML = data.key_findings.key_events.map(event => 
        `<li>${parseMarkdown(event)}</li>`
    ).join('');
}