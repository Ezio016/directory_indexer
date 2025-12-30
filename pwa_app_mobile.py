#!/usr/bin/env python3
"""
Directory Indexer - Mobile-Friendly PWA
With visual folder browser - no need to type paths!
"""

import os
import sys
import json
from pathlib import Path
import tempfile
import shutil

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, request, render_template_string, send_file, jsonify, send_from_directory
except ImportError:
    print("❌ Flask is not installed. Please run: pip3 install flask")
    sys.exit(1)

from directory_indexer import DirectoryIndexer

app = Flask(__name__, static_folder='app/static')

# Store temporary results
sessions = {}

# Get user's home directory
HOME_DIR = str(Path.home())

# HTML Template with mobile-friendly folder browser
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#667eea">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="DirIndex">
    
    <title>Directory Indexer</title>
    <link rel="manifest" href="/static/manifest.json">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
            touch-action: manipulation;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .app-icon {
            font-size: 48px;
            margin-bottom: 5px;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 5px;
            font-size: 1.8em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        
        .browser-section {
            margin-bottom: 20px;
        }
        
        .current-path {
            background: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            font-size: 0.85em;
            word-break: break-all;
            border: 2px solid #e0e0e0;
        }
        
        .current-path strong {
            color: #667eea;
        }
        
        .quick-paths {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .path-btn {
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            touch-action: manipulation;
        }
        
        .path-btn:active {
            transform: scale(0.95);
            background: #5568d3;
        }
        
        .folder-list {
            max-height: 300px;
            overflow-y: auto;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 15px;
            -webkit-overflow-scrolling: touch;
        }
        
        .folder-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            touch-action: manipulation;
            background: white;
            transition: background 0.2s;
        }
        
        .folder-item:active {
            background: #f0f0f0;
        }
        
        .folder-item:last-child {
            border-bottom: none;
        }
        
        .folder-icon {
            font-size: 24px;
        }
        
        .folder-name {
            flex: 1;
            font-weight: 500;
        }
        
        .nav-buttons {
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .nav-btn {
            flex: 1;
            padding: 12px;
            background: #666;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            touch-action: manipulation;
        }
        
        .nav-btn:active {
            background: #555;
        }
        
        .nav-btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        
        .index-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            touch-action: manipulation;
            margin-top: 10px;
        }
        
        .index-btn:active {
            transform: scale(0.98);
        }
        
        .index-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        #result {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        
        #result.show {
            display: block;
        }
        
        #result.error {
            background: #fee;
            color: #c00;
        }
        
        #result.success {
            background: #efe;
            color: #060;
        }
        
        .download-links {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        
        .download-btn {
            flex: 1;
            min-width: 100px;
            padding: 12px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border: 2px solid #667eea;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            display: block;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="app-icon">📁</div>
            <h1>Directory Indexer</h1>
            <p class="subtitle">Browse & index any folder</p>
        </div>
        
        <div class="browser-section">
            <div class="current-path">
                <strong>Current:</strong> <span id="currentPath">/</span>
            </div>
            
            <div class="quick-paths">
                <button class="path-btn" onclick="loadPath('/Users')">📱 Users</button>
                <button class="path-btn" onclick="loadPath('{{home}}')">🏠 Home</button>
                <button class="path-btn" onclick="loadPath('{{home}}/Documents')">📄 Documents</button>
                <button class="path-btn" onclick="loadPath('{{home}}/Desktop')">🖥️ Desktop</button>
            </div>
            
            <div class="nav-buttons">
                <button class="nav-btn" id="backBtn" onclick="goBack()">⬅️ Back</button>
                <button class="nav-btn" id="upBtn" onclick="goUp()">⬆️ Up</button>
            </div>
            
            <div class="folder-list" id="folderList">
                <div class="loading">Loading...</div>
            </div>
            
            <button class="index-btn" id="indexBtn" onclick="indexCurrentFolder()">
                🚀 Index This Folder
            </button>
        </div>
        
        <div id="result"></div>
    </div>
    
    <script>
        let currentPath = '{{home}}';
        let pathHistory = [];
        
        // Load initial path
        window.addEventListener('load', () => {
            loadPath(currentPath);
        });
        
        async function loadPath(path) {
            currentPath = path;
            document.getElementById('currentPath').textContent = path;
            document.getElementById('folderList').innerHTML = '<div class="loading">Loading...</div>';
            
            try {
                const response = await fetch('/browse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: path })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayFolders(data.items);
                } else {
                    document.getElementById('folderList').innerHTML = 
                        '<div class="loading">⚠️ ' + data.error + '</div>';
                }
            } catch (error) {
                document.getElementById('folderList').innerHTML = 
                    '<div class="loading">❌ Error loading folder</div>';
            }
        }
        
        function displayFolders(items) {
            const list = document.getElementById('folderList');
            
            if (items.length === 0) {
                list.innerHTML = '<div class="loading">📭 Empty folder</div>';
                return;
            }
            
            list.innerHTML = '';
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'folder-item';
                div.onclick = () => openItem(item);
                
                const icon = item.is_dir ? '📁' : '📄';
                div.innerHTML = `
                    <span class="folder-icon">${icon}</span>
                    <span class="folder-name">${item.name}</span>
                `;
                
                list.appendChild(div);
            });
        }
        
        function openItem(item) {
            if (item.is_dir) {
                pathHistory.push(currentPath);
                loadPath(item.path);
            }
        }
        
        function goBack() {
            if (pathHistory.length > 0) {
                const prevPath = pathHistory.pop();
                loadPath(prevPath);
            }
        }
        
        function goUp() {
            const parts = currentPath.split('/');
            if (parts.length > 2) {
                parts.pop();
                loadPath(parts.join('/'));
            }
        }
        
        async function indexCurrentFolder() {
            const btn = document.getElementById('indexBtn');
            const result = document.getElementById('result');
            
            btn.disabled = true;
            btn.textContent = '⏳ Indexing...';
            result.className = '';
            result.innerHTML = '';
            
            try {
                const response = await fetch('/index', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dirPath: currentPath })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    result.className = 'show success';
                    result.innerHTML = `
                        <h3>✅ Success!</h3>
                        <p><strong>Found ${data.item_count} items</strong></p>
                        <p>Folder: <strong>${data.output_dir}</strong></p>
                        <div class="download-links">
                            ${data.files.json ? '<a href="/download?type=json&session=' + data.session + '" class="download-btn">📄 JSON</a>' : ''}
                            ${data.files.xml ? '<a href="/download?type=xml&session=' + data.session + '" class="download-btn">📄 XML</a>' : ''}
                            ${data.files.txt ? '<a href="/download?type=txt&session=' + data.session + '" class="download-btn">📄 TXT</a>' : ''}
                        </div>
                    `;
                } else {
                    result.className = 'show error';
                    result.innerHTML = `<h3>❌ Error</h3><p>${data.error}</p>`;
                }
            } catch (error) {
                result.className = 'show error';
                result.innerHTML = `<h3>❌ Error</h3><p>${error.message}</p>`;
            } finally {
                btn.disabled = false;
                btn.textContent = '🚀 Index This Folder';
            }
        }
        
        // Service Worker registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .catch(err => console.log('SW registration failed'));
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, home=HOME_DIR)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('app/static', filename)

