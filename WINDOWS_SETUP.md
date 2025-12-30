# 🪟 Windows Setup Guide

## Installation

1. **Install Python** (if not already installed):
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Download the script**:
   - Clone from GitHub or download the files
   - Extract to a folder like `C:\Tools\directory_indexer\`

## Usage

### Command Line:

```cmd
# Basic usage
python directory_indexer.py C:\Users\YourName\Documents

# Or drag and drop a folder after typing:
python directory_indexer.py [drag folder here]
```

### Make it Global (Optional):

**Option 1: Add to PATH**

1. Move `directory_indexer.py` to a permanent location (e.g., `C:\Tools\`)
2. Open **System Properties** → **Environment Variables**
3. Under **User variables**, find **Path** and click **Edit**
4. Click **New** and add: `C:\Tools\`
5. Click **OK** on all windows
6. Restart Command Prompt

Now you can run:
```cmd
python directory_indexer.py C:\any\path
```

**Option 2: Create a Batch File**

Create `dirindex.bat` with:
```batch
@echo off
python "C:\Tools\directory_indexer.py" %*
```

Place it in a folder that's in your PATH, then use:
```cmd
dirindex C:\path\to\folder
```

## Features on Windows

- ✅ Automatically opens File Explorer when done
- ✅ Creates `Items_in_[FolderName]` output folder
- ✅ Same features as macOS/Linux version

## Web Interface

For easier access or to share with mobile devices:

```cmd
# Install Flask
pip install flask

# Start the server
python web_server.py
```

Then access from any device at: `http://YOUR_PC_IP:5000`

## Troubleshooting

### "python is not recognized"
- Make sure Python is installed and added to PATH
- Try `python3` or `py` instead of `python`

### Permission errors
- Run Command Prompt as Administrator
- Or move files to a folder you have write access to

### File Explorer doesn't open automatically
- This is normal on some Windows configurations
- The files are still created in the output folder
- You can use `--no-open` flag to suppress this feature

