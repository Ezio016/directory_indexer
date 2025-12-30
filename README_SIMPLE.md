# 📁 Directory Indexer

Create hierarchical numbering (1, 1.1, 1.1.1) for any directory. Exports to JSON, XML, and TXT.

---

## 🚀 Two Ways to Use

### 💻 Desktop: Command-Line Tool
**For:** Mac, Windows, Linux

```bash
dirindex /path/to/folder
```

Creates: `Items_in_[FolderName]/` with JSON, XML, TXT files

---

### 📱 Mobile: Web App  
**For:** iPhone, iPad, Android

**Live at:** `https://ezio016.github.io/directory_indexer/` (after deployment)

**Install:** Add to home screen → Works like a native app

---

## 📖 Documentation

- **SIMPLE_GUIDE.md** - Quick start guide
- **TESTING_GUIDE.md** - How to test everything
- **WINDOWS_SETUP.md** - Windows installation
- **OUTPUT_LOCATION_GUIDE.md** - Output options
- **DEPLOYMENT_GUIDE.md** - How to deploy mobile app

---

## ⚡ Quick Examples

### Command-Line:
```bash
# Basic usage
dirindex ~/Documents

# Custom output location  
dirindex ~/Documents -o ~/Desktop

# Inside target directory
dirindex ~/Documents --output-in-target

# Interactive mode
dirindex ~/Documents -i
```

### Mobile:
1. Open app on phone
2. Select folder
3. Choose formats (JSON, XML, TXT)
4. Generate & download

---

## 📦 What It Creates

```
Items_in_YourFolder/
├── directory_index.json    # Machine-readable
├── directory_index.xml     # Structured format
└── directory_index.txt     # Human-readable

Example:
1. 📁 level1
  1.1. 📁 level2
    1.1.1. 📄 file.txt
  1.2. 📄 readme.md
```

---

## 🎯 Perfect For

- ✅ Documenting directory structures
- ✅ Creating file inventories
- ✅ Project documentation
- ✅ Archive catalogs
- ✅ Backup records

---

## 🔒 Privacy

**Mobile app:**
- Runs completely on your device
- Files never uploaded
- Works offline
- 100% private

**Command-line:**
- Processes locally
- Nothing sent anywhere

---

## 📱 Mobile Deployment

```bash
# 1. Push to GitHub
git push origin main

# 2. Enable GitHub Pages
# Settings → Pages → Enable

# 3. Share URL
https://ezio016.github.io/directory_indexer/

# 4. Users install on their phones
```

---

## 💻 Desktop Installation

### Mac/Linux:
```bash
chmod +x directory_indexer.py
sudo ln -sf $(pwd)/directory_indexer.py /usr/local/bin/dirindex
dirindex --help
```

### Windows:
See `WINDOWS_SETUP.md`

---

## ⚠️ Mobile Limitations

Mobile app can only access files **locally on the device**.

**For cloud files (iCloud, Dropbox, etc.):**
Use command-line tool on desktop.

---

## 🆘 Support

- Issues: GitHub Issues
- Docs: See `*.md` files
- Quick help: `dirindex --help`

---

## 📄 License

MIT License - See LICENSE file

---

## 🌟 Features

- ✅ Hierarchical numbering (IP-style)
- ✅ Multiple export formats
- ✅ Cross-platform
- ✅ Offline-capable (mobile)
- ✅ Privacy-focused
- ✅ Easy to use
- ✅ Free and open source

---

**Desktop:** `dirindex /path/to/folder`  
**Mobile:** https://ezio016.github.io/directory_indexer/

That's it! ✨

