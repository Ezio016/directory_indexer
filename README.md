# Directory Hierarchy Indexer

A simple Python tool to create hierarchical numbering (IP-style like 1.1.1) for directory contents and export to JSON, XML, and TXT formats.

## Features

- 📁 Recursively scans directories
- 🔢 Assigns hierarchical numbering (1, 1.1, 1.1.1, etc.)
- 📦 Outputs to JSON, XML, and indented TXT formats
- 🎯 Simple command-line interface
- ✨ Easy to test and use

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

# Specify output directory
python directory_indexer.py /path/to/dir -o ./output

# Combine options
python directory_indexer.py /path/to/dir --no-xml -o ./results
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

By default, the script creates three files in the current directory:
- `directory_index.json`
- `directory_index.xml`
- `directory_index.txt`

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Notes

- Hidden files (starting with `.`) are automatically skipped
- Items are sorted: directories first, then files, alphabetically within each group
- The script handles permission errors gracefully

