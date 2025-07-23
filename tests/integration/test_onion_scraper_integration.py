#!/usr/bin/env python3
"""
Integration tests for the onion scraper system
Tests the complete integration of TOC, OnionSearch, and data conversion
"""

import pytest
import unittest
import json
import tempfile
import csv
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import subprocess

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from onion_data_converters import OnionSearchConverter, TocMainConverter, OnionScraperRunner


class TestOnionScraperIntegration(unittest.TestCase):
    """Test complete onion scraper integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir()
        
        # Create project structure
        (self.project_root / "data").mkdir()
        (self.project_root / "onions" / "toc-main").mkdir(parents=True)
        (self.project_root / "onions" / "OnionSearch-master").mkdir(parents=True)
        
        self.runner = OnionScraperRunner(self.project_root)
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_onionsearch_csv_to_json_integration(self):
        """Test complete OnionSearch CSV to JSON conversion flow"""
        # Create sample CSV data
        csv_data = [
            ['ahmia', 'Privacy Tools', 'http://privacy.onion'],
            ['darksearchio', 'Secure Chat', 'http://chat.onion'],
            ['ahmia', 'Anonymous Forum', 'http://forum.onion'],
            ['onionland', 'Marketplace', 'http://market.onion'],
            ['darksearchio', 'News Site', 'http://news.onion']
        ]
        
        # Write CSV file
        csv_file = self.temp_dir / "test_results.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            
        # Convert to JSON
        converter = OnionSearchConverter("test query")
        success = converter.convert_csv_to_json(str(csv_file))
        
        self.assertTrue(success)
        
        # Verify structure
        data = converter.data_structure
        self.assertEqual(data['name'], 'OnionSearch Results: test query')
        self.assertEqual(data['type'], 'root')
        
        # Check search engines
        engines = {child['name']: child for child in data['children']}
        
        self.assertIn('ahmia', engines)
        self.assertIn('darksearchio', engines)
        self.assertIn('onionland', engines)
        
        # Verify ahmia results
        ahmia_results = engines['ahmia']['children']
        self.assertEqual(len(ahmia_results), 2)
        
        result_names = [result['name'] for result in ahmia_results]
        self.assertIn('Privacy Tools', result_names)
        self.assertIn('Anonymous Forum', result_names)
        
        # Save to file and verify
        output_file = self.temp_dir / "output.json"
        success = converter.save_to_file(str(output_file))
        self.assertTrue(success)
        
        # Verify saved file
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data, data)
        
    def test_toc_json_processing_integration(self):
        """Test TOC JSON processing and conversion"""
        # Sample TOC output
        toc_output = {
            "name": "Test Onion Site",
            "type": "root",
            "url": "http://test.onion",
            "description": "Test onion site crawl",
            "children": [
                {
                    "name": "Services",
                    "type": "category",
                    "url": "http://test.onion/services",
                    "description": "Services page",
                    "children": [
                        {
                            "name": "VPN Service",
                            "type": "item",
                            "url": "http://test.onion/services/vpn",
                            "description": "VPN service page",
                            "children": []
                        },
                        {
                            "name": "Email Service",
                            "type": "item",
                            "url": "http://test.onion/services/email",
                            "description": "Email service page",
                            "children": []
                        }
                    ]
                },
                {
                    "name": "About",
                    "type": "category",
                    "url": "http://test.onion/about",
                    "description": "About page",
                    "children": []
                }
            ]
        }
        
        # Process with TOC converter
        converter = TocMainConverter("http://test.onion")
        success = converter.process_toc_output(json.dumps(toc_output))
        
        self.assertTrue(success)
        
        # Verify processed data
        data = converter.data_structure
        self.assertEqual(data['name'], 'Test Onion Site')
        self.assertEqual(data['type'], 'root')
        self.assertEqual(data['url'], 'http://test.onion')
        self.assertEqual(len(data['children']), 2)
        
        # Check services section
        services = data['children'][0]
        self.assertEqual(services['name'], 'Services')
        self.assertEqual(len(services['children']), 2)
        
        # Save and verify
        output_file = self.temp_dir / "toc_output.json"
        success = converter.save_to_file(str(output_file))
        self.assertTrue(success)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data, data)
        
    @patch('subprocess.run')
    def test_onion_scraper_runner_toc_integration(self, mock_subprocess):
        """Test OnionScraperRunner TOC integration"""
        # Mock successful TOC execution
        toc_output = {
            "name": "TOC Crawl Result",
            "type": "root",
            "url": "http://test.onion",
            "children": []
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(toc_output)
        mock_subprocess.return_value = mock_result
        
        # Run TOC crawler
        success = self.runner.run_toc_crawler("http://test.onion")
        
        self.assertTrue(success)
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        
        # Check that the command includes the URL
        self.assertIn("http://test.onion", str(call_args))
        
        # Verify data file was created
        data_file = self.runner.get_data_file_path()
        self.assertTrue(data_file.exists())
        
        # Verify data content
        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data['name'], 'TOC Crawl Result')
        
    @patch('subprocess.run')
    def test_onion_scraper_runner_onionsearch_integration(self, mock_subprocess):
        """Test OnionScraperRunner OnionSearch integration"""
        # Mock successful OnionSearch execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Create mock CSV output file
        csv_file = self.project_root / "onions" / "OnionSearch-master" / "results.csv"
        csv_data = [
            ['ahmia', 'Test Result', 'http://test.onion']
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            
        # Mock the CSV file existence check
        with patch.object(Path, 'exists', return_value=True):
            success = self.runner.run_onionsearch("test query")
            
        self.assertTrue(success)
        
        # Verify data file was created
        data_file = self.runner.get_data_file_path()
        self.assertTrue(data_file.exists())
        
        # Verify data content
        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data['name'], 'OnionSearch Results: test query')
        self.assertEqual(len(saved_data['children']), 1)  # One search engine
        
    def test_data_format_consistency_across_scrapers(self):
        """Test that all scrapers produce consistent data format"""
        # Test OnionSearch format
        onion_converter = OnionSearchConverter("test query")
        onion_converter.add_search_engine_result("TestEngine", [
            {"title": "Test Site", "url": "http://test.onion"}
        ])
        
        onion_data = onion_converter.data_structure
        
        # Test TOC format
        toc_converter = TocMainConverter("http://test.onion")
        toc_output = {
            "name": "Test Site",
            "type": "root",
            "url": "http://test.onion",
            "children": []
        }
        toc_converter.process_toc_output(json.dumps(toc_output))
        toc_data = toc_converter.data_structure
        
        # Verify both have required fields
        required_fields = ['name', 'type', 'description', 'children']
        
        for field in required_fields:
            self.assertIn(field, onion_data)
            self.assertIn(field, toc_data)
            
        # Verify type values are valid
        valid_types = ['root', 'category', 'subcategory', 'item']
        
        def check_types(node):
            self.assertIn(node['type'], valid_types)
            for child in node.get('children', []):
                check_types(child)
                
        check_types(onion_data)
        check_types(toc_data)
        
    def test_error_handling_in_onion_integration(self):
        """Test error handling in onion scraper integration"""
        # Test with invalid CSV data
        invalid_csv = self.temp_dir / "invalid.csv"
        with open(invalid_csv, 'w') as f:
            f.write("invalid,csv,data,with,too,many,fields\n")
            
        converter = OnionSearchConverter("test")
        success = converter.convert_csv_to_json(str(invalid_csv))
        
        # Should handle gracefully
        self.assertFalse(success)
        
        # Test with invalid JSON for TOC
        toc_converter = TocMainConverter("http://test.onion")
        success = toc_converter.process_toc_output("invalid json")
        
        self.assertFalse(success)
        
        # Test subprocess failure
        with patch('subprocess.run') as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stderr = "Error message"
            mock_subprocess.return_value = mock_result
            
            success = self.runner.run_toc_crawler("http://test.onion")
            self.assertFalse(success)
            
    def test_concurrent_onion_scraper_operations(self):
        """Test concurrent onion scraper operations"""
        # Create multiple converters
        converter1 = OnionSearchConverter("query 1")
        converter2 = OnionSearchConverter("query 2")
        
        # Add data to both
        converter1.add_search_engine_result("Engine1", [
            {"title": "Result 1", "url": "http://test1.onion"}
        ])
        
        converter2.add_search_engine_result("Engine2", [
            {"title": "Result 2", "url": "http://test2.onion"}
        ])
        
        # Save to different files
        file1 = self.temp_dir / "output1.json"
        file2 = self.temp_dir / "output2.json"
        
        success1 = converter1.save_to_file(str(file1))
        success2 = converter2.save_to_file(str(file2))
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        
        # Verify both files exist and have correct content
        with open(file1, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
            
        with open(file2, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
            
        self.assertEqual(data1['name'], 'OnionSearch Results: query 1')
        self.assertEqual(data2['name'], 'OnionSearch Results: query 2')
        
        # Verify data integrity
        self.assertEqual(data1['children'][0]['name'], 'Engine1')
        self.assertEqual(data2['children'][0]['name'], 'Engine2')


if __name__ == '__main__':
    unittest.main()
