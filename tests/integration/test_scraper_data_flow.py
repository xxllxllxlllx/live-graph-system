#!/usr/bin/env python3
"""
Integration tests for the complete scraper data flow
Tests the interaction between scraper, data processing, and file I/O
"""

import pytest
import unittest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))

from web_scraper import WebScraper, ScrapingConfig
from scraper_integration import LiveScraperIntegration, ScraperController
from data_sync import DataSynchronizer


class TestScraperDataFlowIntegration(unittest.TestCase):
    """Test complete scraper data flow integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        self.frontend_data_file = self.temp_dir / "frontend" / "data" / "data.json"
        
        # Create directories
        self.frontend_data_file.parent.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('requests.Session.get')
    def test_complete_scraping_to_file_flow(self, mock_get):
        """Test complete flow from scraping to file output"""
        # Mock HTTP responses
        responses = [
            # Root page response
            Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'''
                <html>
                    <head><title>Root Page</title></head>
                    <body>
                        <a href="http://example.com/page1">Page 1</a>
                        <a href="http://example.com/page2">Page 2</a>
                    </body>
                </html>
                ''',
                url='http://example.com'
            ),
            # Page 1 response
            Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'''
                <html>
                    <head><title>Page 1</title></head>
                    <body><p>Content of page 1</p></body>
                </html>
                ''',
                url='http://example.com/page1'
            ),
            # Page 2 response
            Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'''
                <html>
                    <head><title>Page 2</title></head>
                    <body><p>Content of page 2</p></body>
                </html>
                ''',
                url='http://example.com/page2'
            )
        ]
        
        mock_get.side_effect = responses
        
        # Set up scraper integration
        integration = LiveScraperIntegration(str(self.data_file))
        
        # Configure scraper with limited depth for testing
        config = ScrapingConfig(max_depth=2, max_links_per_page=2, request_delay=0)
        scraper = WebScraper(config)
        
        # Start scraping
        scraped_data = scraper.start_scraping('http://example.com')
        
        # Verify scraped data structure
        self.assertIsNotNone(scraped_data)
        self.assertEqual(scraped_data['name'], 'Root Page')
        self.assertEqual(scraped_data['type'], 'root')
        self.assertEqual(len(scraped_data['children']), 2)
        
        # Transform and save data
        transformed_data = integration.transform_scraped_data(scraped_data)
        success = integration.save_data(transformed_data)
        
        self.assertTrue(success)
        self.assertTrue(self.data_file.exists())
        
        # Verify saved data
        with open(self.data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data['name'], 'Root Page')
        self.assertEqual(saved_data['type'], 'root')
        self.assertEqual(len(saved_data['children']), 2)
        
        # Check child nodes
        child_names = [child['name'] for child in saved_data['children']]
        self.assertIn('Page 1', child_names)
        self.assertIn('Page 2', child_names)
        
    def test_data_synchronization_flow(self):
        """Test data synchronization between main and frontend files"""
        # Create initial data in main file
        initial_data = {
            "name": "Test Data",
            "type": "root",
            "description": "Test synchronization",
            "children": []
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
            
        # Set up data synchronizer
        synchronizer = DataSynchronizer(self.temp_dir)
        
        # Test initial sync
        result = synchronizer.sync_to_frontend()
        self.assertTrue(result)
        self.assertTrue(self.frontend_data_file.exists())
        
        # Verify synchronized data
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            synced_data = json.load(f)
            
        self.assertEqual(synced_data, initial_data)
        
        # Test sync detection
        self.assertFalse(synchronizer.check_sync_needed())
        
        # Modify main file
        modified_data = initial_data.copy()
        modified_data['name'] = 'Modified Test Data'
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, indent=2)
            
        # Check sync needed
        self.assertTrue(synchronizer.check_sync_needed())
        
        # Perform sync
        result = synchronizer.sync_to_frontend()
        self.assertTrue(result)
        
        # Verify updated data
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
            
        self.assertEqual(updated_data['name'], 'Modified Test Data')
        
    @patch('requests.Session.get')
    def test_scraper_controller_integration(self, mock_get):
        """Test ScraperController integration with data flow"""
        # Mock successful response
        mock_get.return_value = Mock(
            status_code=200,
            headers={'content-type': 'text/html'},
            content=b'<html><head><title>Test</title></head><body>Test</body></html>',
            url='http://example.com'
        )
        
        # Set up controller with test data file
        controller = ScraperController()
        controller.integration.data_file_path = self.data_file
        
        # Test status before scraping
        status = controller.get_status()
        self.assertFalse(status['is_running'])
        self.assertEqual(status['total_scraped'], 0)
        
        # Start scraping
        success = controller.start_scraping('http://example.com', max_depth=1)
        self.assertTrue(success)
        
        # Wait for scraping to complete (in real scenario, this would be async)
        time.sleep(0.1)
        
        # Verify data file was created
        self.assertTrue(self.data_file.exists())
        
        # Verify data content
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertEqual(data['name'], 'Test')
        self.assertEqual(data['type'], 'root')
        
    def test_error_handling_in_data_flow(self):
        """Test error handling throughout the data flow"""
        # Test with invalid data file path
        invalid_path = self.temp_dir / "nonexistent" / "data.json"
        integration = LiveScraperIntegration(str(invalid_path))
        
        test_data = {"name": "test", "type": "root", "children": []}
        
        # Should handle directory creation gracefully
        success = integration.save_data(test_data)
        self.assertTrue(success)  # Should create directories and succeed
        
        # Test synchronizer with missing source file
        synchronizer = DataSynchronizer(self.temp_dir)
        result = synchronizer.sync_to_frontend()
        self.assertFalse(result)  # Should fail gracefully
        
        # Test with corrupted data file
        corrupted_file = self.temp_dir / "corrupted.json"
        with open(corrupted_file, 'w') as f:
            f.write("invalid json content")
            
        # Should handle corrupted JSON gracefully
        with open(corrupted_file, 'r') as f:
            content = f.read()
            
        # Synchronizer should handle this gracefully
        synchronizer.main_data_file = corrupted_file
        result = synchronizer.sync_to_frontend()
        self.assertFalse(result)
        
    @patch('requests.Session.get')
    def test_concurrent_scraping_data_access(self, mock_get):
        """Test handling of concurrent access to data files"""
        # Mock response
        mock_get.return_value = Mock(
            status_code=200,
            headers={'content-type': 'text/html'},
            content=b'<html><head><title>Test</title></head><body>Test</body></html>',
            url='http://example.com'
        )
        
        # Set up multiple integrations pointing to same file
        integration1 = LiveScraperIntegration(str(self.data_file))
        integration2 = LiveScraperIntegration(str(self.data_file))
        
        # Create test data
        test_data1 = {"name": "Data 1", "type": "root", "children": []}
        test_data2 = {"name": "Data 2", "type": "root", "children": []}
        
        # Save data from both integrations
        success1 = integration1.save_data(test_data1)
        success2 = integration2.save_data(test_data2)
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        
        # Verify final state (last write wins)
        with open(self.data_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
            
        self.assertEqual(final_data['name'], 'Data 2')
        
    def test_data_transformation_consistency(self):
        """Test consistency of data transformation across components"""
        # Create sample scraped data with various node types
        scraped_data = {
            "name": "Root Site",
            "type": "root",
            "description": "URL: http://example.com",
            "url": "http://example.com",
            "children": [
                {
                    "name": "Level 1 Page",
                    "type": "level1",
                    "description": "URL: http://example.com/level1",
                    "url": "http://example.com/level1",
                    "children": [
                        {
                            "name": "Level 2 Page",
                            "type": "level2",
                            "description": "URL: http://example.com/level2",
                            "url": "http://example.com/level2",
                            "children": [
                                {
                                    "name": "Level 3 Page",
                                    "type": "level3",
                                    "description": "URL: http://example.com/level3",
                                    "url": "http://example.com/level3",
                                    "children": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Transform data
        integration = LiveScraperIntegration(str(self.data_file))
        transformed_data = integration.transform_scraped_data(scraped_data)
        
        # Verify type mappings
        self.assertEqual(transformed_data['type'], 'root')
        self.assertEqual(transformed_data['children'][0]['type'], 'category')  # level1 -> category
        self.assertEqual(transformed_data['children'][0]['children'][0]['type'], 'subcategory')  # level2 -> subcategory
        self.assertEqual(transformed_data['children'][0]['children'][0]['children'][0]['type'], 'item')  # level3 -> item
        
        # Save and verify persistence
        success = integration.save_data(transformed_data)
        self.assertTrue(success)
        
        # Read back and verify consistency
        with open(self.data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data, transformed_data)


if __name__ == '__main__':
    unittest.main()
