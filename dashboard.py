"""Web dashboard for face recognition system."""
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from event_handler import EventHandler
from database import Database
from config import Config
import json

app = Flask(__name__)
CORS(app)

# Global instances
event_handler = None
database = None

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Recognition Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            margin: 0;
            font-size: 2em;
        }
        .stat-card p {
            margin: 5px 0 0 0;
        }
        .events {
            margin-top: 30px;
        }
        .event-item {
            background: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4CAF50;
            border-radius: 4px;
        }
        .event-item.alert {
            border-left-color: #f44336;
        }
        .event-item.track {
            border-left-color: #2196F3;
        }
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .refresh-btn:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Face Recognition Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3 id="total-faces">-</h3>
                <p>Total Faces</p>
            </div>
            <div class="stat-card">
                <h3 id="total-events">-</h3>
                <p>Total Events</p>
            </div>
            <div class="stat-card">
                <h3 id="alerts">-</h3>
                <p>Alerts</p>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="loadData()">Refresh</button>
        
        <div class="events">
            <h2>Recent Events</h2>
            <div id="events-list"></div>
        </div>
    </div>
    
    <script>
        function loadData() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-faces').textContent = data.total_faces;
                    document.getElementById('total-events').textContent = data.total_events;
                    document.getElementById('alerts').textContent = data.alerts;
                });
            
            fetch('/api/events?limit=20')
                .then(r => r.json())
                .then(events => {
                    const list = document.getElementById('events-list');
                    list.innerHTML = events.map(e => `
                        <div class="event-item ${e.type}">
                            <strong>${e.type.toUpperCase()}</strong> - ${new Date(e.timestamp).toLocaleString()}<br>
                            ${JSON.stringify(e.data, null, 2)}
                        </div>
                    `).join('');
                });
        }
        
        // Auto-refresh every 5 seconds
        setInterval(loadData, 5000);
        loadData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Dashboard homepage."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/stats')
def stats():
    """Get statistics."""
    total_faces = database.count_faces() if database else 0
    events = event_handler.get_events() if event_handler else []
    alerts = len([e for e in events if e['type'] == 'alert'])
    
    return jsonify({
        'total_faces': total_faces,
        'total_events': len(events),
        'alerts': alerts
    })

@app.route('/api/events')
def events():
    """Get events."""
    limit = request.args.get('limit', 100, type=int)
    event_type = request.args.get('type', None)
    
    if event_handler:
        events_list = event_handler.get_events(event_type=event_type, limit=limit)
    else:
        events_list = []
    
    return jsonify(events_list)

@app.route('/api/faces')
def faces():
    """Get all faces in database."""
    if database:
        embeddings = database.get_all_embeddings()
        faces_list = [{'person_id': pid, 'person_name': name} for pid, name, _ in embeddings]
        # Remove duplicates
        seen = set()
        unique_faces = []
        for face in faces_list:
            key = face['person_id']
            if key not in seen:
                seen.add(key)
                unique_faces.append(face)
        return jsonify(unique_faces)
    return jsonify([])

def run_dashboard(port=5000, db=None, events=None):
    """Run the dashboard server."""
    global database, event_handler
    database = db
    event_handler = events
    app.run(host='0.0.0.0', port=port, debug=False)

