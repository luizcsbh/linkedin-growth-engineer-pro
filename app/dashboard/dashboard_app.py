from flask import Flask, render_template, jsonify
from app.analytics.database import DatabaseManager
from app.core.config import Config
import pandas as pd

app = Flask(__name__)
db = DatabaseManager()

@app.route('/')
def index():
    # Get recent metrics
    metrics = db.get_recent_metrics(7)
    
    # Calculate current scores
    if metrics:
        latest = metrics[0]
        growth_score = latest[2]
        ssi_score = latest[3]
        consistency = latest[4]
    else:
        growth_score = 0
        ssi_score = 0
        consistency = 0
        
    # Get efficiency per action
    weights = db.get_engagement_weights()
    
    # Get recent detailed actions
    recent_actions = db.get_recent_actions(20)
    
    # Get specific reports for Likes and Jobs
    likes_report = db.get_recent_actions(15, action_types=['post_like'])
    jobs_report = db.get_recent_actions(15, action_types=['jobs_view'])
    
    # Get stats for Likes and Jobs
    action_stats = db.get_action_stats(['post_like', 'jobs_view'])
    stats_dict = {row[0]: {'total': row[1], 'php': row[2]} for row in action_stats}
    
    return render_template('index.html', 
                           growth_score=growth_score, 
                           ssi_score=ssi_score, 
                           consistency=consistency,
                           weights=weights,
                           recent_actions=recent_actions,
                           likes_report=likes_report,
                           jobs_report=jobs_report,
                           stats=stats_dict)

@app.route('/api/metrics')
def get_metrics():
    metrics = db.get_recent_metrics(7)
    # Reverse to show chronological order in chart
    metrics.reverse()
    
    data = {
        'labels': [m[1] for m in metrics],
        'growth_scores': [m[2] for m in metrics],
        'ssi_scores': [m[3] for m in metrics],
        'activity_counts': [m[5] for m in metrics]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.DASHBOARD_PORT)
