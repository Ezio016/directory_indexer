#!/usr/bin/env python3
"""
Directory Hierarchy Indexer
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


class DirectoryIndexer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.hierarchy = []
    
    def scan_directory(self, path=None, prefix="", depth=0):
        """Recursively scan directory and build hierarchy with numbering"""
        if path is None:
            path = self.root_path
        
        if not path.exists():
            print(f"Error: Path '{path}' does not exist")
            return []
        
        items = []
        try:
            # Get all items in directory, filter hidden files, sort alphabetically
            # Directories first, then files, each group sorted alphabetically (case-insensitive)
            all_entries = [e for e in path.iterdir() if not e.name.startswith('.')]
            entries = sorted(all_entries, key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for idx, entry in enumerate(entries, start=1):
                # Create the hierarchical number (e.g., 1.1.1)
                if prefix:
                    number = f"{prefix}.{idx}"
                else:
                    number = str(idx)
                
                item_data = {
                    "number": number,
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "path": str(entry.relative_to(self.root_path)),
                    "children": []
                }
                
                # Recursively process subdirectories
                if entry.is_dir():
                    item_data["children"] = self.scan_directory(entry, number, depth + 1)
                
                items.append(item_data)
        
        except PermissionError:
            print(f"Warning: Permission denied for {path}")
        
        return items
    
    def generate_json(self, output_dir):
        """Generate JSON output"""
        data = {
            "root": str(self.root_path),
            "hierarchy": self.hierarchy
        }
        
        output_path = os.path.join(output_dir, "directory_index.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON file created: {output_path}")
    
    def generate_xml(self, output_dir):
        """Generate XML output"""
        root = ET.Element("directory_index")
        root.set("root_path", str(self.root_path))
        
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
        
        add_items_to_xml(root, self.hierarchy)
        
        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        output_path = os.path.join(output_dir, "directory_index.xml")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        print(f"✓ XML file created: {output_path}")
    
    def generate_txt(self, output_dir):
        """Generate indented text output"""
        def format_item(item, depth=0):
            indent = "  " * depth
            type_icon = "📁" if item["type"] == "directory" else "📄"
            lines = [f"{indent}{item['number']}. {type_icon} {item['name']}"]
            
            for child in item["children"]:
                lines.extend(format_item(child, depth + 1))
            
            return lines
        
        output_path = os.path.join(output_dir, "directory_index.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Directory Index: {self.root_path}\n")
            f.write("=" * 80 + "\n\n")
            
            for item in self.hierarchy:
                for line in format_item(item):
                    f.write(line + "\n")
        
        print(f"✓ TXT file created: {output_path}")
        return output_path
    
    def process(self, json_output=True, xml_output=True, txt_output=True, output_base_dir=".", auto_open=True):
        """Process directory and generate all requested outputs"""
        print(f"Scanning directory: {self.root_path}")
        self.hierarchy = self.scan_directory()
        
        if not self.hierarchy:
            print("No items found or directory is empty")
            return
        
        print(f"Found {self._count_items(self.hierarchy)} items")
        
        # Create output folder with format "Items_in_[FolderName]"
        folder_name = self.root_path.name
        output_dir = os.path.join(output_base_dir, f"Items_in_{folder_name}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nCreating output folder: {output_dir}")
        
        txt_path = None
        
        if json_output:
            self.generate_json(output_dir)
        
        if xml_output:
            self.generate_xml(output_dir)
        
        if txt_output:
            txt_path = self.generate_txt(output_dir)
        
        # Auto-open the TXT file (cross-platform)
        if auto_open and txt_path:
            try:
                import platform
                system = platform.system()
                
                if system == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', txt_path], check=False)
                    print(f"\n📂 Revealing TXT file in Finder...")
                elif system == 'Windows':
                    subprocess.run(['explorer', '/select,', os.path.abspath(txt_path)], check=False)
                    print(f"\n📂 Opening TXT file in Explorer...")
                elif system == 'Linux':
                    # Try xdg-open for Linux
                    subprocess.run(['xdg-open', os.path.dirname(os.path.abspath(txt_path))], check=False)
                    print(f"\n📂 Opening output folder...")
                else:
                    print(f"\n📂 Output saved to: {txt_path}")
            except Exception as e:
                print(f"\nNote: Could not auto-open file: {e}")
                print(f"Output saved to: {txt_path}")
    
    def _count_items(self, items):
        """Count total items recursively"""
        count = len(items)
        for item in items:
            count += self._count_items(item["children"])
        return count


def main():
    parser = argparse.ArgumentParser(
        description="Index directory contents with hierarchical numbering"
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
        default=".",
        help="Output directory for generated files (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Get directory path
    if args.directory:
        target_dir = args.directory
    else:
        target_dir = input("Enter directory path to index: ").strip()
    
    # Create indexer
    indexer = DirectoryIndexer(target_dir)
    
    # Process and generate outputs
    indexer.process(
        json_output=not args.no_json,
        xml_output=not args.no_xml,
        txt_output=not args.no_txt,
        output_base_dir=args.output_dir,
        auto_open=not args.no_open
    )
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()

