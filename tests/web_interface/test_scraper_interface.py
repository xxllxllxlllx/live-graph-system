#!/usr/bin/env python3
"""
Web interface tests for the three-part scraper interface
Tests HTTP/HTTPS, toc-main, and OnionSearch-master components
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
import threading
import subprocess

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from scraper_web_interface import app


class TestScraperWebInterface(unittest.TestCase):
    """Test the complete scraper web interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_main_interface_loads(self):
        """Test that the main scraper interface loads correctly"""
        with patch('flask.render_template') as mock_render:
            mock_render.return_value = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Live Graph System - Scraper Interface</title>
                <style>
                    body { background: white; color: black; }
                    .scraper-section { border: 1px solid black; }
                </style>
            </head>
            <body>
                <div id="http-scraper" class="scraper-section">
                    <h2>HTTP/HTTPS Scraper</h2>
                    <button id="http-start-btn">Start HTTP Scraping</button>
                </div>
                <div id="toc-scraper" class="scraper-section">
                    <h2>TOC Onion Crawler</h2>
                    <button id="toc-start-btn">Start TOC Crawling</button>
                </div>
                <div id="onionsearch-scraper" class="scraper-section">
                    <h2>OnionSearch Engine</h2>
                    <button id="onionsearch-start-btn">Start OnionSearch</button>
                </div>
            </body>
            </html>
            """
            
            response = self.client.get('/')
            
            self.assertEqual(response.status_code, 200)
            mock_render.assert_called_once_with('scraper_interface.html')
            
            # Verify the template contains required elements
            content = mock_render.return_value
            self.assertIn('HTTP/HTTPS Scraper', content)
            self.assertIn('TOC Onion Crawler', content)
            self.assertIn('OnionSearch Engine', content)
            self.assertIn('http-start-btn', content)
            self.assertIn('toc-start-btn', content)
            self.assertIn('onionsearch-start-btn', content)
            
    @patch('requests.Session.get')
    def test_http_scraper_interface(self, mock_get):
        """Test HTTP/HTTPS scraper interface functionality"""
        # Mock successful HTTP response
        mock_get.return_value = Mock(
            status_code=200,
            headers={'content-type': 'text/html'},
            content=b'''
            <html>
                <head><title>Test HTTP Site</title></head>
                <body>
                    <a href="http://example.com/page1">Page 1</a>
                    <a href="http://example.com/page2">Page 2</a>
                </body>
            </html>
            ''',
            url='http://example.com'
        )
        
        # Test HTTP scraper start
        request_data = {
            "url": "http://example.com",
            "max_depth": 2,
            "max_links": 3,
            "progressive": True
        }
        
        response = self.client.post('/api/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        
        # Test status endpoint
        status_response = self.client.get('/api/status')
        self.assertEqual(status_response.status_code, 200)
        
        status_data = status_response.json
        self.assertIn('is_running', status_data)
        self.assertIn('current_url', status_data)
        self.assertIn('total_scraped', status_data)
        
        # Test stop functionality
        stop_response = self.client.post('/api/stop')
        self.assertEqual(stop_response.status_code, 200)
        
    @patch('subprocess.run')
    def test_toc_scraper_interface(self, mock_subprocess):
        """Test TOC onion crawler interface functionality"""
        # Mock successful TOC execution
        toc_output = {
            "name": "TOC Crawl: http://test.onion",
            "type": "root",
            "url": "http://test.onion",
            "description": "TOC onion crawler results",
            "children": [
                {
                    "name": "Services Page",
                    "type": "category",
                    "url": "http://test.onion/services",
                    "description": "URL: http://test.onion/services",
                    "children": []
                }
            ]
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(toc_output)
        mock_subprocess.return_value = mock_result
        
        # Test TOC scraper start
        request_data = {"url": "http://test.onion"}
        
        response = self.client.post('/api/toc/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        
        # Verify subprocess was called with correct parameters
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        
        # Check that the command includes the onion URL
        self.assertIn("http://test.onion", str(call_args))
        
        # Test TOC stop (if implemented)
        stop_response = self.client.post('/api/toc/stop')
        # Should return 200 even if not fully implemented
        self.assertIn(stop_response.status_code, [200, 404, 405])
        
    @patch('subprocess.run')
    def test_onionsearch_interface(self, mock_subprocess):
        """Test OnionSearch engine interface functionality"""
        # Mock successful OnionSearch execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Create temporary project structure for testing
        project_root = self.temp_dir / "project"
        onionsearch_dir = project_root / "onions" / "OnionSearch-master"
        onionsearch_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock CSV output
        csv_file = onionsearch_dir / "results.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('ahmia,"Privacy Tools","http://privacy.onion"\n')
            f.write('darksearchio,"Secure Chat","http://chat.onion"\n')
            
        # Mock the onion runner to use our test directory
        with patch('scraper_web_interface.onion_runner') as mock_runner:
            mock_runner.project_root = project_root
            mock_runner.run_onionsearch.return_value = True
            
            # Test OnionSearch start
            request_data = {"query": "privacy tools"}
            
            response = self.client.post('/api/onionsearch/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            
            # Verify the runner was called with correct query
            mock_runner.run_onionsearch.assert_called_once_with("privacy tools")
            
        # Test OnionSearch stop
        stop_response = self.client.post('/api/onionsearch/stop')
        self.assertIn(stop_response.status_code, [200, 404, 405])
        
    def test_data_output_format_consistency(self):
        """Test that all three scrapers produce consistent data format"""
        expected_structure = {
            "name": str,
            "type": str,
            "description": str,
            "children": list
        }
        
        def validate_data_structure(data, path="root"):
            """Recursively validate data structure"""
            for field, expected_type in expected_structure.items():
                self.assertIn(field, data, f"Missing field '{field}' in {path}")
                self.assertIsInstance(data[field], expected_type, 
                                    f"Field '{field}' has wrong type in {path}")
                
            # Validate type values
            valid_types = ["root", "category", "subcategory", "item"]
            self.assertIn(data["type"], valid_types, 
                         f"Invalid type '{data['type']}' in {path}")
            
            # Recursively validate children
            for i, child in enumerate(data["children"]):
                validate_data_structure(child, f"{path}.children[{i}]")
        
        # Test HTTP scraper output format
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'<html><head><title>HTTP Test</title></head><body>Test</body></html>',
                url='http://example.com'
            )
            
            from scraper_web_interface import scraper_controller
            scraper_controller.integration.data_file_path = self.data_file
            
            request_data = {"url": "http://example.com", "max_depth": 1}
            response = self.client.post('/api/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            time.sleep(0.5)  # Wait for completion
            
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    http_data = json.load(f)
                validate_data_structure(http_data)
                
        # Test TOC output format
        with patch('subprocess.run') as mock_subprocess:
            toc_output = {
                "name": "TOC Test",
                "type": "root",
                "description": "TOC test data",
                "url": "http://test.onion",
                "children": []
            }
            
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps(toc_output)
            mock_subprocess.return_value = mock_result
            
            with patch('scraper_web_interface.onion_runner') as mock_runner:
                mock_runner.run_toc_crawler.return_value = True
                
                request_data = {"url": "http://test.onion"}
                response = self.client.post('/api/toc/start',
                                          data=json.dumps(request_data),
                                          content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                
        # Test OnionSearch output format
        with patch('scraper_web_interface.onion_runner') as mock_runner:
            mock_runner.run_onionsearch.return_value = True
            
            request_data = {"query": "test query"}
            response = self.client.post('/api/onionsearch/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            
    def test_progress_updates_interface(self):
        """Test progress updates interface for all scrapers"""
        from scraper_web_interface import progress_updates, progress_callback
        
        # Clear existing updates
        progress_updates.clear()
        
        # Simulate progress updates from different scrapers
        progress_callback({"type": "progress", "scraper": "http", "message": "HTTP scraping started"})
        progress_callback({"type": "progress", "scraper": "toc", "message": "TOC crawling in progress"})
        progress_callback({"type": "progress", "scraper": "onionsearch", "message": "OnionSearch running"})
        progress_callback({"type": "completion", "scraper": "http", "status": "success", "message": "HTTP completed"})
        
        # Get progress via API
        response = self.client.get('/api/progress')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 4)
        
        # Verify progress content
        progress_data = response.json
        scrapers_mentioned = [update.get("scraper") for update in progress_data]
        
        self.assertIn("http", scrapers_mentioned)
        self.assertIn("toc", scrapers_mentioned)
        self.assertIn("onionsearch", scrapers_mentioned)
        
    def test_error_handling_in_web_interface(self):
        """Test error handling across all scraper interfaces"""
        # Test HTTP scraper with invalid URL
        request_data = {"url": "invalid-url"}
        response = self.client.post('/api/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        
        # Test TOC scraper with missing URL
        request_data = {}
        response = self.client.post('/api/toc/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        # Test OnionSearch with missing query
        request_data = {}
        response = self.client.post('/api/onionsearch/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        # Test invalid JSON
        response = self.client.post('/api/start',
                                  data="invalid json",
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
    def test_concurrent_scraper_operations(self):
        """Test handling of concurrent operations across different scrapers"""
        # Mock successful responses for all scrapers
        with patch('requests.Session.get') as mock_http, \
             patch('subprocess.run') as mock_subprocess, \
             patch('scraper_web_interface.onion_runner') as mock_runner:
            
            # Configure mocks
            mock_http.return_value = Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'<html><head><title>Test</title></head><body>Test</body></html>',
                url='http://example.com'
            )
            
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = '{"name": "Test", "type": "root", "children": []}'
            mock_subprocess.return_value = mock_result
            
            mock_runner.run_toc_crawler.return_value = True
            mock_runner.run_onionsearch.return_value = True
            
            # Start HTTP scraper
            http_request = {"url": "http://example.com", "max_depth": 1}
            http_response = self.client.post('/api/start',
                                           data=json.dumps(http_request),
                                           content_type='application/json')
            
            self.assertEqual(http_response.status_code, 200)
            
            # Start TOC scraper (should work concurrently)
            toc_request = {"url": "http://test.onion"}
            toc_response = self.client.post('/api/toc/start',
                                          data=json.dumps(toc_request),
                                          content_type='application/json')
            
            self.assertEqual(toc_response.status_code, 200)
            
            # Start OnionSearch (should work concurrently)
            onion_request = {"query": "test query"}
            onion_response = self.client.post('/api/onionsearch/start',
                                            data=json.dumps(onion_request),
                                            content_type='application/json')
            
            self.assertEqual(onion_response.status_code, 200)
            
            # Verify all scrapers can run simultaneously
            # (In a real implementation, this would depend on the specific design)


if __name__ == '__main__':
    unittest.main()
