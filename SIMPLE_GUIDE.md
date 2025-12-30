# 📱 Directory Indexer - Simple Guide

Two ways to use it:

---

## 💻 Desktop (Mac, Windows, Linux)

### Command-Line Tool

**Installation:**
```bash
# Mac/Linux
chmod +x directory_indexer.py
sudo ln -sf $(pwd)/directory_indexer.py /usr/local/bin/dirindex

# Windows
# See WINDOWS_SETUP.md
```

**Usage:**
```bash
dirindex /path/to/folder
```

**Done!** Creates `Items_in_[FolderName]/` with JSON, XML, TXT files.

**Options:**
```bash
dirindex ~/Documents                     # Default: current directory
dirindex ~/Documents -o ~/Desktop        # Custom output location
dirindex ~/Documents --output-in-target  # Save inside target folder
dirindex ~/Documents -i                  # Interactive mode
```

---

## 📱 Mobile (iPhone, iPad, Android)

### Standalone Web App

**Installation:**

1. **Deploy to GitHub Pages:**
   ```bash
   git push origin main
   # Go to GitHub → Settings → Pages → Enable
   ```

2. **Your app will be at:**
   ```
   https://ezio016.github.io/directory_indexer/
   ```

3. **Install on mobile:**
   - **iPhone/iPad**: Open in Safari → Share → Add to Home Screen
   - **Android**: Open in Chrome → Menu → Install App

**Usage:**
1. Open the installed app
2. Tap "Select Folder"
3. Choose which formats (JSON, XML, TXT)
4. Tap "Generate Index"
5. Download files

**✨ Features:**
- Runs completely on your device
- No internet needed after install
- Files never leave your device
- Works offline

**⚠️ Limitation:**
- Can only access files **locally on the device**
- Cannot access cloud files (iCloud, Dropbox, etc.) unless downloaded locally

---

## 📊 Which to Use?

| Use Case | Solution |
|----------|----------|
| **Index files on Mac** | Command-line tool |
| **Index files on Windows** | Command-line tool |
| **Index files on Linux** | Command-line tool |
| **Index files on iPhone** | Mobile web app |
| **Index files on iPad** | Mobile web app |
| **Index files on Android** | Mobile web app |
| **Cloud files (Dropbox, iCloud)** | Command-line on desktop |
| **Share with others** | Mobile web app (GitHub Pages) |

---

## 🚀 Quick Start

### For You (Command-Line):
```bash
dirindex ~/Documents
```

### For Everyone (Mobile):
1. Deploy to GitHub Pages
2. Share URL: `https://ezio016.github.io/directory_indexer/`
3. Anyone installs it on their phone
4. They index their own files

---

## 📂 Project Structure

```
DirHierarchy/
├── directory_indexer.py    # Command-line tool
├── index.html              # Mobile app
├── app/static/             # App resources
│   ├── manifest.json       # PWA manifest
│   ├── sw.js              # Service worker
│   ├── icon-192.png       # App icon
│   └── icon-512.png       # App icon
├── test_example/          # Sample folder
└── *.md                   # Documentation
```

---

## 🎯 Deployment Steps (Mobile App)

### 1. Push to GitHub:
```bash
git push origin main
```

### 2. Enable GitHub Pages:
- Go to: https://github.com/Ezio016/directory_indexer
- Settings → Pages
- Source: Deploy from branch
- Branch: `main` → `/` (root)
- Save

### 3. Wait 1-2 minutes

### 4. Access at:
```
https://ezio016.github.io/directory_indexer/
```

### 5. Share this URL!

Anyone can:
- Open it on their phone
- Install it as an app
- Index their own local files

---

## 💡 Tips

### Command-Line:
- Fast and powerful
- Access any file on your computer
- Works with cloud-synced folders
- Great for automation

### Mobile App:
- User-friendly interface
- Works on any device
- Installs like native app
- Perfect for non-technical users

---

## 🆘 Troubleshooting

### Command-Line:
```bash
# Check if installed
which dirindex

# Reinstall
sudo ln -sf /path/to/directory_indexer.py /usr/local/bin/dirindex

# Test
dirindex --help
```

### Mobile App:
- Use Safari on iOS (not Chrome)
- Use Chrome on Android
- Files must be locally on device (not in cloud)
- Clear browser cache if issues

---

## 📱 Mobile App Limitations

**CAN access:**
- ✅ Files in "On My iPhone/iPad"
- ✅ Downloaded files
- ✅ Local device storage
- ✅ Photos (if granted permission)

**CANNOT access:**
- ❌ iCloud files (unless downloaded)
- ❌ Google Drive files
- ❌ Dropbox files
- ❌ Network drives

**Solution for cloud files:**
Use command-line tool on desktop where files are synced.

---

## 🎉 That's It!

**Desktop:** `dirindex /path/to/folder`  
**Mobile:** Install from GitHub Pages

Simple! ✨

