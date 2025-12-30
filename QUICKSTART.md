# 🚀 Quick Start Guide

## Install the App (Recommended)

### On iPhone 15 Pro / iPad A16:

```bash
# 1. On your Mac, start the server:
python3 pwa_app.py

# 2. On your iPhone/iPad, open Safari and go to:
#    http://Myats-MacBook-Pro.local:8080

# 3. Tap Share → Add to Home Screen → Add

# 4. Done! Open the "Directory Indexer" app from your home screen
```

### On Android:

```bash
# 1. Start server on any computer
# 2. Open Chrome → http://YOUR_IP:8080
# 3. Tap Menu → Install App
# 4. Done!
```

### On Mac/Windows/Linux Desktop:

```bash
# 1. Start server:
python3 pwa_app.py

# 2. Open Chrome/Edge → http://localhost:8080
# 3. Click install icon in address bar
# 4. Done!
```

---

## OR Use Command Line (For Power Users)

### One-Time Setup:

```bash
# Make script executable
chmod +x directory_indexer.py

# Create global command (Mac/Linux)
sudo ln -sf /path/to/directory_indexer.py /usr/local/bin/dirindex
```

### Usage:

```bash
# Index any directory
dirindex /path/to/folder

# Or drag-and-drop folder from Finder
dirindex [drag folder here]
```

---

## What Gets Created

Both methods create:
- `Items_in_[FolderName]/`
  - `directory_index.json`
  - `directory_index.xml`
  - `directory_index.txt`

With hierarchical numbering: 1, 1.1, 1.1.1, etc.

---

## Which Method Should I Use?

| Method | Best For |
|--------|----------|
| **PWA App** | iPhone, iPad, Android, easy sharing |
| **Command Line** | Mac terminal users, automation, scripts |

**Recommendation:** Install the app on mobile devices, use command line on desktop!

---

## Need Help?

- **Full app installation guide**: See [APP_GUIDE.md](APP_GUIDE.md)
- **iOS setup**: See [IOS_SETUP.md](IOS_SETUP.md)
- **Windows setup**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **All features**: See [README.md](README.md)

