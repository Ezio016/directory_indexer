# 📂 Output Location Guide

## Where Does `dirindex` Save Files?

By default, output is saved in your **current directory**. But you have options!

---

## Option 1: Current Directory (Default) ⭐

```bash
cd ~/Desktop
dirindex ~/Documents/MyProject
```

**Creates:** `~/Desktop/Items_in_MyProject/`

**When to use:**
- Quick indexing
- You're already in your preferred output location
- Most common use case

---

## Option 2: Custom Location (`-o`)

```bash
dirindex ~/Documents/MyProject -o ~/Desktop/indexes
```

**Creates:** `~/Desktop/indexes/Items_in_MyProject/`

**When to use:**
- Organizing all indexes in one place
- Saving to a specific folder
- Scripting and automation

**Examples:**
```bash
# Save to Desktop
dirindex ~/Documents/MyProject -o ~/Desktop

# Save to a dedicated folder
mkdir ~/MyIndexes
dirindex ~/Documents/MyProject -o ~/MyIndexes

# Save to current project directory
dirindex /path/to/folder -o .
```

---

## Option 3: Inside Target Directory (`--output-in-target`)

```bash
dirindex ~/Documents/MyProject --output-in-target
```

**Creates:** `~/Documents/MyProject/Items_in_MyProject/`

**When to use:**
- Keep index with the original files
- Self-documenting projects
- Archive purposes

**Example:**
```bash
dirindex ~/Documents/MyProject --output-in-target

# Result:
# ~/Documents/MyProject/
#   ├── actual_files/
#   ├── more_files/
#   └── Items_in_MyProject/     ← Output here!
#       ├── directory_index.json
#       ├── directory_index.xml
#       └── directory_index.txt
```

---

## Option 4: Interactive Mode (`-i`)

```bash
dirindex ~/Documents/MyProject -i
```

**Prompts you:**
```
📂 Where do you want to save the output?
   1. Current directory (default)
   2. Inside the target directory
   3. Custom location
Choose (1-3) [1]:
```

**When to use:**
- First time using the tool
- Unsure where to save
- Want to choose on-the-fly

---

## Quick Reference

| Command | Output Location |
|---------|----------------|
| `dirindex /path/to/folder` | Current directory |
| `dirindex /path/to/folder -o ~/Desktop` | `~/Desktop/` |
| `dirindex /path/to/folder --output-in-target` | Inside `/path/to/folder/` |
| `dirindex /path/to/folder -i` | Ask me each time |

---

## Tips & Tricks

### Create a dedicated indexes folder:
```bash
mkdir ~/DirectoryIndexes
cd ~/DirectoryIndexes
dirindex ~/Documents/Project1
dirindex ~/Documents/Project2
dirindex ~/Photos/2024

# Result:
# ~/DirectoryIndexes/
#   ├── Items_in_Project1/
#   ├── Items_in_Project2/
#   └── Items_in_2024/
```

### Index multiple folders to Desktop:
```bash
dirindex ~/Documents/Work -o ~/Desktop
dirindex ~/Documents/Personal -o ~/Desktop
dirindex ~/Photos -o ~/Desktop
```

### Keep indexes with their folders:
```bash
dirindex ~/Project1 --output-in-target
dirindex ~/Project2 --output-in-target
```

### Combine with other options:
```bash
# Save to Desktop, only TXT, don't open
dirindex ~/Documents --no-json --no-xml --no-open -o ~/Desktop

# Save inside target, interactive choice of formats
dirindex ~/Documents -i --output-in-target
```

---

## Common Scenarios

### Scenario 1: Quick personal use
```bash
cd ~/Desktop
dirindex ~/Documents/MyFolder
# Output: ~/Desktop/Items_in_MyFolder/
```

### Scenario 2: Professional documentation
```bash
dirindex /path/to/project --output-in-target
# Keeps documentation with the project
```

### Scenario 3: Bulk indexing
```bash
mkdir ~/all-indexes
for dir in ~/Documents/*/; do
    dirindex "$dir" -o ~/all-indexes
done
# All indexes in one place
```

### Scenario 4: Client delivery
```bash
dirindex ~/client-project -o ~/Desktop/ClientDelivery
# Clean delivery package on Desktop
```

---

## Default Behavior Summary

✅ **Default:** Output goes to current working directory  
✅ **Safe:** Never modifies the target directory  
✅ **Flexible:** Easy to change with flags  
✅ **Intuitive:** Works like most command-line tools  

---

## Frequently Asked Questions

**Q: Can I change the default behavior?**  
A: Yes! Use aliases:
```bash
# Always save to Desktop
alias dirindex-desktop='dirindex -o ~/Desktop'

# Always save inside target
alias dirindex-in='dirindex --output-in-target'
```

**Q: What if I specify multiple conflicting options?**  
A: Priority order:
1. `-o` (explicit path) - highest priority
2. `--output-in-target`
3. `-i` (interactive)
4. Default (current directory) - lowest priority

**Q: Can I use relative paths?**  
A: Yes!
```bash
dirindex ~/Documents -o ./output
dirindex ~/Documents -o ../results
```

**Q: Will it create the output directory if it doesn't exist?**  
A: Yes, automatically!

---

## Best Practices

1. **For yourself:** Use current directory (default)
2. **For projects:** Use `--output-in-target`
3. **For organization:** Use `-o ~/DirectoryIndexes`
4. **When unsure:** Use `-i` (interactive)

