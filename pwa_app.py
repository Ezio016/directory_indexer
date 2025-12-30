#!/usr/bin/env python3
"""
Directory Indexer - Progressive Web App
Installable on ALL devices: iOS, Android, Mac, Windows, Linux
"""

import os
import sys
import json
from pathlib import Path
import tempfile
import shutil
import base64

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

# HTML Template with PWA support
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .app-icon {
            font-size: 64px;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 1.1em;
        }
        
        .install-prompt {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
            align-items: center;
            justify-content: space-between;
        }
        
        .install-prompt.show {
            display: flex;
        }
        
        .install-btn {
            background: white;
            color: #667eea;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
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
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .checkbox-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        button.submit-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button.submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        button.submit-btn:active {
            transform: translateY(0);
        }
        
        button.submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        #result {
            margin-top: 30px;
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
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .download-btn {
            flex: 1;
            min-width: 150px;
            padding: 12px 20px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border: 2px solid #667eea;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .download-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .info-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #2196f3;
        }
        
        .info-box p {
            color: #1565c0;
            margin: 5px 0;
        }
        
        .platform-info {
            text-align: center;
            margin-top: 20px;
            color: #999;
            font-size: 0.9em;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .app-icon {
                font-size: 48px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="app-icon">📁</div>
            <h1>Directory Indexer</h1>
            <p class="subtitle">Create hierarchical numbering for any directory</p>
        </div>
        
        <div class="install-prompt" id="installPrompt">
            <span>📲 Install this app for offline access!</span>
            <button class="install-btn" id="installButton">Install</button>
        </div>
        
        <div class="info-box">
            <p><strong>📱 Works on all devices:</strong> iPhone, iPad, Android, Mac, Windows, Linux</p>
            <p><strong>🔢 IP-style numbering:</strong> 1, 1.1, 1.1.1, etc.</p>
            <p><strong>💾 Installable:</strong> Add to home screen for app-like experience</p>
        </div>
        
        <form id="indexForm">
            <div class="input-group">
                <label for="dirPath">Directory Path</label>
                <input type="text" id="dirPath" name="dirPath" 
                       placeholder="/path/to/directory" required>
            </div>
            
            <div class="input-group">
                <label>Output Formats</label>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <input type="checkbox" id="jsonOutput" name="json" checked>
                        <label for="jsonOutput">JSON</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="xmlOutput" name="xml" checked>
                        <label for="xmlOutput">XML</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="txtOutput" name="txt" checked>
                        <label for="txtOutput">TXT</label>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">
                🚀 Generate Index
            </button>
        </form>
        
        <div id="result"></div>
        
        <div class="platform-info">
            <p>Running on: <span id="platformInfo"></span></p>
        </div>
    </div>
    
    <script>
        // PWA Installation
        let deferredPrompt;
        const installPrompt = document.getElementById('installPrompt');
        const installButton = document.getElementById('installButton');
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            installPrompt.classList.add('show');
        });
        
        installButton.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response: ${outcome}`);
                deferredPrompt = null;
                installPrompt.classList.remove('show');
            }
        });
        
        // Register Service Worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(reg => console.log('Service Worker registered'))
                .catch(err => console.log('Service Worker registration failed'));
        }
        
        // Platform detection
        const platformInfo = document.getElementById('platformInfo');
        const userAgent = navigator.userAgent;
        let platform = 'Unknown';
        
        if (/iPhone|iPad|iPod/.test(userAgent)) {
            platform = 'iOS';
        } else if (/Android/.test(userAgent)) {
            platform = 'Android';
        } else if (/Mac/.test(userAgent)) {
            platform = 'macOS';
        } else if (/Win/.test(userAgent)) {
            platform = 'Windows';
        } else if (/Linux/.test(userAgent)) {
            platform = 'Linux';
        }
        
        platformInfo.textContent = platform;
        
        // Form submission
        document.getElementById('indexForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = document.getElementById('submitBtn');
            const result = document.getElementById('result');
            const dirPath = document.getElementById('dirPath').value;
            
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
                        <p>Output folder: <strong>${data.output_dir}</strong></p>
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
        });
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
    
    print("🚀 Starting Directory Indexer PWA")
    print("=" * 60)
    print("📱 PROGRESSIVE WEB APP - Installable on ANY device!")
    print("=" * 60)
    print("\n📱 Access from:")
    print(f"   🏷️  Hostname: http://{hostname}:8080")
    print("   🔢 Local: http://127.0.0.1:8080")
    print("\n💡 INSTALLATION INSTRUCTIONS:")
    print("   iPhone/iPad: Open in Safari → Share → Add to Home Screen")
    print("   Android: Open in Chrome → Menu → Install App")
    print("   Desktop: Click install button in address bar")
    print("\n✨ Features:")
    print("   • Works offline after installation")
    print("   • Runs like a native app")
    print("   • No App Store required")
    print("   • Updates automatically")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)

