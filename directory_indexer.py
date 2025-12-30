#!/usr/bin/env python3
"""
Directory Hierarchy Indexer - Reindex Tool
Creates hierarchical numbering (IP-style) for directory contents
Outputs stored inside the indexed folder

Usage:
    reindex /path                        # TXT only (default)
    reindex /path "Custom Name"          # TXT with custom name
    reindex /path -a                     # All formats (TXT, JSON, XML)
    reindex /path -j                     # JSON only
    reindex /path -x                     # XML only
    reindex /path -j "Custom Name"       # JSON with custom name
    reindex /path -rn "New Name"         # Rename in output
    reindex /path -u                     # Update existing TXT
    reindex /path -u "custom_index.txt"  # Update specific file
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


# ==================== DIRECTORY INDEXER ====================

class DirectoryIndexer:
    """Main indexer - outputs stored inside indexed folder"""
    
    def __init__(self, root_path: str, display_name: str = None):
        self.root_path = Path(root_path).resolve()
        self.display_name = display_name or self.root_path.name
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
    
    def find_existing_index(self, filename: str = None) -> Optional[Path]:
        """Find existing index file in folder (not subdirectories)"""
        if filename:
            # Look for specific file
            target = self.root_path / filename
            if target.exists():
                return target
            return None
        
        # Look for default index files
        for name in ["directory_index.txt", "directory_index.json", "directory_index.xml"]:
            target = self.root_path / name
            if target.exists():
                return target
        return None
    
    def generate_output(self, format_type: str, filename: str = None):
        """Generate single output file"""
        if not self.hierarchy:
            print("No data. Run scan() first.")
            return None
        
        data = {
            "root": self.display_name,
            "hierarchy": self.hierarchy
        }
        
        # Determine filename and content
        if format_type == 'txt':
            content = generate_txt(data)
            default_name = "directory_index.txt"
        elif format_type == 'json':
            content = generate_json(data)
            default_name = "directory_index.json"
        elif format_type == 'xml':
            content = generate_xml(data)
            default_name = "directory_index.xml"
        else:
            print(f"Unknown format: {format_type}")
            return None
        
        output_name = filename or default_name
        output_path = self.root_path / output_name
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Created: {output_name}")
        return output_path
    
    def generate_all(self):
        """Generate all formats"""
        if not self.hierarchy:
            print("No data. Run scan() first.")
            return []
        
        print(f"\nSaving to: {self.root_path}")
        files = []
        for fmt in ['txt', 'json', 'xml']:
            path = self.generate_output(fmt)
            if path:
                files.append(path)
        return files


# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(
        prog='reindex',
        description='Index directory with hierarchical numbering.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  reindex /path                        TXT only (default)
  reindex /path "Custom Name"          TXT with custom name
  reindex /path -a                     All formats (TXT, JSON, XML)
  reindex /path -j                     JSON only
  reindex /path -x                     XML only
  reindex /path -j "Custom Name"       JSON with custom name
  reindex /path -rn "New Name"         Rename directory in output
  reindex /path -u                     Update existing index
  reindex /path -u "my_index.txt"      Update specific file
"""
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        help="Directory path to index"
    )
    
    parser.add_argument(
        "name",
        nargs="?",
        help="Optional custom name for output"
    )
    
    parser.add_argument(
        "-a",
        action="store_true",
        help="All formats (TXT, JSON, XML)"
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
        "-rn",
        metavar="NAME",
        help="Rename directory in output"
    )
    
    parser.add_argument(
        "-u",
        nargs="?",
        const="",
        metavar="FILE",
        help="Update existing index (optionally specify filename)"
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
    
    # Determine display name
    display_name = args.rn or args.name or None
    
    # Create indexer
    indexer = DirectoryIndexer(target_dir, display_name=display_name)
    
    try:
        # Update mode
        if args.u is not None:
            update_file = args.u if args.u else None
            existing = indexer.find_existing_index(update_file)
            
            if existing:
                print(f"Updating: {existing.name}")
                indexer.scan()
                
                # Determine format from extension
                ext = existing.suffix.lower()
                if ext == '.txt':
                    indexer.generate_output('txt', existing.name)
                elif ext == '.json':
                    indexer.generate_output('json', existing.name)
                elif ext == '.xml':
                    indexer.generate_output('xml', existing.name)
                else:
                    indexer.generate_output('txt', existing.name)
            else:
                if update_file:
                    print(f"File not found: {update_file}")
                    print("Creating new index...")
                else:
                    print("No existing index found, creating new...")
                indexer.scan()
                print(f"\nSaving to: {indexer.root_path}")
                indexer.generate_output('txt')
        
        # All formats
        elif args.a:
            indexer.scan()
            indexer.generate_all()
        
        # JSON only
        elif args.j:
            indexer.scan()
            print(f"\nSaving to: {indexer.root_path}")
            indexer.generate_output('json')
        
        # XML only
        elif args.x:
            indexer.scan()
            print(f"\nSaving to: {indexer.root_path}")
            indexer.generate_output('xml')
        
        # Default: TXT only
        else:
            indexer.scan()
            print(f"\nSaving to: {indexer.root_path}")
            indexer.generate_output('txt')
        
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
