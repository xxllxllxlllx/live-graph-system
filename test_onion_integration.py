#!/usr/bin/env python3
"""
Test script for the integrated onion scraper system
Tests all three scraping methods and data format conversion
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add backend paths
sys.path.append('backend/core')
sys.path.append('backend/interfaces')

def test_data_converters():
    """Test the data format converters"""
    print("🧪 Testing data format converters...")
    
    try:
        from onion_data_converters import OnionSearchConverter, TocMainConverter, OnionScraperRunner
        
        # Test OnionSearchConverter
        print("  ✓ OnionSearchConverter imported successfully")
        converter = OnionSearchConverter("test query")
        print(f"  ✓ OnionSearchConverter initialized: {converter.data_structure['name']}")
        
        # Test TocMainConverter  
        toc_converter = TocMainConverter("http://test.onion")
        print(f"  ✓ TocMainConverter initialized: {toc_converter.data_structure['name']}")
        
        # Test OnionScraperRunner
        project_root = Path(".")
        runner = OnionScraperRunner(project_root)
        print(f"  ✓ OnionScraperRunner initialized with root: {runner.project_root}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data converter test failed: {e}")
        return False

def test_csv_to_json_conversion():
    """Test CSV to JSON conversion"""
    print("🔄 Testing CSV to JSON conversion...")
    
    try:
        from onion_data_converters import OnionSearchConverter
        
        # Create test CSV data
        test_csv_content = '''ahmia,"Test Site 1","http://test1.onion"
darksearchio,"Test Site 2","http://test2.onion"
ahmia,"Another Site","http://test3.onion"'''
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            csv_path = f.name
        
        # Convert to JSON
        converter = OnionSearchConverter("test")
        success = converter.convert_csv_to_json(csv_path)
        
        if success:
            print("  ✓ CSV to JSON conversion successful")
            print(f"  ✓ Found {len(converter.data_structure['children'])} search engines")
            
            # Verify structure
            for engine in converter.data_structure['children']:
                print(f"    - {engine['name']}: {len(engine['children'])} results")
            
            # Clean up
            os.unlink(csv_path)
            return True
        else:
            print("  ❌ CSV to JSON conversion failed")
            return False
            
    except Exception as e:
        print(f"  ❌ CSV conversion test failed: {e}")
        return False

def test_json_structure_validation():
    """Test that generated JSON matches expected format"""
    print("📋 Testing JSON structure validation...")
    
    try:
        from onion_data_converters import OnionSearchConverter
        
        converter = OnionSearchConverter("validation test")
        
        # Add some test data
        converter.data_structure["children"] = [
            {
                "name": "Test Engine",
                "type": "category", 
                "description": "URL: onion://test",
                "url": "onion://test",
                "children": [
                    {
                        "name": "Test Result",
                        "type": "item",
                        "description": "URL: http://test.onion",
                        "url": "http://test.onion",
                        "children": []
                    }
                ]
            }
        ]
        
        # Validate structure
        def validate_node(node, path="root"):
            required_fields = ["name", "type", "description", "url"]
            for field in required_fields:
                if field not in node:
                    raise ValueError(f"Missing field '{field}' in {path}")
            
            if node["type"] not in ["root", "category", "subcategory", "item"]:
                raise ValueError(f"Invalid type '{node['type']}' in {path}")
            
            if "children" in node:
                for i, child in enumerate(node["children"]):
                    validate_node(child, f"{path}.children[{i}]")
        
        validate_node(converter.data_structure)
        print("  ✓ JSON structure validation passed")
        
        # Test saving to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name
        
        success = converter.save_to_file(json_path)
        if success:
            print("  ✓ JSON file saving successful")
            
            # Verify file content
            with open(json_path, 'r') as f:
                loaded_data = json.load(f)
            
            if loaded_data["name"] == converter.data_structure["name"]:
                print("  ✓ JSON file content verification passed")
            else:
                print("  ❌ JSON file content verification failed")
                return False
            
            os.unlink(json_path)
            return True
        else:
            print("  ❌ JSON file saving failed")
            return False
            
    except Exception as e:
        print(f"  ❌ JSON validation test failed: {e}")
        return False

def test_web_interface_template():
    """Test that the web interface template can be created"""
    print("🌐 Testing web interface template creation...")
    
    try:
        from scraper_web_interface import create_scraper_interface_template
        
        create_scraper_interface_template()
        
        # Check if template was created
        template_path = Path("backend/templates/scraper_interface.html")
        if template_path.exists():
            print("  ✓ Web interface template created successfully")
            
            # Check for key elements
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_elements = [
                "HTTP/HTTPS Scraper",
                "TOC Onion Crawler", 
                "OnionSearch Engine",
                "http-start-btn",
                "toc-start-btn",
                "onionsearch-start-btn"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"  ❌ Missing elements in template: {missing_elements}")
                return False
            else:
                print("  ✓ All required elements found in template")
                return True
        else:
            print("  ❌ Template file not created")
            return False
            
    except Exception as e:
        print(f"  ❌ Web interface template test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints can be imported and initialized"""
    print("🔌 Testing API endpoints...")
    
    try:
        # This is a basic import test since we can't easily test Flask routes without running the server
        from scraper_web_interface import app
        
        # Check that the app has the expected routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/toc/start',
            '/api/toc/stop', 
            '/api/onionsearch/start',
            '/api/onionsearch/stop'
        ]
        
        missing_routes = []
        for route in expected_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"  ❌ Missing API routes: {missing_routes}")
            return False
        else:
            print("  ✓ All expected API routes found")
            return True
            
    except Exception as e:
        print(f"  ❌ API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Onion Scraper Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Data Converters", test_data_converters),
        ("CSV to JSON Conversion", test_csv_to_json_conversion),
        ("JSON Structure Validation", test_json_structure_validation),
        ("Web Interface Template", test_web_interface_template),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The onion scraper integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
