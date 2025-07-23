#!/usr/bin/env python3
"""
Demo script for the onion scraper integration
Shows how to use the data converters programmatically
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add backend paths
sys.path.append('backend/core')

def demo_onionsearch_converter():
    """Demonstrate OnionSearch CSV to JSON conversion"""
    print("🔍 OnionSearch Converter Demo")
    print("-" * 40)
    
    from onion_data_converters import OnionSearchConverter
    
    # Create sample CSV data (simulating OnionSearch output)
    sample_csv = '''ahmia,"Hidden Wiki","http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion"
darksearchio,"DuckDuckGo Onion","http://3g2upl4pq6kufc4m.onion"
ahmia,"Facebook Onion","http://facebookcorewwwi.onion"
phobos,"ProtonMail Onion","http://protonirockerxow.onion"
haystack,"Tor Project","http://expyuzz4wqqyqhjn.onion"'''
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv)
        csv_path = f.name
    
    try:
        # Convert CSV to JSON
        converter = OnionSearchConverter("privacy tools")
        success = converter.convert_csv_to_json(csv_path)
        
        if success:
            print(f"✅ Converted CSV with {len(converter.data_structure['children'])} search engines")
            
            # Display structure
            for engine in converter.data_structure['children']:
                print(f"  📂 {engine['name']}")
                for result in engine['children']:
                    print(f"    🔗 {result['name']}")
                    print(f"       {result['url']}")
            
            # Save to demo file
            demo_file = "demo_onionsearch_output.json"
            converter.save_to_file(demo_file)
            print(f"💾 Saved demo output to: {demo_file}")
            
        else:
            print("❌ Conversion failed")
            
    finally:
        # Cleanup
        os.unlink(csv_path)
    
    print()

def demo_toc_converter():
    """Demonstrate TOC JSON handling"""
    print("🧅 TOC Converter Demo")
    print("-" * 40)
    
    from onion_data_converters import TocMainConverter
    
    # Create sample TOC JSON data (simulating toc-main output)
    sample_toc_data = {
        "name": "Hidden Service Directory",
        "type": "root",
        "description": "URL: http://example.onion",
        "url": "http://example.onion",
        "children": [
            {
                "name": "Forum Section",
                "type": "category",
                "description": "URL: http://example.onion/forum",
                "url": "http://example.onion/forum",
                "children": [
                    {
                        "name": "General Discussion",
                        "type": "subcategory",
                        "description": "URL: http://example.onion/forum/general",
                        "url": "http://example.onion/forum/general",
                        "children": [
                            {
                                "name": "Welcome Thread",
                                "type": "item",
                                "description": "URL: http://example.onion/forum/general/welcome",
                                "url": "http://example.onion/forum/general/welcome",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Marketplace",
                "type": "category", 
                "description": "URL: http://example.onion/market",
                "url": "http://example.onion/market",
                "children": []
            }
        ]
    }
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_toc_data, f, indent=2)
        json_path = f.name
    
    try:
        # Process with TOC converter
        converter = TocMainConverter("http://example.onion")
        success = converter.convert_toc_json_to_json(json_path)
        
        if success:
            print(f"✅ Processed TOC data: {converter.data_structure['name']}")
            
            # Display structure
            def print_node(node, indent=0):
                prefix = "  " * indent
                icon = {"root": "🏠", "category": "📂", "subcategory": "📁", "item": "📄"}.get(node['type'], "📄")
                print(f"{prefix}{icon} {node['name']}")
                for child in node.get('children', []):
                    print_node(child, indent + 1)
            
            print_node(converter.data_structure)
            
            # Save to demo file
            demo_file = "demo_toc_output.json"
            converter.save_to_file(demo_file)
            print(f"💾 Saved demo output to: {demo_file}")
            
        else:
            print("❌ Processing failed")
            
    finally:
        # Cleanup
        os.unlink(json_path)
    
    print()

def demo_data_merging():
    """Demonstrate merging multiple JSON files"""
    print("🔗 Data Merging Demo")
    print("-" * 40)
    
    from onion_data_converters import merge_json_files
    
    # Create sample data files
    data1 = {
        "name": "HTTP Results",
        "type": "root",
        "description": "Regular web scraping results",
        "url": "https://example.com",
        "children": [
            {
                "name": "About Page",
                "type": "item",
                "description": "URL: https://example.com/about",
                "url": "https://example.com/about",
                "children": []
            }
        ]
    }
    
    data2 = {
        "name": "Onion Results", 
        "type": "root",
        "description": "Dark web scraping results",
        "url": "http://example.onion",
        "children": [
            {
                "name": "Hidden Service",
                "type": "item", 
                "description": "URL: http://example.onion/service",
                "url": "http://example.onion/service",
                "children": []
            }
        ]
    }
    
    # Write temporary files
    files_to_merge = []
    for i, data in enumerate([data1, data2], 1):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, indent=2)
            files_to_merge.append(f.name)
    
    try:
        # Merge files
        merged_file = "demo_merged_output.json"
        success = merge_json_files(files_to_merge, merged_file, "Combined Scraping Results")
        
        if success:
            print(f"✅ Merged {len(files_to_merge)} files successfully")
            
            # Display merged structure
            with open(merged_file, 'r') as f:
                merged_data = json.load(f)
            
            print(f"📊 Combined data: {merged_data['name']}")
            print(f"   Total sections: {len(merged_data['children'])}")
            
            for section in merged_data['children']:
                print(f"   📂 {section['name']}: {len(section['children'])} items")
            
            print(f"💾 Saved merged output to: {merged_file}")
            
        else:
            print("❌ Merging failed")
            
    finally:
        # Cleanup
        for file_path in files_to_merge:
            os.unlink(file_path)
    
    print()

def demo_validation():
    """Demonstrate data validation"""
    print("✅ Data Validation Demo")
    print("-" * 40)
    
    # Test valid data
    valid_data = {
        "name": "Test Site",
        "type": "root",
        "description": "URL: https://test.com",
        "url": "https://test.com",
        "children": [
            {
                "name": "Sub Page",
                "type": "item",
                "description": "URL: https://test.com/sub",
                "url": "https://test.com/sub",
                "children": []
            }
        ]
    }
    
    # Test invalid data
    invalid_data = {
        "name": "Invalid Site",
        "type": "invalid_type",  # Invalid type
        "description": "URL: https://invalid.com",
        # Missing 'url' field
        "children": []
    }
    
    def validate_data(data, name):
        try:
            def validate_node(node, path="root"):
                required_fields = ["name", "type", "description", "url"]
                for field in required_fields:
                    if field not in node:
                        raise ValueError(f"Missing field '{field}' in {path}")
                
                valid_types = ["root", "category", "subcategory", "item"]
                if node["type"] not in valid_types:
                    raise ValueError(f"Invalid type '{node['type']}' in {path}")
                
                if "children" in node:
                    for i, child in enumerate(node["children"]):
                        validate_node(child, f"{path}.children[{i}]")
            
            validate_node(data)
            print(f"✅ {name}: Valid data structure")
            return True
            
        except ValueError as e:
            print(f"❌ {name}: {e}")
            return False
    
    validate_data(valid_data, "Valid Data Test")
    validate_data(invalid_data, "Invalid Data Test")
    
    print()

def main():
    """Run all demos"""
    print("🚀 Onion Scraper Integration Demo")
    print("=" * 50)
    print("This demo shows how the data converters work")
    print("without actually running the scrapers.\n")
    
    # Run demos
    demo_onionsearch_converter()
    demo_toc_converter()
    demo_data_merging()
    demo_validation()
    
    print("🎉 Demo completed!")
    print("\nGenerated files:")
    demo_files = [
        "demo_onionsearch_output.json",
        "demo_toc_output.json", 
        "demo_merged_output.json"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            print(f"  📄 {file}")
    
    print("\n💡 To see the actual scrapers in action:")
    print("   1. Run: python run.py --web")
    print("   2. Navigate to: http://localhost:5000")
    print("   3. Use the 3-section scraper interface")

if __name__ == "__main__":
    main()
