#!/usr/bin/env python3
"""
Directory Hierarchy Indexer - Reindex Tool
Creates hierarchical numbering (IP-style) for directory contents
Outputs stored inside the indexed folder

Usage:
    reindex /path/to/folder           # Generate all formats (TXT, JSON, XML)
    reindex /path/to/folder -t        # TXT only
    reindex /path/to/folder -j        # JSON only
    reindex /path/to/folder -x        # XML only
    reindex /path/to/folder -w        # All formats + new ReadMe.txt
    reindex /path/to/folder -t -w     # TXT + ReadMe.txt
    reindex /path/to/folder -u        # Update (same as no flag)
"""

import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import argparse
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime


# ==================== HYBRID PIPELINE ====================

class HybridPipeline:
    """Optimized scanning with periodic progress yields"""
    
    def __init__(self):
        self.item_count = 0
        self.on_progress: Optional[Callable[[int, str], None]] = None
        self.yield_interval = 100
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        self.on_progress = callback
    
    def _emit_progress(self):
        if self.on_progress and self.item_count % self.yield_interval == 0:
            self.on_progress(self.item_count, f"Processing... {self.item_count:,} items")
    
    def scan_and_build(self, root_path: Path) -> List[Dict[str, Any]]:
        """Single-pass scan and hierarchy building"""
        self.item_count = 0
        root_str = str(root_path)
        
        hierarchy = self._scan_recursive(root_str, "")
        
        if self.on_progress:
            self.on_progress(self.item_count, f"Complete: {self.item_count:,} items")
        
        return hierarchy
    
    def _scan_recursive(self, dir_path: str, rel_path: str, parent_number: str = "") -> List[Dict[str, Any]]:
        """Recursive scan with inline numbering"""
        items = []
        
        try:
            with os.scandir(dir_path) as entries:
                sorted_entries = sorted(
                    [e for e in entries if not e.name.startswith('.')],
                    key=lambda e: (not e.is_dir(), e.name.lower())
                )
        except (PermissionError, OSError):
            return items
        
        for idx, entry in enumerate(sorted_entries, start=1):
            self.item_count += 1
            self._emit_progress()
            
            number = f"{parent_number}.{idx}" if parent_number else str(idx)
            item_rel_path = f"{rel_path}/{entry.name}" if rel_path else entry.name
            is_dir = entry.is_dir()
            
            item = {
                "number": number,
                "name": entry.name,
                "type": "directory" if is_dir else "file",
                "path": item_rel_path,
                "children": []
            }
            
            if is_dir:
                item["children"] = self._scan_recursive(entry.path, item_rel_path, number)
            
            items.append(item)
        
        return items


# ==================== OUTPUT GENERATORS ====================

def generate_txt(data: Dict[str, Any]) -> str:
    """Generate TXT output"""
    lines = [
        f"Directory Index: {data['root']}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        ""
    ]
    
    def format_items(items, depth=0):
        for item in items:
            indent = "  " * depth
            type_marker = "[D]" if item["type"] == "directory" else "[F]"
            lines.append(f"{indent}{item['number']}. {type_marker} {item['name']}")
            
            if item.get("children"):
                format_items(item["children"], depth + 1)
    
    format_items(data["hierarchy"])
    return "\n".join(lines)


def generate_json(data: Dict[str, Any]) -> str:
    """Generate JSON output"""
    return json.dumps(data, indent=2, ensure_ascii=False)


