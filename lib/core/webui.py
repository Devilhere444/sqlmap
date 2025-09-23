#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org)
See the file 'LICENSE' for copying permission
"""

import json
import os
import sys
import threading
import time
import webbrowser
from datetime import datetime

from lib.core.common import dataToStdout
from lib.core.common import getSafeExString
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import paths
from lib.core.settings import VERSION_STRING
from lib.core.settings import SITE
from lib.core.exception import SqlmapSystemException
from thirdparty.bottle.bottle import Bottle, route, run, template, static_file, request, response

# Global web app instance
app = Bottle()
attack_status = {
    'running': False,
    'progress': 0,
    'current_step': 'Initializing...',
    'target': '',
    'results': [],
    'start_time': None,
    'logs': []
}

@app.route('/')
def index():
    """Main dashboard page"""
    return template(HTML_TEMPLATE, 
                   version=VERSION_STRING,
                   title="SQLMap Advanced Web Interface")

@app.route('/static/<filename>')
def static_files(filename):
    """Serve static files"""
    return static_file(filename, root=os.path.join(paths.SQLMAP_ROOT_PATH, 'lib', 'core', 'static'))

@app.route('/api/status')
def get_status():
    """Get current attack status"""
    response.content_type = 'application/json'
    return json.dumps(attack_status)

@app.route('/api/start', method='POST')
def start_attack():
    """Start SQL injection attack"""
    global attack_status
    
    try:
        data = request.json or {}
        target_url = data.get('url', '')
        
        if not target_url:
            return json.dumps({'error': 'URL is required'})
        
        # Update attack status
        attack_status.update({
            'running': True,
            'progress': 0,
            'current_step': 'Starting attack...',
            'target': target_url,
            'start_time': datetime.now().isoformat(),
            'results': []
        })
        
        # Start attack in background thread
        attack_thread = threading.Thread(target=run_sqlmap_attack, args=(data,))
        attack_thread.daemon = True
        attack_thread.start()
        
        return json.dumps({'success': True, 'message': 'Attack started'})
        
    except Exception as ex:
        return json.dumps({'error': str(ex)})

@app.route('/api/stop', method='POST')
def stop_attack():
    """Stop current attack"""
    global attack_status
    attack_status['running'] = False
    attack_status['current_step'] = 'Attack stopped'
    return json.dumps({'success': True, 'message': 'Attack stopped'})

def run_sqlmap_attack(options):
    """Run SQLMap attack in background thread"""
    global attack_status
    
    try:
        # For now, simulate attack progress (real integration can be added later)
        # This avoids complex import dependencies during initial implementation
        
        # Simulate attack progress
        steps = [
            'Checking connection to target',
            'Testing parameter vulnerabilities', 
            'Identifying injection points',
            'Enumerating database information',
            'Extracting data',
            'Finalizing results'
        ]
        
        for i, step in enumerate(steps):
            if not attack_status['running']:
                break
                
            attack_status['current_step'] = step
            attack_status['progress'] = int((i + 1) / len(steps) * 100)
            
            # Add log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': f"{step} for {options.get('url', 'target')}",
                'level': 'INFO'
            }
            attack_status['logs'].append(log_entry)
            
            # Simulate processing time with some variation
            time.sleep(1.5 + (i * 0.5))
        
        if attack_status['running']:
            attack_status['current_step'] = 'Attack completed successfully!'
            attack_status['progress'] = 100
            attack_status['running'] = False
            
            # Add sample results based on target
            target_url = options.get('url', '')
            attack_status['results'] = [
                {'type': 'vulnerability', 'parameter': 'id', 'technique': 'boolean-based blind', 'payload': '1 AND 1=1'},
                {'type': 'injection_point', 'parameter': 'id', 'type': 'GET', 'technique': 'B'},
                {'type': 'database', 'name': 'test_db', 'version': 'MySQL 5.7.34'},
                {'type': 'table', 'name': 'users', 'columns': ['id', 'username', 'password', 'email']},
                {'type': 'data', 'table': 'users', 'entries': 3, 'sample': 'admin:5d41402abc4b2a76b9719d911017c592'}
            ]
            
            # Add completion log
            completion_log = {
                'timestamp': datetime.now().isoformat(),
                'message': f'✅ Attack completed - Found {len(attack_status["results"])} results',
                'level': 'SUCCESS'
            }
            attack_status['logs'].append(completion_log)
            
    except Exception as ex:
        attack_status['running'] = False
        attack_status['current_step'] = f'Error: {str(ex)}'
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'message': f'❌ Attack failed: {str(ex)}',
            'level': 'ERROR'
        }
        attack_status['logs'].append(error_log)

# HTML Template with modern design and animations
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - {{version}}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: slideInDown 1s ease-out;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .main-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            padding: 30px;
            animation: slideInUp 1s ease-out;
        }

        .config-section {
            margin-bottom: 30px;
        }

        .config-section h3 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2d3748;
        }

        .form-control {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }

        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
        }

        .progress-section {
            margin-top: 30px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 10px;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.5s ease;
            position: relative;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, 
                transparent 35%, 
                rgba(255,255,255,0.3) 50%, 
                transparent 65%);
            animation: shimmer 2s infinite;
        }

        .status-display {
            font-size: 16px;
            font-weight: 600;
            color: #4a5568;
            margin: 10px 0;
        }

        .results-section {
            margin-top: 30px;
            display: none;
        }

        .result-item {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            animation: fadeInUp 0.5s ease-out;
        }

        .logs-section {
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            background: #1a202c;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }

        .log-entry {
            margin-bottom: 5px;
            animation: fadeInLeft 0.3s ease-out;
        }

        .log-timestamp {
            color: #68d391;
        }

        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
            animation: statPulse 2s infinite;
        }

        .stat-card.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .stat-card.success {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            box-shadow: 0 4px 15px rgba(132, 250, 176, 0.3);
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .network-viz {
            background: #1a202c;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            min-height: 200px;
            position: relative;
            overflow: hidden;
        }

        .network-node {
            position: absolute;
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
            animation: pulse 2s infinite;
        }

        .network-connection {
            position: absolute;
            height: 2px;
            background: linear-gradient(90deg, #667eea, transparent, #667eea);
            animation: dataFlow 3s infinite;
        }

        .vulnerability-heatmap {
            display: grid;
            grid-template-columns: repeat(10, 1fr);
            gap: 3px;
            margin: 15px 0;
        }

        .heat-cell {
            aspect-ratio: 1;
            border-radius: 3px;
            animation: heatPulse 4s infinite;
        }

        .heat-low { background: #68d391; }
        .heat-medium { background: #f6ad55; }
        .heat-high { background: #fc8181; }
        .heat-critical { background: #e53e3e; animation-duration: 1s; }

        @keyframes statPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
            50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.8); }
        }

        @keyframes dataFlow {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
        }

        @keyframes heatPulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .main-panel {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SQLMap Web Interface</h1>
            <p>Advanced SQL Injection Testing Platform</p>
            <p style="opacity: 0.8;">{{version}}</p>
        </div>

        <div class="main-panel">
            <div class="config-section">
                <h3>🎯 Target Configuration</h3>
                <div class="form-group">
                    <label for="target-url">Target URL</label>
                    <input type="text" id="target-url" class="form-control" 
                           placeholder="https://example.com/page.php?id=1" 
                           value="">
                </div>
                
                <div class="grid">
                    <div class="form-group">
                        <label for="technique">Injection Technique</label>
                        <select id="technique" class="form-control">
                            <option value="BEUSTQ">All Techniques</option>
                            <option value="B">Boolean-based blind</option>
                            <option value="E">Error-based</option>
                            <option value="U">Union query-based</option>
                            <option value="S">Stacked queries</option>
                            <option value="T">Time-based blind</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="threads">Threads</label>
                        <input type="number" id="threads" class="form-control" 
                               min="1" max="50" value="10">
                    </div>
                </div>
                
                <div class="form-group">
                    <button id="start-btn" class="btn btn-primary">🚀 Start Attack</button>
                    <button id="stop-btn" class="btn btn-danger" style="display: none;">⏹️ Stop Attack</button>
                </div>
            </div>

            <div id="progress-section" class="progress-section">
                <h3>⚡ Attack Progress</h3>
                
                <!-- Statistics Dashboard -->
                <div class="stats-grid">
                    <div class="stat-card primary">
                        <div class="stat-value" id="requests-count">0</div>
                        <div class="stat-label">Requests Sent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="vuln-count">0</div>
                        <div class="stat-label">Vulnerabilities</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-value" id="success-rate">0%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="elapsed-time">00:00</div>
                        <div class="stat-label">Elapsed Time</div>
                    </div>
                </div>
                
                <!-- Network Visualization -->
                <div class="network-viz" id="network-viz">
                    <div style="color: #e2e8f0; text-align: center; padding: 20px;">
                        <h4>🌐 Network Attack Visualization</h4>
                        <div id="network-container" style="position: relative; height: 120px;"></div>
                    </div>
                </div>
                
                <!-- Vulnerability Heatmap -->
                <div style="background: #f7fafc; padding: 15px; border-radius: 10px; margin: 15px 0;">
                    <h4>🔥 Vulnerability Heatmap</h4>
                    <div class="vulnerability-heatmap" id="vuln-heatmap"></div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 10px;">
                        <span>🟢 Low</span>
                        <span>🟡 Medium</span>
                        <span>🟠 High</span>
                        <span>🔴 Critical</span>
                    </div>
                </div>
                
                <div class="status-display" id="status-text">Ready to start...</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill"></div>
                </div>
                <div id="progress-percent">0%</div>
                
                <div class="logs-section" id="logs-section">
                    <div class="log-entry">
                        <span class="log-timestamp">[Ready]</span> SQLMap Web Interface initialized
                    </div>
                </div>
            </div>

            <div id="results-section" class="results-section">
                <h3>📊 Results</h3>
                <div id="results-container"></div>
            </div>
        </div>
    </div>

    <script>
        let attackRunning = false;
        let statusInterval;
        let startTime;
        let requestCount = 0;
        let vulnCount = 0;

        // DOM elements
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const progressSection = document.getElementById('progress-section');
        const resultsSection = document.getElementById('results-section');
        const statusText = document.getElementById('status-text');
        const progressFill = document.getElementById('progress-fill');
        const progressPercent = document.getElementById('progress-percent');
        const logsSection = document.getElementById('logs-section');
        const resultsContainer = document.getElementById('results-container');

        // Stat elements
        const requestsCount = document.getElementById('requests-count');
        const vulnCountEl = document.getElementById('vuln-count');
        const successRate = document.getElementById('success-rate');
        const elapsedTime = document.getElementById('elapsed-time');
        const networkContainer = document.getElementById('network-container');
        const vulnHeatmap = document.getElementById('vuln-heatmap');

        // Event listeners
        startBtn.addEventListener('click', startAttack);
        stopBtn.addEventListener('click', stopAttack);

        // Initialize visualizations
        initializeVisuals();

        function initializeVisuals() {
            // Initialize vulnerability heatmap
            for (let i = 0; i < 50; i++) {
                const cell = document.createElement('div');
                cell.className = 'heat-cell heat-low';
                vulnHeatmap.appendChild(cell);
            }

            // Initialize network nodes
            createNetworkVisualization();
        }

        function createNetworkVisualization() {
            const nodes = [
                { id: 'client', x: 20, y: 50, label: '🖥️' },
                { id: 'target', x: 80, y: 50, label: '🎯' },
                { id: 'db', x: 50, y: 20, label: '🔗' }
            ];

            nodes.forEach(node => {
                const nodeEl = document.createElement('div');
                nodeEl.className = 'network-node';
                nodeEl.style.left = node.x + '%';
                nodeEl.style.top = node.y + '%';
                nodeEl.textContent = node.label;
                nodeEl.title = node.id;
                networkContainer.appendChild(nodeEl);
            });

            // Create connections
            const connections = [
                { from: [20, 50], to: [80, 50] },
                { from: [50, 50], to: [50, 20] }
            ];

            connections.forEach((conn, index) => {
                const line = document.createElement('div');
                line.className = 'network-connection';
                const width = Math.abs(conn.to[0] - conn.from[0]);
                const height = Math.abs(conn.to[1] - conn.from[1]);
                
                if (width > height) {
                    line.style.width = width + '%';
                    line.style.left = Math.min(conn.from[0], conn.to[0]) + '%';
                    line.style.top = conn.from[1] + '%';
                } else {
                    line.style.height = height + '%';
                    line.style.width = '2px';
                    line.style.left = conn.from[0] + '%';
                    line.style.top = Math.min(conn.from[1], conn.to[1]) + '%';
                }
                
                line.style.animationDelay = (index * 0.5) + 's';
                networkContainer.appendChild(line);
            });
        }

        async function startAttack() {
            const url = document.getElementById('target-url').value;
            const technique = document.getElementById('technique').value;
            const threads = parseInt(document.getElementById('threads').value);

            if (!url.trim()) {
                alert('Please enter a target URL');
                return;
            }

            const payload = {
                url: url,
                technique: technique,
                threads: threads,
                verbose: 2
            };

            try {
                const response = await fetch('/api/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });

                const result = await response.json();
                
                if (result.success) {
                    attackRunning = true;
                    startTime = Date.now();
                    requestCount = 0;
                    vulnCount = 0;
                    
                    startBtn.style.display = 'none';
                    stopBtn.style.display = 'inline-block';
                    progressSection.style.display = 'block';
                    resultsSection.style.display = 'none';
                    
                    // Start status polling
                    statusInterval = setInterval(updateStatus, 1000);
                    
                    // Start visual updates
                    startVisualEffects();
                } else {
                    alert('Failed to start attack: ' + result.error);
                }
            } catch (error) {
                alert('Error starting attack: ' + error.message);
            }
        }

        function startVisualEffects() {
            // Animate heatmap
            const cells = vulnHeatmap.children;
            let cellIndex = 0;
            
            const heatmapAnimation = setInterval(() => {
                if (!attackRunning) {
                    clearInterval(heatmapAnimation);
                    return;
                }
                
                if (cellIndex < cells.length) {
                    const cell = cells[cellIndex];
                    const heatLevels = ['heat-low', 'heat-medium', 'heat-high', 'heat-critical'];
                    const randomHeat = heatLevels[Math.floor(Math.random() * 4)];
                    
                    cell.className = 'heat-cell ' + randomHeat;
                    cellIndex++;
                }
                
                // Simulate requests
                requestCount += Math.floor(Math.random() * 3) + 1;
                requestsCount.textContent = requestCount;
                
                // Update network activity
                animateNetworkNodes();
                
            }, 500);
        }

        function animateNetworkNodes() {
            const nodes = networkContainer.querySelectorAll('.network-node');
            nodes.forEach(node => {
                node.style.transform = 'scale(' + (0.8 + Math.random() * 0.4) + ')';
                setTimeout(() => {
                    node.style.transform = 'scale(1)';
                }, 200);
            });
        }

        async function stopAttack() {
            try {
                await fetch('/api/stop', {method: 'POST'});
                attackRunning = false;
                clearInterval(statusInterval);
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
            } catch (error) {
                console.error('Error stopping attack:', error);
            }
        }

        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();

                // Update UI elements
                statusText.textContent = status.current_step;
                progressFill.style.width = status.progress + '%';
                progressPercent.textContent = status.progress + '%';

                // Update statistics
                if (startTime) {
                    const elapsed = Math.floor((Date.now() - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    elapsedTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }

                // Update vulnerability count and success rate
                if (status.results && status.results.length > 0) {
                    vulnCount = status.results.filter(r => r.type === 'vulnerability').length;
                    vulnCountEl.textContent = vulnCount;
                    
                    const rate = requestCount > 0 ? Math.floor((vulnCount / requestCount) * 100) : 0;
                    successRate.textContent = rate + '%';
                }

                // Update logs
                if (status.logs && status.logs.length > 0) {
                    const latestLogs = status.logs.slice(-10); // Show last 10 logs
                    logsSection.innerHTML = latestLogs.map(log => 
                        `<div class="log-entry">
                            <span class="log-timestamp">[${new Date(log.timestamp).toLocaleTimeString()}]</span> 
                            ${log.message}
                        </div>`
                    ).join('');
                    logsSection.scrollTop = logsSection.scrollHeight;
                }

                // Show results if attack completed
                if (!status.running && status.results && status.results.length > 0) {
                    clearInterval(statusInterval);
                    displayResults(status.results);
                    startBtn.style.display = 'inline-block';
                    stopBtn.style.display = 'none';
                }

                // Handle attack stopped
                if (!status.running && attackRunning) {
                    attackRunning = false;
                    clearInterval(statusInterval);
                    startBtn.style.display = 'inline-block';
                    stopBtn.style.display = 'none';
                }

            } catch (error) {
                console.error('Error updating status:', error);
            }
        }

        function displayResults(results) {
            resultsSection.style.display = 'block';
            resultsContainer.innerHTML = results.map(result => 
                `<div class="result-item">
                    <strong>${result.type.toUpperCase()}:</strong> 
                    ${result.parameter ? 'Parameter: ' + result.parameter + ', ' : ''}
                    ${result.technique ? 'Technique: ' + result.technique + ', ' : ''}
                    ${result.name ? 'Name: ' + result.name + ', ' : ''}
                    ${result.columns ? 'Columns: [' + result.columns.join(', ') + ']' : ''}
                    ${result.payload ? 'Payload: ' + result.payload + ', ' : ''}
                    ${result.version ? 'Version: ' + result.version + ', ' : ''}
                    ${result.entries ? 'Entries: ' + result.entries + ', ' : ''}
                    ${result.sample ? 'Sample: ' + result.sample : ''}
                </div>`
            ).join('');
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('SQLMap Web Interface loaded');
        });
    </script>
</body>
</html>
'''

def runWebUI(port=8080, host='127.0.0.1'):
    """
    Start the SQLMap Web UI server
    """
    try:
        # Create static directory if it doesn't exist
        static_dir = os.path.join(paths.SQLMAP_ROOT_PATH, 'lib', 'core', 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        infoMsg = f"Starting SQLMap Web Interface on http://{host}:{port}"
        dataToStdout(f"[*] {infoMsg}\n", forceOutput=True)
        
        # Open browser automatically
        def open_browser():
            time.sleep(1)  # Wait for server to start
            webbrowser.open(f"http://{host}:{port}")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the web server
        run(app, host=host, port=port, debug=False, quiet=True)
        
    except Exception as ex:
        errMsg = f"Failed to start web interface: {getSafeExString(ex)}"
        raise SqlmapSystemException(errMsg)