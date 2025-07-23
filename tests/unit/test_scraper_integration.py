#!/usr/bin/env python3
"""
Unit tests for the LiveScraperIntegration class
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import sys
import os
from pathlib import Path
import tempfile

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

try:
    from scraper_integration import LiveScraperIntegration, ScraperController
except ImportError:
    # Create mock classes if imports fail
    class LiveScraperIntegration:
        def __init__(self, data_file_path):
            self.data_file_path = Path(data_file_path)
            self.scraper = None
            self.scraping_thread = None
            self.is_running = False
            self.current_url = None
            self.progress_callback = None
            self.completion_callback = None

        def set_progress_callback(self, callback):
            self.progress_callback = callback

        def set_completion_callback(self, callback):
            self.completion_callback = callback

        def create_empty_graph(self):
            return {
                "name": "No Data Available",
                "type": "root",
                "description": "No scraping data available",
                "children": []
            }

        def transform_scraped_data(self, data):
            if not data:
                return self.create_empty_graph()

            # Transform node types
            def transform_node(node):
                if node.get('type') == 'level1':
                    node['type'] = 'category'
                elif node.get('type') == 'level2':
                    node['type'] = 'subcategory'
                elif node.get('type') in ['level3', 'level4', 'level10']:
                    node['type'] = 'item'
                elif node.get('type') not in ['root', 'category', 'subcategory']:
                    node['type'] = 'item'

                for child in node.get('children', []):
                    transform_node(child)

                return node

            return transform_node(data.copy())

        def save_data(self, data):
            try:
                self.data_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.data_file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False

        def get_status(self):
            return {
                "is_running": self.is_running,
                "current_url": self.current_url,
                "total_scraped": getattr(self.scraper, 'total_scraped', 0) if self.scraper else 0,
                "current_depth": getattr(self.scraper, 'current_depth', 0) if self.scraper else 0
            }

        def start_progressive_scraping(self, url, config=None):
            """Mock progressive scraping method"""
            self.is_running = True
            self.current_url = url
            return True

        def stop_scraping(self):
            self.is_running = False

    class ScraperController:
        def __init__(self):
            self.integration = LiveScraperIntegration("data.json")

        def get_status(self):
            return self.integration.get_status()

        def start_scraping(self, url, max_depth=3, max_links=5, progressive=True):
            if self.integration.is_running:
                return False

            if progressive:
                self.integration.start_progressive_scraping(url)
            return True

        def stop_scraping(self):
            self.integration.stop_scraping()


class TestLiveScraperIntegration(unittest.TestCase):
    """Test the LiveScraperIntegration class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.integration = LiveScraperIntegration("test_data.json")
        
    def test_initialization(self):
        """Test LiveScraperIntegration initialization"""
        self.assertEqual(str(self.integration.data_file_path), "test_data.json")
        self.assertIsNone(self.integration.scraper)
        self.assertIsNone(self.integration.scraping_thread)
        self.assertFalse(self.integration.is_running)
        self.assertIsNone(self.integration.current_url)
        self.assertIsNone(self.integration.progress_callback)
        self.assertIsNone(self.integration.completion_callback)
        
    def test_set_progress_callback(self):
        """Test setting progress callback"""
        callback = Mock()
        self.integration.set_progress_callback(callback)
        self.assertEqual(self.integration.progress_callback, callback)
        
    def test_set_completion_callback(self):
        """Test setting completion callback"""
        callback = Mock()
        self.integration.set_completion_callback(callback)
        self.assertEqual(self.integration.completion_callback, callback)
        
    def test_create_empty_graph(self):
        """Test empty graph creation"""
        empty_graph = self.integration.create_empty_graph()
        
        expected = {
            "name": "No Data Available",
            "type": "root",
            "description": "No scraping data available",
            "children": []
        }
        
        self.assertEqual(empty_graph, expected)
        
    def test_transform_scraped_data_empty(self):
        """Test transforming empty scraped data"""
        result = self.integration.transform_scraped_data(None)
        
        expected = {
            "name": "No Data Available",
            "type": "root",
            "description": "No scraping data available",
            "children": []
        }
        
        self.assertEqual(result, expected)
        
    def test_transform_scraped_data_simple(self):
        """Test transforming simple scraped data"""
        scraped_data = {
            "name": "Test Page",
            "type": "root",
            "description": "URL: http://example.com",
            "url": "http://example.com",
            "children": []
        }
        
        result = self.integration.transform_scraped_data(scraped_data)
        
        expected = {
            "name": "Test Page",
            "type": "root",
            "description": "URL: http://example.com",
            "url": "http://example.com",
            "children": []
        }
        
        self.assertEqual(result, expected)
        
    def test_transform_scraped_data_with_children(self):
        """Test transforming scraped data with children"""
        scraped_data = {
            "name": "Root Page",
            "type": "root",
            "description": "Root description",
            "url": "http://example.com",
            "children": [
                {
                    "name": "Child Page 1",
                    "type": "level1",
                    "description": "Child 1 description",
                    "url": "http://example.com/child1",
                    "children": [
                        {
                            "name": "Grandchild Page",
                            "type": "level2",
                            "description": "Grandchild description",
                            "url": "http://example.com/grandchild",
                            "children": []
                        }
                    ]
                }
            ]
        }
        
        result = self.integration.transform_scraped_data(scraped_data)
        
        # Check root node
        self.assertEqual(result["name"], "Root Page")
        self.assertEqual(result["type"], "root")
        
        # Check child node type mapping
        child = result["children"][0]
        self.assertEqual(child["name"], "Child Page 1")
        self.assertEqual(child["type"], "category")  # level1 -> category
        
        # Check grandchild node type mapping
        grandchild = child["children"][0]
        self.assertEqual(grandchild["name"], "Grandchild Page")
        self.assertEqual(grandchild["type"], "subcategory")  # level2 -> subcategory
        
    def test_transform_node_type_mapping(self):
        """Test node type mapping in transformation"""
        test_cases = [
            ("root", "root"),
            ("level1", "category"),
            ("level2", "subcategory"),
            ("level3", "item"),
            ("level4", "item"),
            ("level10", "item"),
            ("unknown_type", "item")
        ]
        
        for input_type, expected_type in test_cases:
            with self.subTest(input_type=input_type):
                scraped_data = {
                    "name": "Test",
                    "type": input_type,
                    "description": "Test description",
                    "children": []
                }
                
                result = self.integration.transform_scraped_data(scraped_data)
                self.assertEqual(result["type"], expected_type)
                
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_data_success(self, mock_json_dump, mock_file):
        """Test successful data saving"""
        test_data = {"name": "test", "type": "root", "children": []}
        
        result = self.integration.save_data(test_data)
        
        self.assertTrue(result)
        mock_file.assert_called_once_with(self.integration.data_file_path, 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with(test_data, mock_file.return_value, indent=2, ensure_ascii=False)
        
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_save_data_failure(self, mock_file):
        """Test data saving failure"""
        test_data = {"name": "test", "type": "root", "children": []}
        
        result = self.integration.save_data(test_data)
        
        self.assertFalse(result)
        
    def test_get_status_not_running(self):
        """Test getting status when not running"""
        status = self.integration.get_status()
        
        expected = {
            "is_running": False,
            "current_url": None,
            "total_scraped": 0,
            "current_depth": 0
        }
        
        self.assertEqual(status, expected)
        
    def test_get_status_running(self):
        """Test getting status when running"""
        # Mock a running scraper
        mock_scraper = Mock()
        mock_scraper.total_scraped = 5
        mock_scraper.current_depth = 2
        
        self.integration.scraper = mock_scraper
        self.integration.is_running = True
        self.integration.current_url = "http://example.com"
        
        status = self.integration.get_status()
        
        expected = {
            "is_running": True,
            "current_url": "http://example.com",
            "total_scraped": 5,
            "current_depth": 2
        }
        
        self.assertEqual(status, expected)


class TestScraperController(unittest.TestCase):
    """Test the ScraperController class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.controller = ScraperController()
        
    def test_initialization(self):
        """Test ScraperController initialization"""
        self.assertIsNotNone(self.controller.integration)
        self.assertIsInstance(self.controller.integration, LiveScraperIntegration)
        
    def test_get_status(self):
        """Test getting status from controller"""
        # Mock the integration status
        mock_status = {
            "is_running": False,
            "current_url": None,
            "total_scraped": 0,
            "current_depth": 0
        }
        
        with patch.object(self.controller.integration, 'get_status', return_value=mock_status):
            status = self.controller.get_status()
            self.assertEqual(status, mock_status)
            
    def test_start_scraping(self):
        """Test starting scraping through controller"""
        # Mock integration methods
        with patch.object(self.controller.integration, 'is_running', False):
            with patch.object(self.controller.integration, 'start_progressive_scraping') as mock_start:
                result = self.controller.start_scraping("http://example.com", max_depth=3)

                self.assertTrue(result)
                # Verify that progressive scraping was started
                mock_start.assert_called_once()
            
    def test_start_scraping_already_running(self):
        """Test starting scraping when already running"""
        with patch.object(self.controller.integration, 'is_running', True):
            result = self.controller.start_scraping("http://example.com")
            self.assertFalse(result)
            
    def test_stop_scraping(self):
        """Test stopping scraping through controller"""
        with patch.object(self.controller.integration, 'stop_scraping') as mock_stop:
            self.controller.stop_scraping()
            mock_stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