def generate_xml(data: Dict[str, Any]) -> str:
    """Generate XML output"""
    root = ET.Element("directory_index")
    root.set("root_path", str(data["root"]))
    root.set("generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def add_items(parent_element, items):
        for item in items:
            item_element = ET.SubElement(parent_element, "item")
            item_element.set("number", item["number"])
            item_element.set("type", item["type"])
            
            name_elem = ET.SubElement(item_element, "name")
            name_elem.text = item["name"]
            
            path_elem = ET.SubElement(item_element, "path")
            path_elem.text = item["path"]
            
            if item.get("children"):
                children_elem = ET.SubElement(item_element, "children")
                add_items(children_elem, item["children"])
    
    add_items(root, data["hierarchy"])
    
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_str


def generate_readme(folder_name: str, item_count: int, hierarchy: List[Dict]) -> str:
    """Generate ReadMe.txt with folder overview"""
    
    def count_types(items):
        dirs = 0
        files = 0
        for item in items:
            if item["type"] == "directory":
                dirs += 1
                sub_dirs, sub_files = count_types(item.get("children", []))
                dirs += sub_dirs
                files += sub_files
            else:
                files += 1
        return dirs, files
    
    dir_count, file_count = count_types(hierarchy)
    
    top_items = []
    for item in hierarchy[:10]:
        type_marker = "[D]" if item["type"] == "directory" else "[F]"
        top_items.append(f"  {item['number']}. {type_marker} {item['name']}")
    
    if len(hierarchy) > 10:
        top_items.append(f"  ... and {len(hierarchy) - 10} more items")
    
    readme = f"""ReadMe - {folder_name}
{'=' * 60}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Items: {item_count:,}
Directories: {dir_count:,}
Files:       {file_count:,}

TOP-LEVEL CONTENTS
------------------
{chr(10).join(top_items)}

INDEX FILES
-----------
- directory_index.txt  : Full hierarchical listing
- directory_index.json : Machine-readable JSON format
- directory_index.xml  : XML format

NUMBERING SCHEME
----------------
Items are numbered hierarchically (e.g., 1.2.3):
- First number: position at root level
- Subsequent numbers: position within parent directory
- [D] = Directory, [F] = File

Example:
  1. [D] Documents
    1.1. [F] report.pdf
    1.2. [D] Archive
      1.2.1. [F] old_data.zip
"""
    return readme


# ==================== DIRECTORY INDEXER ====================

class DirectoryIndexer:
    """Main indexer - outputs stored inside indexed folder"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.hierarchy = []
        self.pipeline = HybridPipeline()
        self.item_count = 0
    
    def scan(self) -> List[Dict[str, Any]]:
        """Build hierarchy"""
        print(f"Scanning: {self.root_path}")
        
        def progress_callback(count: int, message: str):
            print(f"\r{message}", end="", flush=True)
        
        self.pipeline.set_progress_callback(progress_callback)
        self.hierarchy = self.pipeline.scan_and_build(self.root_path)
        self.item_count = self.pipeline.item_count
        
        print(f"\nFound {self.item_count:,} items")
        return self.hierarchy
    
    def generate_outputs(self, formats: Dict[str, bool], write_readme: bool = False):
        """Generate output files inside the indexed folder"""
        if not self.hierarchy:
            print("No data. Run scan() first.")
            return
        
        data = {
            "root": str(self.root_path),
            "hierarchy": self.hierarchy
        }
        
        output_dir = self.root_path
        print(f"\nSaving to: {output_dir}")
        
        created_files = []
        
        if formats.get('txt', False):
            txt_content = generate_txt(data)
            txt_path = output_dir / "directory_index.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            print(f"  Created: directory_index.txt")
            created_files.append(txt_path)
        
        if formats.get('json', False):
            json_content = generate_json(data)
            json_path = output_dir / "directory_index.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            print(f"  Created: directory_index.json")
            created_files.append(json_path)
        
        if formats.get('xml', False):
            xml_content = generate_xml(data)
            xml_path = output_dir / "directory_index.xml"
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            print(f"  Created: directory_index.xml")
            created_files.append(xml_path)
        
        if write_readme:
            readme_content = generate_readme(
                self.root_path.name, 
                self.item_count, 
                self.hierarchy
            )
            readme_path = output_dir / "ReadMe.txt"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"  Created: ReadMe.txt")
            created_files.append(readme_path)
        
        return created_files


# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(
        prog='reindex',
        description='Index directory with hierarchical numbering.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  reindex /path/to/folder           All formats (TXT, JSON, XML)
  reindex /path/to/folder -t        TXT only
  reindex /path/to/folder -j        JSON only
  reindex /path/to/folder -x        XML only
  reindex /path/to/folder -w        All formats + ReadMe.txt
  reindex /path/to/folder -t -w     TXT + ReadMe.txt
"""
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        help="Directory path to index"
    )
    
    parser.add_argument(
        "-t",
        action="store_true",
        help="TXT format only"
    )
    
    parser.add_argument(
        "-j",
        action="store_true",
        help="JSON format only"
    )
    
    parser.add_argument(
        "-x",
        action="store_true",
        help="XML format only"
    )
    
    parser.add_argument(
        "-w",
        action="store_true",
        help="Write ReadMe.txt"
    )
    
    parser.add_argument(
        "-u",
        action="store_true",
        help="Update existing index"
    )
    
    args = parser.parse_args()
    
    # Get directory
    if args.directory:
        target_dir = args.directory
    else:
        target_dir = input("Enter directory path: ").strip()
    
    if not target_dir:
        print("Error: No directory specified")
        return 1
    
    target_path = Path(target_dir)
    if not target_path.exists():
        print(f"Error: Directory not found: {target_dir}")
        return 1
    
    if not target_path.is_dir():
        print(f"Error: Not a directory: {target_dir}")
        return 1
    
    # Determine formats
    # If any specific format is specified, use only those
    # Otherwise, generate all formats
    specific_format = args.t or args.j or args.x
    
    if specific_format:
        formats = {
            'txt': args.t,
            'json': args.j,
            'xml': args.x
        }
    else:
        # Default: all formats
        formats = {
            'txt': True,
            'json': True,
            'xml': True
        }
    
    # Create indexer and run
    indexer = DirectoryIndexer(target_dir)
    
    try:
        indexer.scan()
        indexer.generate_outputs(
            formats=formats,
            write_readme=args.w
        )
        print("\nDone!")
        
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
