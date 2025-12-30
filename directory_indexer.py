#!/usr/bin/env python3
"""
Directory Hierarchy Indexer - Pipes & Filters Architecture
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
from typing import List, Dict, Any, Callable


# ==================== FILTER FUNCTIONS ====================
# Each filter is a pure function that transforms data

def filter_scan(path: Path) -> List[Path]:
    """Filter 1: Scan directory and return all entries"""
    if not path.exists():
        raise ValueError(f"Path '{path}' does not exist")
    
    try:
        # Get all items, filter hidden files
        entries = [e for e in path.iterdir() if not e.name.startswith('.')]
        return entries
    except PermissionError:
        print(f"Warning: Permission denied for {path}")
        return []


def filter_sort(entries: List[Path]) -> List[Path]:
    """Filter 2: Sort entries (directories first, then alphabetically)"""
    return sorted(entries, key=lambda x: (not x.is_dir(), x.name.lower()))


def filter_assign_numbers(entries: List[Path], root_path: Path, prefix: str = "") -> List[Dict[str, Any]]:
    """Filter 3: Assign hierarchical numbers to entries"""
    items = []
    
    for idx, entry in enumerate(entries, start=1):
        # Create hierarchical number (e.g., 1.1.1)
        number = f"{prefix}.{idx}" if prefix else str(idx)
        
        item = {
            "number": number,
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file",
            "path": str(entry.relative_to(root_path)),
            "full_path": entry,
            "children": []
        }
        
        items.append(item)
    
    return items


def filter_recurse(items: List[Dict[str, Any]], root_path: Path) -> List[Dict[str, Any]]:
    """Filter 4: Recursively process subdirectories"""
    for item in items:
        if item["type"] == "directory":
            # Build sub-pipeline for subdirectory
            sub_path = item["full_path"]
            
            try:
                # Apply same pipeline to subdirectory
                sub_entries = filter_scan(sub_path)
                sub_sorted = filter_sort(sub_entries)
                sub_numbered = filter_assign_numbers(sub_sorted, root_path, item["number"])
                sub_recursive = filter_recurse(sub_numbered, root_path)
                
                item["children"] = sub_recursive
            except Exception as e:
                print(f"Warning: Error processing {sub_path}: {e}")
    
    # Clean up full_path (not needed in output)
    for item in items:
        if "full_path" in item:
            del item["full_path"]
    
    return items


def filter_to_json(data: Dict[str, Any]) -> str:
    """Output Filter: Convert hierarchy to JSON"""
    return json.dumps(data, indent=2, ensure_ascii=False)


def filter_to_xml(data: Dict[str, Any]) -> str:
    """Output Filter: Convert hierarchy to XML"""
    root = ET.Element("directory_index")
    root.set("root_path", str(data["root"]))
    
    def add_items_to_xml(parent_element, items):
        for item in items:
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
    
    # Pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    return xml_str


def filter_to_txt(data: Dict[str, Any]) -> str:
    """Output Filter: Convert hierarchy to indented text"""
    def format_item(item, depth=0):
        indent = "  " * depth
        type_icon = "📁" if item["type"] == "directory" else "📄"
        lines = [f"{indent}{item['number']}. {type_icon} {item['name']}"]
        
        for child in item["children"]:
            lines.extend(format_item(child, depth + 1))
        
        return lines
    
    txt_lines = [
        f"Directory Index: {data['root']}",
        "=" * 80,
        ""
    ]
    
    for item in data["hierarchy"]:
        txt_lines.extend(format_item(item))
    
    return "\n".join(txt_lines)


# ==================== PIPELINE CLASS ====================

class Pipeline:
    """Pipes & Filters Pipeline"""
    
    def __init__(self):
        self.filters: List[Callable] = []
        self.name = "Pipeline"
    
    def add_filter(self, filter_func: Callable, name: str = None):
        """Add a filter to the pipeline"""
        self.filters.append((filter_func, name or filter_func.__name__))
        return self
    
    def execute(self, initial_data: Any) -> Any:
        """Execute all filters in sequence"""
        data = initial_data
        
        for filter_func, filter_name in self.filters:
            try:
                data = filter_func(data)
            except Exception as e:
                print(f"Error in filter '{filter_name}': {e}")
                raise
        
        return data


# ==================== DIRECTORY INDEXER ====================

class DirectoryIndexer:
    """Main indexer using Pipes & Filters architecture"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.hierarchy = []
    
    def scan(self):
        """Build hierarchy using pipeline"""
        print(f"Scanning directory: {self.root_path}")
        
        # Build main pipeline
        pipeline = Pipeline()
        
        # Add filters in sequence
        hierarchy = (pipeline
            .add_filter(lambda p: filter_scan(p), "scan")
            .add_filter(lambda entries: filter_sort(entries), "sort")
            .add_filter(lambda entries: filter_assign_numbers(entries, self.root_path), "number")
            .add_filter(lambda items: filter_recurse(items, self.root_path), "recurse")
            .execute(self.root_path))
        
        self.hierarchy = hierarchy
        
        item_count = self._count_items(self.hierarchy)
        print(f"Found {item_count} items")
        
        return self.hierarchy
    
    def generate_outputs(self, output_dir: str, formats: Dict[str, bool], auto_open: bool = True):
        """Generate output files using output filters"""
        if not self.hierarchy:
            print("No hierarchy data. Run scan() first.")
            return
        
        # Create output folder
        folder_name = self.root_path.name
        output_path = os.path.join(output_dir, f"Items_in_{folder_name}")
        os.makedirs(output_path, exist_ok=True)
        print(f"\nCreating output folder: {output_path}")
        
        # Prepare data for output filters
        data = {
            "root": str(self.root_path),
            "hierarchy": self.hierarchy
        }
        
        txt_file_path = None
        
        # Apply output filters in parallel (could be multithreaded)
        if formats.get('json', True):
            json_content = filter_to_json(data)
            json_path = os.path.join(output_path, "directory_index.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            print(f"✓ JSON file created: {json_path}")
        
        if formats.get('xml', True):
            xml_content = filter_to_xml(data)
            xml_path = os.path.join(output_path, "directory_index.xml")
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            print(f"✓ XML file created: {xml_path}")
        
        if formats.get('txt', True):
            txt_content = filter_to_txt(data)
            txt_file_path = os.path.join(output_path, "directory_index.txt")
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(txt_content)
            print(f"✓ TXT file created: {txt_file_path}")
        
        # Auto-open TXT file (cross-platform)
        if auto_open and txt_file_path:
            self._open_file(txt_file_path)
    
    def _open_file(self, file_path: str):
        """Open file in system default application"""
        try:
            system = platform.system()
            
            if system == 'Darwin':  # macOS
                subprocess.run(['open', '-R', file_path], check=False)
                print(f"\n📂 Revealing TXT file in Finder...")
            elif system == 'Windows':
                subprocess.run(['explorer', '/select,', os.path.abspath(file_path)], check=False)
                print(f"\n📂 Opening TXT file in Explorer...")
            elif system == 'Linux':
                subprocess.run(['xdg-open', os.path.dirname(os.path.abspath(file_path))], check=False)
                print(f"\n📂 Opening output folder...")
            else:
                print(f"\n📂 Output saved to: {file_path}")
        except Exception as e:
            print(f"\nNote: Could not auto-open file: {e}")
            print(f"Output saved to: {file_path}")
    
    def _count_items(self, items: List[Dict]) -> int:
        """Count total items recursively"""
        count = len(items)
        for item in items:
            count += self._count_items(item.get("children", []))
        return count


# ==================== MAIN CLI ====================

def main():
    parser = argparse.ArgumentParser(
        description="Index directory contents with hierarchical numbering (Pipes & Filters architecture)"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        help="Directory path to index (if not provided, will prompt)"
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip JSON output"
    )
    parser.add_argument(
        "--no-xml",
        action="store_true",
        help="Skip XML output"
    )
    parser.add_argument(
        "--no-txt",
        action="store_true",
        help="Skip TXT output"
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Don't automatically open the TXT file when done"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory for generated files (if not specified, will prompt or use current directory)"
    )
    parser.add_argument(
        "--output-in-target",
        action="store_true",
        help="Save output inside the target directory instead of current directory"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Ask where to save output (interactive mode)"
    )
    
    args = parser.parse_args()
    
    # Get directory path
    if args.directory:
        target_dir = args.directory
    else:
        target_dir = input("Enter directory path to index: ").strip()
    
    # Determine output directory
    if args.output_dir:
        output_base_dir = args.output_dir
    elif args.output_in_target:
        output_base_dir = target_dir
    elif args.interactive:
        print("\n📂 Where do you want to save the output?")
        print("   1. Current directory (default)")
        print("   2. Inside the target directory")
        print("   3. Custom location")
        choice = input("Choose (1-3) [1]: ").strip() or "1"
        
        if choice == "2":
            output_base_dir = target_dir
        elif choice == "3":
            output_base_dir = input("Enter custom output path: ").strip()
        else:
            output_base_dir = "."
    else:
        output_base_dir = "."
    
    # Create indexer and build hierarchy
    indexer = DirectoryIndexer(target_dir)
    
    try:
        indexer.scan()
        
        # Generate outputs
        formats = {
            'json': not args.no_json,
            'xml': not args.no_xml,
            'txt': not args.no_txt
        }
        
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
