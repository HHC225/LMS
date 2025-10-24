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
    
    // Render charts if metrics exist
    if (data.metrics) {
        renderCharts(data.metrics);
    }
}

function renderCharts(metrics) {
    if (!metrics || !metrics.charts || metrics.charts.length === 0) {
        return; // No chart data
    }
    
    metrics.charts.forEach(chartConfig => {
        const ctx = document.getElementById(chartConfig.id);
        if (!ctx) {
            console.warn(`Canvas element not found: ${chartConfig.id}`);
            return;
        }
        
        // Transform datasets (values -> data)
        const datasets = chartConfig.data.datasets.map((dataset, index) => ({
            label: dataset.label,
            data: dataset.values,
            backgroundColor: getChartColors(chartConfig.chartType, index, chartConfig.data.labels.length),
            borderColor: getBorderColors(chartConfig.chartType, index, chartConfig.data.labels.length),
            borderWidth: 2,
            fill: chartConfig.chartType === 'line' ? false : true
        }));
        
        new Chart(ctx, {
            type: chartConfig.chartType,
            data: {
                labels: chartConfig.data.labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#e8e8e8'
                        }
                    }
                },
                scales: chartConfig.chartType !== 'pie' && chartConfig.chartType !== 'doughnut' && chartConfig.chartType !== 'radar' ? {
                    x: {
                        ticks: { color: '#b8b8b8' },
                        grid: { color: '#3a3a3a' }
                    },
                    y: {
                        ticks: { color: '#b8b8b8' },
                        grid: { color: '#3a3a3a' }
                    }
                } : {},
                ...(chartConfig.options || {})
            }
        });
    });
}

function getChartColors(chartType, index, labelCount) {
    const colorPalette = [
        'rgba(99, 102, 241, 0.8)',   // Indigo
        'rgba(16, 185, 129, 0.8)',   // Green
        'rgba(245, 158, 11, 0.8)',   // Amber
        'rgba(239, 68, 68, 0.8)',    // Red
        'rgba(139, 92, 246, 0.8)',   // Purple
        'rgba(59, 130, 246, 0.8)',   // Blue
        'rgba(236, 72, 153, 0.8)',   // Pink
        'rgba(34, 197, 94, 0.8)'     // Emerald
    ];
    
    if (chartType === 'pie' || chartType === 'doughnut') {
        return colorPalette.slice(0, labelCount);
    }
    return colorPalette[index % colorPalette.length];
}

function getBorderColors(chartType, index, labelCount) {
    const borderPalette = [
        'rgba(99, 102, 241, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(239, 68, 68, 1)',
        'rgba(139, 92, 246, 1)',
        'rgba(59, 130, 246, 1)',
        'rgba(236, 72, 153, 1)',
        'rgba(34, 197, 94, 1)'
    ];
    
    if (chartType === 'pie' || chartType === 'doughnut') {
        return borderPalette.slice(0, labelCount);
    }
    return borderPalette[index % borderPalette.length];
}