#!/usr/bin/env python3
"""
Directory Hierarchy Indexer - Optimized Hybrid Architecture
Fast scanning with periodic yielding for UI responsiveness
Creates hierarchical numbering (IP-style) for directory contents
Outputs: JSON, XML, and indented TXT formats
"""

import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import argparse
import subprocess
import platform
from typing import Iterator, Dict, Any, Callable, List, Optional


# ==================== OPTIMIZED HYBRID PIPELINE ====================

class HybridPipeline:
    """
    Hybrid approach: Fast scanning + periodic yielding
    - Scans efficiently using os.scandir (fastest method)
    - Tracks paths as strings (no expensive relative_to())
    - Yields progress callbacks for UI responsiveness
    - Builds hierarchy in single pass
    """
    
    def __init__(self):
        self.item_count = 0
        self.on_progress: Optional[Callable[[int, str], None]] = None
        self.yield_interval = 100
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        self.on_progress = callback
    
    def _emit_progress(self):
        """Emit progress if callback is set"""
        if self.on_progress and self.item_count % self.yield_interval == 0:
            self.on_progress(self.item_count, f"Processing... {self.item_count:,} items")
    
    def scan_and_build(self, root_path: Path) -> List[Dict[str, Any]]:
        """
        Single-pass scan and hierarchy building
        Optimized: tracks relative path as string, no Path operations
        """
        self.item_count = 0
        root_str = str(root_path)
        
        hierarchy = self._scan_recursive(root_str, "")
        
        if self.on_progress:
            self.on_progress(self.item_count, f"Complete: {self.item_count:,} items")
        
        return hierarchy
    
    def _scan_recursive(self, dir_path: str, rel_path: str, parent_number: str = "") -> List[Dict[str, Any]]:
        """
        Recursive scan with inline numbering
        Optimized: uses os.scandir and string paths only
        """
        items = []
        
        try:
            # Use os.scandir for speed (faster than Path.iterdir)
            with os.scandir(dir_path) as entries:
                # Filter hidden and sort: dirs first, then alphabetically
                sorted_entries = sorted(
                    [e for e in entries if not e.name.startswith('.')],
                    key=lambda e: (not e.is_dir(), e.name.lower())
                )
        except (PermissionError, OSError):
            return items
        
        for idx, entry in enumerate(sorted_entries, start=1):
            self.item_count += 1
            self._emit_progress()
            
            # Build hierarchical number
            number = f"{parent_number}.{idx}" if parent_number else str(idx)
            
            # Build relative path as string (no Path operations)
            item_rel_path = f"{rel_path}/{entry.name}" if rel_path else entry.name
            
            is_dir = entry.is_dir()
            
            item = {
                "number": number,
                "name": entry.name,
                "type": "directory" if is_dir else "file",
                "path": item_rel_path,
                "children": []
            }
            
            # Recurse into directories
            if is_dir:
                item["children"] = self._scan_recursive(entry.path, item_rel_path, number)
            
            items.append(item)
        
        return items


# ==================== STREAMING OUTPUT GENERATORS ====================

def stream_to_json(data: Dict[str, Any]) -> Iterator[str]:
    """Stream JSON output"""
    yield json.dumps(data, indent=2, ensure_ascii=False)


def stream_to_xml(data: Dict[str, Any], on_progress: Callable = None) -> Iterator[str]:
    """Stream XML output"""
    root = ET.Element("directory_index")
    root.set("root_path", str(data["root"]))
    
    item_count = [0]
    
    def add_items_to_xml(parent_element, items):
        for item in items:
            item_count[0] += 1
            if on_progress and item_count[0] % 500 == 0:
                on_progress(item_count[0], f"Generating XML... {item_count[0]:,}")
            
            item_element = ET.SubElement(parent_element, "item")
            item_element.set("number", item["number"])
            item_element.set("type", item["type"])
            
            name_elem = ET.SubElement(item_element, "name")
            name_elem.text = item["name"]
            
            path_elem = ET.SubElement(item_element, "path")
            path_elem.text = item["path"]
            
            if item["children"]:
                children_elem = ET.SubElement(item_element, "children")
                add_items_to_xml(children_elem, item["children"])
    
    add_items_to_xml(root, data["hierarchy"])
    
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    yield xml_str


def stream_to_txt(data: Dict[str, Any], on_progress: Callable = None) -> Iterator[str]:
    """Stream TXT output line by line"""
    yield f"Directory Index: {data['root']}"
    yield "=" * 80
    yield ""
    
    item_count = [0]
    
    def format_items(items, depth=0):
        for item in items:
            item_count[0] += 1
            if on_progress and item_count[0] % 500 == 0:
                on_progress(item_count[0], f"Generating TXT... {item_count[0]:,}")
            
            indent = "  " * depth
            icon = "📁" if item["type"] == "directory" else "📄"
            yield f"{indent}{item['number']}. {icon} {item['name']}"
            
            if item["children"]:
                yield from format_items(item["children"], depth + 1)
    
    yield from format_items(data["hierarchy"])


# ==================== DIRECTORY INDEXER ====================