@app.route('/browse', methods=['POST'])
def browse():
    try:
        data = request.get_json()
        path = data.get('path', HOME_DIR)
        
        if not os.path.exists(path):
            return jsonify({'success': False, 'error': 'Path does not exist'})
        
        if not os.path.isdir(path):
            return jsonify({'success': False, 'error': 'Not a directory'})
        
        items = []
        try:
            entries = sorted(Path(path).iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for entry in entries:
                if entry.name.startswith('.'):
                    continue
                    
                items.append({
                    'name': entry.name,
                    'path': str(entry),
                    'is_dir': entry.is_dir()
                })
        except PermissionError:
            return jsonify({'success': False, 'error': 'Permission denied'})
        
        return jsonify({'success': True, 'items': items})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/index', methods=['POST'])
def index_directory():
    try:
        data = request.get_json()
        dir_path = data.get('dirPath')
        
        if not dir_path or not os.path.exists(dir_path):
            return jsonify({'success': False, 'error': 'Invalid directory path'})
        
        # Create temporary directory for output
        temp_dir = tempfile.mkdtemp()
        session_id = os.path.basename(temp_dir)
        
        # Index the directory
        indexer = DirectoryIndexer(dir_path)
        indexer.process(
            json_output=True,
            xml_output=True,
            txt_output=True,
            output_base_dir=temp_dir,
            auto_open=False
        )
        
        # Find the output directory
        folder_name = Path(dir_path).name
        output_dir = os.path.join(temp_dir, f"Items_in_{folder_name}")
        
        # Store session info
        sessions[session_id] = {
            'output_dir': output_dir,
            'files': {
                'json': True,
                'xml': True,
                'txt': True
            }
        }
        
        item_count = indexer._count_items(indexer.hierarchy)
        
        return jsonify({
            'success': True,
            'session': session_id,
            'output_dir': f"Items_in_{folder_name}",
            'item_count': item_count,
            'files': {
                'json': True,
                'xml': True,
                'txt': True
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download')
def download():
    session_id = request.args.get('session')
    file_type = request.args.get('type')
    
    if session_id not in sessions:
        return 'Session not found', 404
    
    session = sessions[session_id]
    output_dir = session['output_dir']
    
    filename_map = {
        'json': 'directory_index.json',
        'xml': 'directory_index.xml',
        'txt': 'directory_index.txt'
    }
    
    if file_type not in filename_map:
        return 'Invalid file type', 400
    
    file_path = os.path.join(output_dir, filename_map[file_type])
    
    if not os.path.exists(file_path):
        return 'File not found', 404
    
    return send_file(file_path, as_attachment=True, download_name=filename_map[file_type])

if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    
    print("🚀 Starting Directory Indexer PWA (Mobile-Friendly)")
    print("=" * 60)
    print("📱 MOBILE-OPTIMIZED - Visual folder browser!")
    print("=" * 60)
    print("\n📱 Access from:")
    print(f"   🏷️  Hostname: http://{hostname}:8080")
    print("   🔢 Local: http://127.0.0.1:8080")
    print("\n✨ Features:")
    print("   • Visual folder browser (no typing paths!)")
    print("   • Touch-optimized interface")
    print("   • Works on iPhone, iPad, Android")
    print("   • Install as app")
    print("\n📱 On iPhone/iPad:")
    print("   1. Open Safari")
    print(f"   2. Go to: http://{hostname}:8080")
    print("   3. Browse folders visually")
    print("   4. Tap folder to open, tap 'Index' to process")
    print("   5. Add to Home Screen for app experience")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

