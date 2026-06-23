import os
from datetime import datetime
from jinja2 import Template
from storage import get_comments_by_source, get_sentiment_stats, get_top_comments, get_last_update_time

REPORTS_PATH = "reports"

def ensure_reports_dir():
    """Create reports directory if it doesn't exist"""
    os.makedirs(REPORTS_PATH, exist_ok=True)

def calculate_sentiment_breakdown():
    """Calculate sentiment counts for chart"""
    stats = get_sentiment_stats()

    breakdown = {
        'youtube': {'Positive': 0, 'Negative': 0, 'Neutral': 0},
        'x': {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    }

    for source, sentiment, count in stats:
        source_key = source.lower()
        if source_key in breakdown:
            breakdown[source_key][sentiment] = count

    return breakdown

def escape_html(text):
    """Escape HTML special characters"""
    if not text:
        return ""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def generate_html_report():
    """Generate HTML report with sentiment analysis"""
    ensure_reports_dir()

    breakdown = calculate_sentiment_breakdown()
    top_positive = get_top_comments('positive', 10)
    top_negative = get_top_comments('negative', 10)
    last_update = get_last_update_time()

    youtube_total = sum(breakdown['youtube'].values())
    x_total = sum(breakdown['x'].values())

    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }

        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }

        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }

        .sentiment-breakdown {
            display: flex;
            gap: 10px;
            justify-content: space-around;
            margin-top: 15px;
        }

        .sentiment-item {
            text-align: center;
            flex: 1;
        }

        .sentiment-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }

        .positive { color: #28a745; font-weight: bold; }
        .negative { color: #dc3545; font-weight: bold; }
        .neutral { color: #ffc107; font-weight: bold; }

        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            padding: 30px;
        }

        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .chart-container h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }

        .comments-section {
            padding: 30px;
            background: white;
        }

        .comments-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }

        .comments-column h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }

        .comment-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }

        .comment-card.positive {
            border-left-color: #28a745;
        }

        .comment-card.negative {
            border-left-color: #dc3545;
        }

        .comment-author {
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 8px;
        }

        .comment-text {
            color: #333;
            line-height: 1.5;
            margin-bottom: 8px;
            word-wrap: break-word;
        }

        .comment-meta {
            font-size: 0.85em;
            color: #999;
        }

        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }

        .timestamp {
            font-size: 0.9em;
            color: #999;
        }

        @media (max-width: 768px) {
            .charts-section {
                grid-template-columns: 1fr;
            }
            .comments-grid {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sentiment Analysis Report</h1>
            <p>Automated analysis from YouTube & X (Twitter)</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Comments Analyzed</h3>
                <div class="number">{{ total_comments }}</div>
            </div>

            <div class="stat-card">
                <h3>YouTube</h3>
                <div class="number">{{ youtube_total }}</div>
                <div class="sentiment-breakdown">
                    <div class="sentiment-item">
                        <div class="positive">{{ breakdown.youtube.Positive }}</div>
                        <div class="sentiment-label">Positive</div>
                    </div>
                    <div class="sentiment-item">
                        <div class="neutral">{{ breakdown.youtube.Neutral }}</div>
                        <div class="sentiment-label">Neutral</div>
                    </div>
                    <div class="sentiment-item">
                        <div class="negative">{{ breakdown.youtube.Negative }}</div>
                        <div class="sentiment-label">Negative</div>
                    </div>
                </div>
            </div>

            <div class="stat-card">
                <h3>X (Twitter)</h3>
                <div class="number">{{ x_total }}</div>
                <div class="sentiment-breakdown">
                    <div class="sentiment-item">
                        <div class="positive">{{ breakdown.x.Positive }}</div>
                        <div class="sentiment-label">Positive</div>
                    </div>
                    <div class="sentiment-item">
                        <div class="neutral">{{ breakdown.x.Neutral }}</div>
                        <div class="sentiment-label">Neutral</div>
                    </div>
                    <div class="sentiment-item">
                        <div class="negative">{{ breakdown.x.Negative }}</div>
                        <div class="sentiment-label">Negative</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="charts-section">
            <div class="chart-container">
                <h3>📈 YouTube Sentiment Distribution</h3>
                <canvas id="youtubeChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>📈 X (Twitter) Sentiment Distribution</h3>
                <canvas id="xChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>📊 YouTube vs X Comparison</h3>
                <canvas id="comparisonChart"></canvas>
            </div>
        </div>

        <div class="comments-section">
            <div class="comments-grid">
                <div class="comments-column">
                    <h3>💚 Top Positive Comments</h3>
                    {% for comment in top_positive %}
                    <div class="comment-card positive">
                        <div class="comment-author">{{ comment[1] }} ({{ comment[0] }})</div>
                        <div class="comment-text">{{ comment[2] }}</div>
                        <div class="comment-meta">Sentiment Score: {{ comment[3] }}</div>
                    </div>
                    {% endfor %}
                </div>

                <div class="comments-column">
                    <h3>❤️ Top Negative Comments</h3>
                    {% for comment in top_negative %}
                    <div class="comment-card negative">
                        <div class="comment-author">{{ comment[1] }} ({{ comment[0] }})</div>
                        <div class="comment-text">{{ comment[2] }}</div>
                        <div class="comment-meta">Sentiment Score: {{ comment[3] }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="timestamp">Last updated: {{ last_update }}</div>
            <div class="timestamp">Report generated with ❤️ by Sentiment Analyzer</div>
        </div>
    </div>

    <script>
        const chartOptions = {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        };

        new Chart(document.getElementById('youtubeChart'), {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [{{ breakdown.youtube.Positive }}, {{ breakdown.youtube.Neutral }}, {{ breakdown.youtube.Negative }}],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderColor: ['#1e7e34', '#ff9800', '#c82333'],
                    borderWidth: 2
                }]
            },
            options: chartOptions
        });

        new Chart(document.getElementById('xChart'), {
            type: 'doughnut',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [{{ breakdown.x.Positive }}, {{ breakdown.x.Neutral }}, {{ breakdown.x.Negative }}],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                    borderColor: ['#1e7e34', '#ff9800', '#c82333'],
                    borderWidth: 2
                }]
            },
            options: chartOptions
        });

        new Chart(document.getElementById('comparisonChart'), {
            type: 'bar',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [
                    {
                        label: 'YouTube',
                        data: [{{ breakdown.youtube.Positive }}, {{ breakdown.youtube.Neutral }}, {{ breakdown.youtube.Negative }}],
                        backgroundColor: '#667eea',
                        borderRadius: 4
                    },
                    {
                        label: 'X (Twitter)',
                        data: [{{ breakdown.x.Positive }}, {{ breakdown.x.Neutral }}, {{ breakdown.x.Negative }}],
                        backgroundColor: '#764ba2',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                ...chartOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });
    </script>
</body>
</html>'''

    template = Template(html_template)
    html_content = template.render(
        breakdown=breakdown,
        youtube_total=youtube_total,
        x_total=x_total,
        total_comments=youtube_total + x_total,
        top_positive=[
            (escape_html(c[0]), escape_html(c[1]), escape_html(c[2]), c[3])
            for c in top_positive
        ],
        top_negative=[
            (escape_html(c[0]), escape_html(c[1]), escape_html(c[2]), c[3])
            for c in top_negative
        ],
        last_update=last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else 'Never'
    )

    output_path = os.path.join(REPORTS_PATH, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Report generated: {output_path}")
    return output_path
