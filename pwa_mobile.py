#!/usr/bin/env python3
"""
Directory Indexer - Mobile-Optimized PWA with Visual Directory Browser
Works on iPhone, iPad, Android with touch-friendly interface
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

# Default base paths for browsing (configure these for your system)
BASE_PATHS = [
    str(Path.home()),
    str(Path.home() / "Documents"),
    str(Path.home() / "Desktop"),
    str(Path.home() / "Downloads"),
    "/Users",
]

# Mobile-optimized HTML with directory browser
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
            -webkit-tap-highlight-color: rgba(0,0,0,0);
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .app-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 8px;
            font-size: 1.8em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .tab {
            flex: 1;
            padding: 15px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            color: #666;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Directory Browser */
        .browser {
            margin-bottom: 20px;
        }
        
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow-x: auto;
            white-space: nowrap;
        }
        
        .breadcrumb-item {
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
            padding: 4px 8px;
            border-radius: 4px;
            background: white;
            min-width: fit-content;
        }
        
        .breadcrumb-item:active {
            background: #e0e0e0;
        }
        
        .directory-list {
            max-height: 400px;
            overflow-y: auto;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
        }
        
        .directory-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            border-bottom: 1px solid #f0f0f0;
            cursor: pointer;
            transition: background 0.2s;
            min-height: 60px;
        }
        
        .directory-item:active {
            background: #f8f9fa;
        }
        
        .directory-item:last-child {
            border-bottom: none;
        }
        
        .directory-icon {
            font-size: 32px;
            min-width: 32px;
        }
        
        .directory-info {
            flex: 1;
            min-width: 0;
        }
        
        .directory-name {
            font-weight: 600;
            color: #333;
            font-size: 16px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .directory-path {
            font-size: 12px;
            color: #999;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .select-btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            min-width: 80px;
        }
        
        .select-btn:active {
            background: #5568d3;
        }
        
        /* Manual Input */
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 8px;
            cursor: pointer;
            min-height: 48px;
        }
        
        .checkbox-item input[type="checkbox"] {
            width: 24px;
            height: 24px;
            cursor: pointer;
        }
        
        .checkbox-item label {
            margin: 0;
            cursor: pointer;
        }
        
        button.submit-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            min-height: 56px;
        }
        
        button.submit-btn:active {
            transform: scale(0.98);
        }
        
        button.submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        #result {
            margin-top: 20px;
            padding: 20px;
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
            flex-direction: column;
            gap: 12px;
            margin-top: 15px;
        }
        
        .download-btn {
            padding: 16px 20px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border: 2px solid #667eea;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s;
            min-height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .download-btn:active {
            background: #667eea;
            color: white;
        }
        
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #2196f3;
            font-size: 14px;
        }
        
        .info-box p {
            color: #1565c0;
            margin: 5px 0;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .selected-path {
            background: #e8f5e9;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            word-break: break-all;
            font-size: 14px;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="app-icon">📁</div>
            <h1>Directory Indexer</h1>
            <p class="subtitle">Create hierarchical numbering for directories</p>
        </div>
        
        <div class="info-box">
            <p><strong>📱 Touch-optimized</strong> for mobile devices</p>
            <p><strong>🔢 IP-style numbering:</strong> 1, 1.1, 1.1.1, etc.</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('browse')">📂 Browse</button>
            <button class="tab" onclick="switchTab('manual')">⌨️ Manual</button>
        </div>
        
        <div id="browseTab" class="tab-content active">
            <div class="browser">
                <div class="breadcrumb" id="breadcrumb"></div>
                <div class="directory-list" id="directoryList">
                    <div class="loading">
                        <div class="spinner"></div>
                        <div>Loading directories...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="manualTab" class="tab-content">
            <div class="input-group">
                <label for="dirPath">Directory Path</label>
                <input type="text" id="dirPath" name="dirPath" 
                       placeholder="/path/to/directory">
            </div>
        </div>
        
        <div id="selectedPathDisplay"></div>
        
        <div class="input-group">
            <label>Output Formats</label>
            <div class="checkbox-group">
                <div class="checkbox-item">
                    <input type="checkbox" id="jsonOutput" checked>
                    <label for="jsonOutput">JSON</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="xmlOutput" checked>
                    <label for="xmlOutput">XML</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="txtOutput" checked>
                    <label for="txtOutput">TXT</label>
                </div>
            </div>
        </div>
        
        <button class="submit-btn" id="submitBtn" onclick="generateIndex()">
            🚀 Generate Index
        </button>
        
        <div id="result"></div>
    </div>
    
    <script>
        let currentPath = '';
        let selectedPath = '';
        
        // Tab switching
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            
            if (tab === 'browse') {
                document.querySelector('.tab:first-child').classList.add('active');
                document.getElementById('browseTab').classList.add('active');
                if (!currentPath) loadDirectory('');
            } else {
                document.querySelector('.tab:last-child').classList.add('active');
                document.getElementById('manualTab').classList.add('active');
            }
        }
        
        // Load directory contents
        async function loadDirectory(path) {
            currentPath = path;
            const list = document.getElementById('directoryList');
            list.innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading...</div></div>';
            
            try {
                const response = await fetch('/browse?path=' + encodeURIComponent(path));
                const data = await response.json();
                
                if (!data.success) {
                    list.innerHTML = '<div style="padding: 20px; text-align: center; color: #c00;">' + data.error + '</div>';
                    return;
                }
                
                updateBreadcrumb(data.current_path, data.parents);
                renderDirectories(data.items, data.current_path);
            } catch (error) {
                list.innerHTML = '<div style="padding: 20px; text-align: center; color: #c00;">Error loading directory</div>';
            }
        }
        
        // Update breadcrumb
        function updateBreadcrumb(current, parents) {
            const breadcrumb = document.getElementById('breadcrumb');
            breadcrumb.innerHTML = '';
            
            // Add home
            const home = document.createElement('a');
            home.href = '#';
            home.className = 'breadcrumb-item';
            home.textContent = '🏠 Home';
            home.onclick = (e) => { e.preventDefault(); loadDirectory(''); };
            breadcrumb.appendChild(home);
            
            // Add parents
            parents.forEach(p => {
                const sep = document.createElement('span');
                sep.textContent = ' › ';
                sep.style.color = '#999';
                breadcrumb.appendChild(sep);
                
                const item = document.createElement('a');
                item.href = '#';
                item.className = 'breadcrumb-item';
                item.textContent = p.name;
                item.onclick = (e) => { e.preventDefault(); loadDirectory(p.path); };
                breadcrumb.appendChild(item);
            });
        }
        
        // Render directory items
        function renderDirectories(items, currentPath) {
            const list = document.getElementById('directoryList');
            
            if (items.length === 0) {
                list.innerHTML = '<div style="padding: 20px; text-align: center; color: #999;">No accessible directories</div>';
                return;
            }
            
            list.innerHTML = '';
            
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'directory-item';
                
                const icon = document.createElement('div');
                icon.className = 'directory-icon';
                icon.textContent = item.is_dir ? '📁' : '📄';
                div.appendChild(icon);
                
                const info = document.createElement('div');
                info.className = 'directory-info';
                
                const name = document.createElement('div');
                name.className = 'directory-name';
                name.textContent = item.name;
                info.appendChild(name);
                
                const path = document.createElement('div');
                path.className = 'directory-path';
                path.textContent = item.path;
                info.appendChild(path);
                
                div.appendChild(info);
                
                if (item.is_dir) {
                    const btn = document.createElement('button');
                    btn.className = 'select-btn';
                    btn.textContent = item.can_enter ? 'Open' : 'Select';
                    btn.onclick = (e) => {
                        e.stopPropagation();
                        if (item.can_enter) {
                            loadDirectory(item.path);
                        } else {
                            selectPath(item.path);
                        }
                    };
                    div.appendChild(btn);
                    
                    if (item.can_enter) {
                        div.onclick = () => loadDirectory(item.path);
                    }
                } else {
                    const btn = document.createElement('button');
                    btn.className = 'select-btn';
                    btn.textContent = 'Parent';
                    btn.onclick = (e) => {
                        e.stopPropagation();
                        selectPath(currentPath);
                    };
                    div.appendChild(btn);
                }
                
                list.appendChild(div);
            });
            
            // Add "Select This Folder" option at top if we're in a valid directory
            if (currentPath) {
                const selectThis = document.createElement('div');
                selectThis.className = 'directory-item';
                selectThis.style.background = '#f0f7ff';
                selectThis.style.borderBottom = '2px solid #667eea';
                
                const icon = document.createElement('div');
                icon.className = 'directory-icon';
                icon.textContent = '✅';
                selectThis.appendChild(icon);
                
                const info = document.createElement('div');
                info.className = 'directory-info';
                
                const name = document.createElement('div');
                name.className = 'directory-name';
                name.textContent = 'Select Current Folder';
                name.style.color = '#667eea';
                info.appendChild(name);
                
                const path = document.createElement('div');
                path.className = 'directory-path';
                path.textContent = currentPath;
                info.appendChild(path);
                
                selectThis.appendChild(info);
                
                const btn = document.createElement('button');
                btn.className = 'select-btn';
                btn.textContent = 'Select';
                btn.style.background = '#4caf50';
                btn.onclick = () => selectPath(currentPath);
                selectThis.appendChild(btn);
                
                list.insertBefore(selectThis, list.firstChild);
            }
        }
        
        // Select a path
        function selectPath(path) {
            selectedPath = path;
            document.getElementById('dirPath').value = path;
            document.getElementById('selectedPathDisplay').innerHTML = 
                '<div class="selected-path"><strong>✅ Selected:</strong><br>' + path + '</div>';
        }
        
        // Generate index
        async function generateIndex() {
            const btn = document.getElementById('submitBtn');
            const result = document.getElementById('result');
            let dirPath = document.getElementById('dirPath').value || selectedPath;
            
            if (!dirPath) {
                alert('Please select or enter a directory path');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '⏳ Processing...';
            result.className = '';
            result.innerHTML = '';
            
            try {
                const formData = new FormData();
                formData.append('dirPath', dirPath);
                formData.append('json', document.getElementById('jsonOutput').checked);
                formData.append('xml', document.getElementById('xmlOutput').checked);
                formData.append('txt', document.getElementById('txtOutput').checked);
                
                const response = await fetch('/index', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    result.className = 'show success';
                    result.innerHTML = `
                        <h3>✅ Success!</h3>
                        <p><strong>Found ${data.item_count} items</strong></p>
                        <p>Output: <strong>${data.output_dir}</strong></p>
                        <div class="download-links">
                            ${data.files.json ? '<a href="/download?type=json&session=' + data.session + '" class="download-btn">📄 Download JSON</a>' : ''}
                            ${data.files.xml ? '<a href="/download?type=xml&session=' + data.session + '" class="download-btn">📄 Download XML</a>' : ''}
                            ${data.files.txt ? '<a href="/download?type=txt&session=' + data.session + '" class="download-btn">📄 Download TXT</a>' : ''}
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
                btn.textContent = '🚀 Generate Index';
            }
        }
        
        // Load initial directory
        loadDirectory('');
        
        // Register Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('app/static', filename)

@app.route('/browse')
def browse_directory():
    """Browse directories with permission handling"""
    path = request.args.get('path', '')
    
    try:
        if not path:
            # Show base paths
            items = []
            for base_path in BASE_PATHS:
                if os.path.exists(base_path):
                    items.append({
                        'name': os.path.basename(base_path) or base_path,
                        'path': base_path,
                        'is_dir': True,
                        'can_enter': os.access(base_path, os.R_OK)
                    })
            return jsonify({
                'success': True,
                'current_path': '',
                'parents': [],
                'items': items
            })
        
        if not os.path.exists(path):
            return jsonify({'success': False, 'error': 'Path does not exist'})
        
        if not os.access(path, os.R_OK):
            return jsonify({'success': False, 'error': 'Permission denied'})
        
        # Get directory contents
        items = []
        try:
            entries = sorted(os.listdir(path))
            for entry in entries:
                if entry.startswith('.'):
                    continue
                
                full_path = os.path.join(path, entry)
                is_dir = os.path.isdir(full_path)
                can_enter = is_dir and os.access(full_path, os.R_OK)
                
                items.append({
                    'name': entry,
                    'path': full_path,
                    'is_dir': is_dir,
                    'can_enter': can_enter
                })
        except PermissionError:
            pass
        
        # Build breadcrumb
        parents = []
        current = Path(path)
        for parent in current.parents:
            if str(parent) == '/':
                break
            parents.insert(0, {
                'name': parent.name,
                'path': str(parent)
            })
        
        return jsonify({
            'success': True,
            'current_path': path,
            'parents': parents,
            'items': items
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/index', methods=['POST'])
def index_directory():
    try:
        dir_path = request.form.get('dirPath')
        json_output = request.form.get('json') == 'true'
        xml_output = request.form.get('xml') == 'true'
        txt_output = request.form.get('txt') == 'true'
        
        if not dir_path or not os.path.exists(dir_path):
            return jsonify({'success': False, 'error': 'Invalid directory path'})
        
        # Create temporary directory for output
        temp_dir = tempfile.mkdtemp()
        session_id = os.path.basename(temp_dir)
        
        # Index the directory
        indexer = DirectoryIndexer(dir_path)
        indexer.process(
            json_output=json_output,
            xml_output=xml_output,
            txt_output=txt_output,
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
                'json': json_output,
                'xml': xml_output,
                'txt': txt_output
            }
        }
        
        item_count = indexer._count_items(indexer.hierarchy)
        
        return jsonify({
            'success': True,
            'session': session_id,
            'output_dir': f"Items_in_{folder_name}",
            'item_count': item_count,
            'files': {
                'json': json_output,
                'xml': xml_output,
                'txt': txt_output
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
    
    print("🚀 Starting Mobile-Optimized Directory Indexer PWA")
    print("=" * 70)
    print("📱 MOBILE-FRIENDLY with Visual Directory Browser!")
    print("=" * 70)
    print("\n📱 Access from:")
    print(f"   🏷️  Hostname: http://{hostname}:8080")
    print("   🔢 Local: http://127.0.0.1:8080")
    print("\n💡 FEATURES:")
    print("   • Touch-optimized interface")
    print("   • Visual directory browser (no typing paths!)")
    print("   • Larger touch targets")
    print("   • Mobile-friendly design")
    print("   • Works on iPhone, iPad, Android")
    print("\n✨ Installation:")
    print("   iPhone/iPad: Safari → Share → Add to Home Screen")
    print("   Android: Chrome → Menu → Install App")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

