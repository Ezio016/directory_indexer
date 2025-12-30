# Directory Indexer

Create hierarchical numbering (1, 1.1, 1.1.1, etc.) for any directory. Exports to JSON, XML, and TXT.

---

## Installation

### Desktop (Mac/Linux):
```bash
chmod +x directory_indexer.py
sudo ln -sf $(pwd)/directory_indexer.py /usr/local/bin/dirindex
```

### Windows:
```cmd
# Add directory_indexer.py to PATH, or run directly:
python directory_indexer.py /path/to/folder
```

### Mobile (iPhone/iPad/Android):
Visit: https://ezio016.github.io/directory_indexer/  
Tap "Add to Home Screen" to install as app.

---

## Usage

### Command-Line:
```bash
dirindex /path/to/folder                 # Basic usage
dirindex ~/Documents -o ~/Desktop        # Custom output location
dirindex ~/Documents --output-in-target  # Save inside target folder
dirindex ~/Documents -i                  # Interactive mode
```

### Mobile App:
1. Open app
2. Select folder from your device
3. Choose formats (JSON/XML/TXT)
4. Generate & download

---

## Output Example

```
Items_in_YourFolder/
├── directory_index.json
├── directory_index.xml
└── directory_index.txt

1. 📁 Documents
  1.1. 📁 Projects
    1.1.1. 📄 file.txt
  1.2. 📄 readme.md
```

---

## Options

```bash
--no-json            # Skip JSON output
--no-xml             # Skip XML output
--no-txt             # Skip TXT output
--no-open            # Don't auto-open files
-o, --output-dir     # Custom output location
--output-in-target   # Save inside target folder
-i, --interactive    # Ask where to save
```

---

## Features

- Hierarchical numbering (IP-style: 1.1.1)
- Multiple export formats (JSON, XML, TXT)
- Alphabetically sorted
- Works on all platforms
- Mobile app for iOS/Android
- Privacy-focused (files stay on device)

---

## Mobile Limitations

Mobile app can only access files **locally on the device**.  
For cloud files (iCloud, Dropbox), use the command-line tool on desktop.

---

## License

MIT License - See LICENSE file