class DirectoryIndexer:
    """Main indexer using Optimized Hybrid architecture"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.hierarchy = []
        self.pipeline = HybridPipeline()
        self.item_count = 0
    
    def scan(self) -> List[Dict[str, Any]]:
        """Build hierarchy using optimized hybrid pipeline"""
        print(f"Scanning directory: {self.root_path}")
        
        def progress_callback(count: int, message: str):
            print(f"\r{message}", end="", flush=True)
        
        self.pipeline.set_progress_callback(progress_callback)
        self.hierarchy = self.pipeline.scan_and_build(self.root_path)
        self.item_count = self.pipeline.item_count
        
        print(f"\nFound {self.item_count:,} items")
        return self.hierarchy
    
    def generate_outputs(self, output_dir: str, formats: Dict[str, bool], auto_open: bool = True):
        """Generate output files"""
        if not self.hierarchy:
            print("No hierarchy data. Run scan() first.")
            return
        
        folder_name = self.root_path.name
        output_path = os.path.join(output_dir, f"Items_in_{folder_name}")
        os.makedirs(output_path, exist_ok=True)
        print(f"\nCreating output folder: {output_path}")
        
        data = {
            "root": str(self.root_path),
            "hierarchy": self.hierarchy
        }
        
        txt_file_path = None
        
        def progress_callback(count: int, message: str):
            print(f"\r{message}", end="", flush=True)
        
        if formats.get('json', True):
            print("Generating JSON...", end="")
            json_path = os.path.join(output_path, "directory_index.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                for chunk in stream_to_json(data):
                    f.write(chunk)
            print(f"\r✓ JSON: {json_path}")
        
        if formats.get('xml', True):
            print("Generating XML...", end="")
            xml_path = os.path.join(output_path, "directory_index.xml")
            with open(xml_path, 'w', encoding='utf-8') as f:
                for chunk in stream_to_xml(data, progress_callback):
                    f.write(chunk)
            print(f"\r✓ XML: {xml_path}                    ")
        
        if formats.get('txt', True):
            print("Generating TXT...", end="")
            txt_file_path = os.path.join(output_path, "directory_index.txt")
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                for line in stream_to_txt(data, progress_callback):
                    f.write(line + "\n")
            print(f"\r✓ TXT: {txt_file_path}                    ")
        
        if auto_open and txt_file_path:
            self._open_file(txt_file_path)
    
    def _open_file(self, file_path: str):
        """Open file in system default application"""
        try:
            system = platform.system()
            
            if system == 'Darwin':
                subprocess.run(['open', '-R', file_path], check=False)
                print(f"\n📂 Revealing in Finder...")
            elif system == 'Windows':
                subprocess.run(['explorer', '/select,', os.path.abspath(file_path)], check=False)
                print(f"\n📂 Opening in Explorer...")
            elif system == 'Linux':
                subprocess.run(['xdg-open', os.path.dirname(os.path.abspath(file_path))], check=False)
                print(f"\n📂 Opening folder...")
            else:
                print(f"\n📂 Output: {file_path}")
        except Exception as e:
            print(f"\nOutput saved to: {file_path}")


# ==================== BACKWARD COMPATIBLE FILTERS ====================

def filter_to_json(data: Dict[str, Any]) -> str:
    """Convert hierarchy to JSON"""
    return json.dumps(data, indent=2, ensure_ascii=False)


def filter_to_xml(data: Dict[str, Any]) -> str:
    """Convert hierarchy to XML"""
    return "".join(stream_to_xml(data))


def filter_to_txt(data: Dict[str, Any]) -> str:
    """Convert hierarchy to indented text"""
    return "\n".join(stream_to_txt(data))


# ==================== MAIN CLI ====================

def main():
    parser = argparse.ArgumentParser(
        description="Index directory with hierarchical numbering (Optimized Hybrid Pipeline)"
    )
    parser.add_argument("directory", nargs="?", help="Directory path to index")
    parser.add_argument("--no-json", action="store_true", help="Skip JSON")
    parser.add_argument("--no-xml", action="store_true", help="Skip XML")
    parser.add_argument("--no-txt", action="store_true", help="Skip TXT")
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open")
    parser.add_argument("-o", "--output-dir", help="Output directory")
    parser.add_argument("--output-in-target", action="store_true", help="Save in target dir")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.directory:
        target_dir = args.directory
    else:
        target_dir = input("Enter directory path to index: ").strip()
    
    if args.output_dir:
        output_base_dir = args.output_dir
    elif args.output_in_target:
        output_base_dir = target_dir
    elif args.interactive:
        print("\n📂 Where to save output?")
        print("   1. Current directory (default)")
        print("   2. Inside target directory")
        print("   3. Custom location")
        choice = input("Choose (1-3) [1]: ").strip() or "1"
        
        if choice == "2":
            output_base_dir = target_dir
        elif choice == "3":
            output_base_dir = input("Enter path: ").strip()
        else:
            output_base_dir = "."
    else:
        output_base_dir = "."
    
    indexer = DirectoryIndexer(target_dir)
    
    formats = {
        'json': not args.no_json,
        'xml': not args.no_xml,
        'txt': not args.no_txt
    }
    
    try:
        indexer.scan()
        indexer.generate_outputs(
            output_dir=output_base_dir,
            formats=formats,
            auto_open=not args.no_open
        )
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
