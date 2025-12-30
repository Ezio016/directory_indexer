# 📱 iOS/iPadOS Setup Guide

This guide shows you how to use the Directory Indexer on your iPhone 15 Pro and iPad A16.

## Option 1: Web Interface (Recommended) 🌐

The easiest way to use this on iOS devices is through the web interface.

### Setup on Your Mac:

1. **Install Flask** (only needed once):
   ```bash
   pip3 install flask
   ```

2. **Start the web server**:
   ```bash
   cd /path/to/DirHierarchy
   python3 web_server.py
   ```

3. **Find your Mac's IP address**:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Look for something like `192.168.1.XXX`

### Access from iPhone/iPad:

1. **Make sure both devices are on the same WiFi network**
2. **Open Safari** on your iPhone or iPad
3. **Go to**: `http://YOUR_MAC_IP:5000` (replace YOUR_MAC_IP with the IP from step 3)
4. **Enter the directory path** you want to index
5. **Click "Generate Index"**
6. **Download** the JSON, XML, or TXT files

### Features:
- ✅ Works on any iOS/iPadOS device
- ✅ Beautiful mobile-friendly interface
- ✅ Direct download to Files app
- ✅ No app installation needed

---

## Option 2: Pythonista App 🐍

If you want to run Python directly on iOS:

1. **Download Pythonista** from the App Store ($9.99)
2. **Copy `directory_indexer.py`** to your iPad/iPhone via:
   - iCloud Drive
   - AirDrop
   - iTunes File Sharing
3. **Open the script in Pythonista**
4. **Run it** and provide the directory path

Note: File system access is limited on iOS, so you can only index directories in:
- Pythonista's sandbox
- iCloud Drive (with permissions)
- Files app locations you have access to

---

## Option 3: a-Shell (Free) 📱

a-Shell is a free terminal emulator for iOS with Python support:

1. **Download a-Shell** from the App Store (Free)
2. **Transfer the script** via Files app to a-Shell's directory
3. **Run**: `python directory_indexer.py /path/to/folder`

---

## Option 4: Cloud Solution ☁️

### Using Shortcuts + Cloud Storage:

1. **Save files to iCloud Drive** on your Mac
2. **Create an iOS Shortcut** that:
   - Gets file path from Files app
   - Sends to your Mac via API/SSH
   - Retrieves results from shared folder

---

## Recommended Workflow

**For iPhone 15 Pro & iPad A16:**

1. **Start web server on Mac** (one time when you need it)
2. **Access from Safari** on your iOS device
3. **Browse directories** in Files app to find paths
4. **Paste path** into web interface
5. **Download results** directly to Files app

This gives you full desktop functionality from any iOS device!

---

## Tips

- **Bookmark the web interface** in Safari for quick access
- **Use iCloud Drive paths** for easy cross-device access
- **Share the server** with other devices on your network
- **Run server in background** on Mac for always-available access

---

## Troubleshooting

### Can't connect from iPhone/iPad:
- Make sure both devices are on the same WiFi
- Check firewall settings on Mac
- Try `http://localhost:5000` if testing on the Mac itself

### Can't find directory paths:
- Use Files app to navigate to folders
- Long-press folder and select "Get Info" to see path
- iCloud paths typically start with `/private/var/mobile/...`

### Permission errors:
- iOS restricts file system access
- Use the web interface to run on Mac instead
- Only accessible folders will work with native iOS apps

