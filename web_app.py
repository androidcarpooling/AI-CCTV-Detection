"""Enhanced web application for face recognition system."""
import os
import json
import uuid
from flask import Flask, render_template_string, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from database import Database
from processor import FaceRecognitionProcessor
from event_handler import EventHandler
from config import Config
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv'}

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['RESULTS_FOLDER'], 'watchlist_photos']:
    os.makedirs(folder, exist_ok=True)

# Global instances
database = None
processor = None
event_handler = None
processing_jobs = {}  # Track processing jobs

def get_processor():
    """Get or create processor instance (lazy initialization)."""
    global processor, database
    if processor is None:
        try:
            print("Lazy loading processor and models...")
            if database is None:
                database = Database()
            processor = FaceRecognitionProcessor(database)
            print("Processor initialized successfully")
        except Exception as e:
            import traceback
            print(f"ERROR: Could not initialize processor: {e}")
            traceback.print_exc()
            raise
    return processor

def init_app():
    """Initialize application components."""
    global database, processor, event_handler
    try:
        print("Initializing database...")
        database = Database()
        print("Database initialized successfully")
        
        print("Initializing event handler...")
        event_handler = EventHandler()
        print("Event handler initialized successfully")
        
        # Don't initialize processor immediately - it loads heavy models
        # Will be initialized lazily on first use via get_processor()
        processor = None
        print("App initialization complete (processor will load on first use)")
    except Exception as e:
        import traceback
        print(f"ERROR: Could not initialize components: {e}")
        traceback.print_exc()
        # Will be initialized on first use

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI CCTV Face Recognition System</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .content {
            padding: 30px;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 30px;
        }
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }
        .tab.active {
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #f8f9fa;
            margin: 20px 0;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #e9ecef;
            border-color: #764ba2;
        }
        .upload-area.dragover {
            background: #e3f2fd;
            border-color: #2196F3;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            font-size: 2.5em;
            margin: 10px 0;
        }
        .stat-card p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .file-list {
            margin: 20px 0;
        }
        .file-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-item .file-info {
            flex: 1;
        }
        .file-item .file-name {
            font-weight: 600;
            color: #333;
        }
        .file-item .file-size {
            color: #666;
            font-size: 0.9em;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        .results {
            margin-top: 30px;
        }
        .result-item {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .result-item.match {
            border-left-color: #28a745;
            background: #d4edda;
        }
        .result-item.no-match {
            border-left-color: #dc3545;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .alert-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .video-preview {
            max-width: 100%;
            border-radius: 8px;
            margin: 10px 0;
        }
        input[type="file"] {
            display: none;
        }
        .file-input-label {
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .file-input-label:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎥 AI CCTV Face Recognition</h1>
            <p>Advanced face detection and recognition system</p>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('dashboard')">Dashboard</button>
                <button class="tab" onclick="switchTab('blacklist')">Blacklist Management</button>
                <button class="tab" onclick="switchTab('process')">Process Video</button>
                <button class="tab" onclick="switchTab('results')">Results</button>
            </div>
            
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <h2>System Overview</h2>
                <div class="stats">
                    <div class="stat-card">
                        <h3 id="total-faces">-</h3>
                        <p>Faces in Watchlist</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="total-events">-</h3>
                        <p>Total Events</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="alerts">-</h3>
                        <p>Alerts</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="processing-jobs">-</h3>
                        <p>Active Jobs</p>
                    </div>
                </div>
                <button class="btn" onclick="loadStats()">Refresh Stats</button>
                <div id="recent-events"></div>
            </div>
            
            <!-- Blacklist Management Tab -->
            <div id="blacklist" class="tab-content">
                <h2>Manage Blacklist</h2>
                <p>Upload photos to build your watchlist. Each photo should contain one person's face.</p>
                
                <div class="upload-area" id="blacklist-upload-area" 
                     ondrop="handleDrop(event, 'blacklist')" 
                     ondragover="handleDragOver(event)" 
                     ondragleave="handleDragLeave(event)">
                    <p style="font-size: 1.2em; margin-bottom: 15px;">📸 Drop photos here or click to upload</p>
                    <label for="blacklist-file-input" class="file-input-label">Choose Photos</label>
                    <input type="file" id="blacklist-file-input" multiple accept="image/*" 
                           onchange="handleFileSelect(event, 'blacklist')">
                </div>
                
                <div id="blacklist-files"></div>
                <button class="btn" onclick="buildWatchlist()" id="build-btn" disabled>Build Watchlist</button>
                <div id="blacklist-status"></div>
            </div>
            
            <!-- Process Video Tab -->
            <div id="process" class="tab-content">
                <h2>Process Video</h2>
                <p>Upload a video file or provide a local file path to process.</p>
                
                <div style="margin: 20px 0;">
                    <label><strong>Option 1: Upload Video</strong></label>
                    <div class="upload-area" id="video-upload-area"
                         ondrop="handleDrop(event, 'video')" 
                         ondragover="handleDragOver(event)" 
                         ondragleave="handleDragLeave(event)">
                        <p style="font-size: 1.2em; margin-bottom: 15px;">🎬 Drop video here or click to upload</p>
                        <label for="video-file-input" class="file-input-label">Choose Video</label>
                        <input type="file" id="video-file-input" accept="video/*" 
                               onchange="handleFileSelect(event, 'video')">
                    </div>
                </div>
                
                <div style="margin: 20px 0;">
                    <label><strong>Option 2: Local File Path</strong></label>
                    <input type="text" id="video-path" placeholder="/path/to/video.mp4" 
                           style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 6px; font-size: 16px;">
                </div>
                
                <div style="margin: 20px 0;">
                    <label><strong>Processing Options</strong></label>
                    <div style="margin: 10px 0;">
                        <label>Frame Rate (process every Nth frame):</label>
                        <input type="number" id="fps" value="30" min="1" max="60" 
                               style="padding: 8px; border: 2px solid #e0e0e0; border-radius: 6px; width: 100px; margin-left: 10px;">
                        <small style="color: #666; margin-left: 10px;">Higher = faster (less accurate), Lower = slower (more accurate)</small>
                    </div>
                    <div style="margin: 10px 0;">
                        <label>Similarity Threshold:</label>
                        <input type="number" id="threshold" value="0.35" min="0" max="1" step="0.05"
                               style="padding: 8px; border: 2px solid #e0e0e0; border-radius: 6px; width: 100px; margin-left: 10px;">
                    </div>
                    <div style="margin: 10px 0; padding: 10px; background: #fff3cd; border-radius: 6px;">
                        <strong>💡 Quick Test Mode:</strong> Set FPS to 30-60 for faster processing during testing/debugging
                    </div>
                </div>
                
                <div id="video-preview"></div>
                <button class="btn" onclick="processVideo()" id="process-btn" disabled>Process Video</button>
                <div id="process-status"></div>
                <div id="process-progress"></div>
            </div>
            
            <!-- Results Tab -->
            <div id="results" class="tab-content">
                <h2>Processing Results</h2>
                <div id="results-list"></div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedFiles = { blacklist: [], video: null };
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            if (tabName === 'dashboard') loadStats();
            if (tabName === 'results') loadResults();
        }
        
        function handleDragOver(e) {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        }
        
        function handleDragLeave(e) {
            e.currentTarget.classList.remove('dragover');
        }
        
        function handleDrop(e, type) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            if (type === 'blacklist') {
                selectedFiles.blacklist = files.filter(f => f.type.startsWith('image/'));
            } else {
                selectedFiles.video = files.find(f => f.type.startsWith('video/'));
            }
            updateFileDisplay(type);
        }
        
        function handleFileSelect(e, type) {
            const files = Array.from(e.target.files);
            if (type === 'blacklist') {
                selectedFiles.blacklist = files;
            } else {
                selectedFiles.video = files[0];
            }
            updateFileDisplay(type);
        }
        
        function updateFileDisplay(type) {
            const container = document.getElementById(type === 'blacklist' ? 'blacklist-files' : 'video-preview');
            container.innerHTML = '';
            
            if (type === 'blacklist') {
                selectedFiles.blacklist.forEach((file, i) => {
                    const div = document.createElement('div');
                    div.className = 'file-item';
                    div.innerHTML = `
                        <div class="file-info">
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
                        </div>
                        <button class="btn btn-secondary" onclick="removeFile(${i}, 'blacklist')">Remove</button>
                    `;
                    container.appendChild(div);
                });
                document.getElementById('build-btn').disabled = selectedFiles.blacklist.length === 0;
            } else {
                if (selectedFiles.video) {
                    const div = document.createElement('div');
                    div.innerHTML = `
                        <div class="file-item">
                            <div class="file-info">
                                <div class="file-name">${selectedFiles.video.name}</div>
                                <div class="file-size">${(selectedFiles.video.size / 1024 / 1024).toFixed(2)} MB</div>
                            </div>
                            <button class="btn btn-secondary" onclick="removeFile(0, 'video')">Remove</button>
                        </div>
                    `;
                    container.appendChild(div);
                    document.getElementById('process-btn').disabled = false;
                }
            }
        }
        
        function removeFile(index, type) {
            if (type === 'blacklist') {
                selectedFiles.blacklist.splice(index, 1);
            } else {
                selectedFiles.video = null;
            }
            updateFileDisplay(type);
        }
        
        async function buildWatchlist() {
            if (selectedFiles.blacklist.length === 0) return;
            
            const statusDiv = document.getElementById('blacklist-status');
            statusDiv.innerHTML = '<div class="alert alert-info">Uploading and processing photos...</div>';
            document.getElementById('build-btn').disabled = true;
            
            const formData = new FormData();
            selectedFiles.blacklist.forEach(file => {
                formData.append('photos', file);
            });
            
            try {
                const response = await fetch('/api/build-watchlist', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = `<div class="alert alert-success">✓ Successfully added ${result.count} faces to watchlist!</div>`;
                    selectedFiles.blacklist = [];
                    updateFileDisplay('blacklist');
                    loadStats();
                } else {
                    statusDiv.innerHTML = `<div class="alert alert-error">Error: ${result.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
            } finally {
                document.getElementById('build-btn').disabled = false;
            }
        }
        
        async function processVideo() {
            const statusDiv = document.getElementById('process-status');
            const progressDiv = document.getElementById('process-progress');
            document.getElementById('process-btn').disabled = true;
            
            const fps = parseInt(document.getElementById('fps').value) || 10;
            const threshold = parseFloat(document.getElementById('threshold').value) || 0.35;
            const videoPath = document.getElementById('video-path').value;
            
            const formData = new FormData();
            if (selectedFiles.video) {
                formData.append('video', selectedFiles.video);
            } else if (videoPath) {
                formData.append('video_path', videoPath);
            } else {
                statusDiv.innerHTML = '<div class="alert alert-error">Please upload a video or provide a file path</div>';
                document.getElementById('process-btn').disabled = false;
                return;
            }
            
            formData.append('fps', fps);
            formData.append('threshold', threshold);
            
            statusDiv.innerHTML = '<div class="alert alert-info">Starting video processing...</div>';
            progressDiv.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width: 10%">Starting...</div></div>';
            
            try {
                const response = await fetch('/api/process-video', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const jobId = result.job_id;
                    statusDiv.innerHTML = '<div class="alert alert-info">Processing video... This may take a while. <span class="loading"></span></div>';
                    
                    // Poll for job status
                    const pollInterval = setInterval(async () => {
                        try {
                            const statusResponse = await fetch(`/api/job-status/${jobId}`);
                            const jobStatus = await statusResponse.json();
                            
                            if (jobStatus.status === 'completed') {
                                clearInterval(pollInterval);
                                statusDiv.innerHTML = `<div class="alert alert-success">✓ Processing complete! Found ${jobStatus.matches || 0} matches. <a href="/api/download-results/${jobId}" class="btn">Download Results</a></div>`;
                                progressDiv.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width: 100%">100% Complete</div></div>';
                                loadResults();
                                loadStats();
                                document.getElementById('process-btn').disabled = false;
                            } else if (jobStatus.status === 'error') {
                                clearInterval(pollInterval);
                                statusDiv.innerHTML = `<div class="alert alert-error">Error: ${jobStatus.error || 'Processing failed'}</div>`;
                                progressDiv.innerHTML = '';
                                document.getElementById('process-btn').disabled = false;
                            } else {
                                // Update progress
                                const progress = jobStatus.progress || 0;
                                const message = jobStatus.message || 'Processing...';
                                const processed = jobStatus.processed_frames || 0;
                                const total = jobStatus.total_frames || 0;
                                let progressText = message;
                                if (total > 0) {
                                    progressText = `${message} (${processed}/${total} frames - ${progress}%)`;
                                }
                                progressDiv.innerHTML = `<div class="progress-bar"><div class="progress-fill" style="width: ${progress}%">${progressText}</div></div>`;
                            }
                        } catch (error) {
                            console.error('Error polling job status:', error);
                        }
                    }, 2000); // Poll every 2 seconds
                    
                    // Stop polling after 10 minutes
                    setTimeout(() => {
                        clearInterval(pollInterval);
                    }, 600000);
                    
                } else {
                    statusDiv.innerHTML = `<div class="alert alert-error">Error: ${result.error}</div>`;
                    progressDiv.innerHTML = '';
                    document.getElementById('process-btn').disabled = false;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="alert alert-error">Error: ${error.message}</div>`;
                progressDiv.innerHTML = '';
                document.getElementById('process-btn').disabled = false;
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('total-faces').textContent = data.total_faces;
                document.getElementById('total-events').textContent = data.total_events;
                document.getElementById('alerts').textContent = data.alerts;
                document.getElementById('processing-jobs').textContent = data.active_jobs;
                
                // Load recent events
                const eventsResponse = await fetch('/api/events?limit=10');
                const events = await eventsResponse.json();
                const eventsDiv = document.getElementById('recent-events');
                eventsDiv.innerHTML = '<h3 style="margin-top: 30px;">Recent Events</h3>';
                events.slice().reverse().forEach(event => {
                    const div = document.createElement('div');
                    div.className = `result-item ${event.type === 'alert' ? 'match' : ''}`;
                    div.innerHTML = `
                        <strong>${event.type.toUpperCase()}</strong> - ${new Date(event.timestamp).toLocaleString()}<br>
                        <pre style="margin-top: 10px; font-size: 0.9em;">${JSON.stringify(event.data, null, 2)}</pre>
                    `;
                    eventsDiv.appendChild(div);
                });
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadResults() {
            try {
                const response = await fetch('/api/results');
                const results = await response.json();
                const resultsDiv = document.getElementById('results-list');
                resultsDiv.innerHTML = '';
                
                if (results.length === 0) {
                    resultsDiv.innerHTML = '<p>No results yet. Process a video to see results here.</p>';
                    return;
                }
                
                results.forEach(result => {
                    const div = document.createElement('div');
                    div.className = 'result-item';
                    div.innerHTML = `
                        <h3>${result.filename || result.job_id}</h3>
                        <p><strong>Status:</strong> ${result.status}</p>
                        <p><strong>Matches Found:</strong> ${result.matches || 0}</p>
                        <p><strong>Total Detections:</strong> ${result.total_detections || 0}</p>
                        <p><strong>Processed:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
                        <a href="/api/download-results/${result.job_id}" class="btn">Download Results</a>
                    `;
                    resultsDiv.appendChild(div);
                });
            } catch (error) {
                console.error('Error loading results:', error);
            }
        }
        
        // Auto-refresh stats every 5 seconds
        setInterval(loadStats, 5000);
        
        // Initial load
        loadStats();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/health')
def health():
    """Health check endpoint for Railway."""
    return jsonify({
        'status': 'ok',
        'database': database is not None,
        'processor': processor is not None,
        'event_handler': event_handler is not None
    }), 200

@app.route('/api/stats')
def stats():
    """Get system statistics."""
    total_faces = database.count_faces() if database else 0
    events = event_handler.get_events() if event_handler else []
    alerts = len([e for e in events if e['type'] == 'alert'])
    active_jobs = len([j for j in processing_jobs.values() if j.get('status') == 'processing'])
    
    return jsonify({
        'total_faces': total_faces,
        'total_events': len(events),
        'alerts': alerts,
        'active_jobs': active_jobs
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

@app.route('/api/build-watchlist', methods=['POST'])
def build_watchlist_api():
    """Build watchlist from uploaded photos."""
    if 'photos' not in request.files:
        return jsonify({'success': False, 'error': 'No photos provided'}), 400
    
    files = request.files.getlist('photos')
    if not files or files[0].filename == '':
        return jsonify({'success': False, 'error': 'No files selected'}), 400
    
    saved_files = []
    try:
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join('watchlist_photos', filename)
                file.save(filepath)
                saved_files.append(filepath)
        
        if not saved_files:
            return jsonify({'success': False, 'error': 'No valid image files'}), 400
        
        # Build watchlist
        proc = get_processor()
        count = proc.build_watchlist('watchlist_photos', person_id_prefix='person')
        proc.matcher.invalidate_cache()
        
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process-video', methods=['POST'])
def process_video_api():
    """Process video file."""
    job_id = str(uuid.uuid4())
    processing_jobs[job_id] = {
        'status': 'processing', 
        'timestamp': time.time(),
        'progress': 0,
        'message': 'Initializing...'
    }
    
    try:
        fps = int(request.form.get('fps', 10))
        threshold = float(request.form.get('threshold', 0.35))
        
        video_path = None
        if 'video' in request.files:
            file = request.files['video']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(video_path)
        elif 'video_path' in request.form:
            video_path = request.form['video_path']
            if not os.path.exists(video_path):
                return jsonify({'success': False, 'error': 'Video file not found'}), 400
        
        if not video_path:
            return jsonify({'success': False, 'error': 'No video provided'}), 400
        
        # Update threshold if provided
        try:
            proc = get_processor()
            proc.matcher.threshold = threshold
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to initialize processor: {str(e)}'}), 500
        
        # Process in background thread
        def process():
            try:
                import cv2
                # Get video info for progress tracking
                cap = cv2.VideoCapture(video_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.isOpened() else 0
                cap.release()
                frames_to_process = total_frames // fps if fps > 0 else 0
                
                processing_jobs[job_id]['message'] = f'Processing video... (0/{frames_to_process} frames)'
                processing_jobs[job_id]['total_frames'] = frames_to_process
                processing_jobs[job_id]['processed_frames'] = 0
                
                output_file = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}.json')
                
                # Get processor (lazy load)
                proc = get_processor()
                
                # Process video with progress tracking
                results = []
                with VideoHandler(video_path, fps=fps) as video:
                    for frame_num, frame, timestamp in video.frames():
                        # Detect faces
                        faces = proc.detector.detect(frame)
                        proc.event_handler.detection(len(faces), source=video_path)
                        
                        for face_info in faces:
                            # Get embedding
                            embedding = proc.recognizer.get_embedding(frame, face_info['face'])
                            if embedding is None:
                                continue
                            
                            # Match against database
                            is_match, person_id, person_name, similarity = proc.matcher.is_match(embedding)
                            
                            result = {
                                'frame': frame_num,
                                'timestamp': timestamp,
                                'bbox': face_info['bbox'],
                                'det_score': face_info['det_score'],
                                'matched': is_match,
                                'person_id': person_id,
                                'person_name': person_name,
                                'similarity': similarity
                            }
                            
                            if is_match:
                                processor.event_handler.alert(person_id, person_name, similarity, metadata={'frame': frame_num})
                                processor.event_handler.track(person_id, person_name, location=video_path, frame_number=frame_num, timestamp=timestamp)
                            
                            results.append(result)
                        
                        # Update progress
                        processing_jobs[job_id]['processed_frames'] = frame_num
                        if frames_to_process > 0:
                            progress = min(90, int((frame_num / frames_to_process) * 90))  # Reserve 10% for finalization
                            processing_jobs[job_id]['progress'] = progress
                            processing_jobs[job_id]['message'] = f'Processing... ({frame_num}/{frames_to_process} frames)'
                
                # Save results
                import json
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                matches = len([r for r in results if r.get('matched', False)])
                processing_jobs[job_id] = {
                    'status': 'completed',
                    'matches': matches,
                    'total_detections': len(results),
                    'timestamp': time.time(),
                    'filename': os.path.basename(video_path),
                    'output_file': output_file,
                    'progress': 100,
                    'message': f'Completed: {matches} matches found in {len(results)} detections'
                }
            except Exception as e:
                import traceback
                error_msg = str(e)
                processing_jobs[job_id] = {
                    'status': 'error',
                    'error': error_msg,
                    'timestamp': time.time(),
                    'progress': 0,
                    'message': f'Error: {error_msg}'
                }
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Processing started',
            'status': 'processing'
        })
    except Exception as e:
        processing_jobs[job_id] = {
            'status': 'error', 
            'error': str(e),
            'timestamp': time.time()
        }
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/results')
def get_results():
    """Get all processing results."""
    results = []
    for job_id, job in processing_jobs.items():
        if job.get('status') in ['completed', 'error']:
            results.append({
                'job_id': job_id,
                **job
            })
    results.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    return jsonify(results)

@app.route('/api/job-status/<job_id>')
def job_status(job_id):
    """Get job processing status."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id].copy()
    return jsonify(job)

@app.route('/api/download-results/<job_id>')
def download_results(job_id):
    """Download results file."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id]
    if job.get('status') != 'completed':
        return jsonify({
            'error': 'Job not completed',
            'status': job.get('status'),
            'message': job.get('message', 'Processing in progress...')
        }), 400
    
    output_file = job.get('output_file')
    if not output_file or not os.path.exists(output_file):
        return jsonify({'error': 'Results file not found'}), 404
    
    return send_file(output_file, as_attachment=True, download_name=f'results_{job_id}.json')

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 500MB'}), 413

if __name__ == '__main__':
    try:
        print("=" * 50)
        print("Starting AI CCTV Face Recognition System")
        print("=" * 50)
        init_app()
        port = int(os.environ.get('PORT', 5000))
        print(f"Starting Flask server on 0.0.0.0:{port}")
        print(f"PORT environment variable: {os.environ.get('PORT', 'not set')}")
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except Exception as e:
        import traceback
        print(f"FATAL ERROR starting application: {e}")
        traceback.print_exc()
        raise

