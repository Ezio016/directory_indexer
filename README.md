# Directory Hierarchy Indexer

A simple Python tool to create hierarchical numbering (IP-style like 1.1.1) for directory contents and export to JSON, XML, and TXT formats.

## Features

- 📁 Recursively scans directories
- 🔢 Assigns hierarchical numbering (1, 1.1, 1.1.1, etc.)
- 📦 Outputs to JSON, XML, and indented TXT formats
- 🎯 Simple command-line interface
- ✨ Easy to test and use
- 📂 Automatically opens the TXT file in Finder when done
- 🔤 Items sorted alphabetically (directories first, then files)

## Usage

### Basic Usage

```bash
python directory_indexer.py /path/to/directory
```

Or run without arguments to be prompted:

```bash
python directory_indexer.py
# Enter directory path to index: /path/to/directory
```

### Options

```bash
# Skip certain output formats
python directory_indexer.py /path/to/dir --no-json
python directory_indexer.py /path/to/dir --no-xml
python directory_indexer.py /path/to/dir --no-txt

# Don't automatically open the TXT file
python directory_indexer.py /path/to/dir --no-open

# Specify output directory
python directory_indexer.py /path/to/dir -o ./output

# Combine options
python directory_indexer.py /path/to/dir --no-xml --no-open -o ./results
```

### Examples

1. **Index the current directory:**
   ```bash
   python directory_indexer.py .
   ```

2. **Index a specific folder:**
   ```bash
   python directory_indexer.py ~/Documents/MyProject
   ```

3. **Create only TXT output:**
   ```bash
   python directory_indexer.py ~/Documents --no-json --no-xml
   ```

## 🌐 Web Interface (For iOS/iPad/Remote Access)

Access the indexer from **any device** including iPhone, iPad, or remote computers:

### Start the Web Server:

```bash
# Install Flask (one time only)
pip3 install -r requirements.txt

# Start the server
python3 web_server.py
```

### Access from any device:

1. **On the same network**: Open browser and go to `http://YOUR_IP:5000`
2. **From iPhone/iPad**: See [IOS_SETUP.md](IOS_SETUP.md) for full guide
3. Enter directory path, generate index, and download files

**Features:**
- 📱 Mobile-friendly interface
- 🎨 Beautiful, modern UI
- 💾 Direct download to device
- 🔄 Works on all platforms

## Output Formats

### JSON Format
```json
{
  "root": "/path/to/directory",
  "hierarchy": [
    {
      "number": "1",
      "name": "folder1",
      "type": "directory",
      "path": "folder1",
      "children": [
        {
          "number": "1.1",
          "name": "subfolder",
          "type": "directory",
          "path": "folder1/subfolder",
          "children": []
        }
      ]
    }
  ]
}
```

### TXT Format
```
Directory Index: /path/to/directory
================================================================================

1. 📁 folder1
  1.1. 📁 subfolder
    1.1.1. 📄 file.txt
    1.1.2. 📄 document.pdf
  1.2. 📄 readme.md
2. 📁 folder2
  2.1. 📄 data.json
```

### XML Format
```xml
<?xml version="1.0" ?>
<directory_index root_path="/path/to/directory">
  <item number="1" type="directory">
    <name>folder1</name>
    <path>folder1</path>
    <children>
      <item number="1.1" type="file">
        <name>file.txt</name>
        <path>folder1/file.txt</path>
      </item>
    </children>
  </item>
</directory_index>
```

## Output Files

The script automatically creates a folder named `Items_in_[FolderName]` (where FolderName is the name of the directory you're indexing) and places three files inside:
- `directory_index.json`
- `directory_index.xml`
- `directory_index.txt`

**Example:** If you index a folder called `MyProject`, the output folder will be `Items_in_MyProject/`

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)
- **Web interface**: Flask (optional, for iOS/web access)

## Platform Support

✅ **Desktop:**
- macOS (tested)
- Windows (cross-platform compatible)
- Linux (cross-platform compatible)

✅ **Mobile:**
- iPhone/iPad via web interface
- See [IOS_SETUP.md](IOS_SETUP.md) for detailed instructions

## Global Installation (Optional)

To use `dirindex` from anywhere on your system:

```bash
# Make the script executable
chmod +x /path/to/directory_indexer.py

# Create a global symlink (requires sudo)
sudo ln -sf /path/to/directory_indexer.py /usr/local/bin/dirindex

# Now use it from anywhere!
dirindex /path/to/folder

# Or drag and drop folders:
dirindex [drag folder here from Finder]
```

**To remove:**
```bash
sudo rm /usr/local/bin/dirindex
```

## Notes

- Hidden files (starting with `.`) are automatically skipped
- Items are sorted: directories first, then files, alphabetically within each group
- The script handles permission errors gracefully

