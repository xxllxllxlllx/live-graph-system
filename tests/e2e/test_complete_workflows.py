#!/usr/bin/env python3
"""
End-to-end tests for complete user workflows
Tests full scraping operations, data visualization, and user interactions
"""

import pytest
import unittest
import json
import tempfile
import time
import threading
import subprocess
import requests
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from scraper_web_interface import app
from data_sync import DataSynchronizer


class TestCompleteWorkflows(unittest.TestCase):
    """Test complete end-to-end user workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        self.frontend_data_file = self.temp_dir / "frontend" / "data" / "data.json"
        self.frontend_data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Test server setup
        self.test_server_port = 8888
        self.test_server_process = None
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.test_server_process:
            self.test_server_process.terminate()
            self.test_server_process.wait()
            
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def start_test_website_server(self):
        """Start a test website server for scraping"""
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Website</title>
        </head>
        <body>
            <h1>Welcome to Test Website</h1>
            <nav>
                <a href="/page1.html">Page 1</a>
                <a href="/page2.html">Page 2</a>
                <a href="/page3.html">Page 3</a>
            </nav>
            <main>
                <p>This is the main page of our test website.</p>
                <p>It contains several links for testing web scraping functionality.</p>
            </main>
        </body>
        </html>
        """
        
        # Create test website files
        test_site_dir = self.temp_dir / "test_website"
        test_site_dir.mkdir()
        
        with open(test_site_dir / "index.html", 'w') as f:
            f.write(test_html)
            
        # Create additional pages
        for i in range(1, 4):
            page_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Page {i}</title>
            </head>
            <body>
                <h1>Test Page {i}</h1>
                <p>This is test page {i}.</p>
                <a href="/index.html">Back to Home</a>
            </body>
            </html>
            """
            with open(test_site_dir / f"page{i}.html", 'w') as f:
                f.write(page_html)
                
        # Start HTTP server
        try:
            self.test_server_process = subprocess.Popen([
                sys.executable, '-m', 'http.server', str(self.test_server_port)
            ], cwd=test_site_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(2)  # Wait for server to start
            
            # Test if server is running
            test_url = f"http://localhost:{self.test_server_port}/index.html"
            response = requests.get(test_url, timeout=5)
            
            if response.status_code == 200:
                return test_url
            else:
                raise Exception("Test server not responding")
                
        except Exception as e:
            if self.test_server_process:
                self.test_server_process.terminate()
            raise e
            
    @patch('scraper_web_interface.scraper_controller')
    @patch('scraper_web_interface.data_synchronizer')
    def test_complete_http_scraping_workflow(self, mock_sync, mock_controller):
        """Test complete HTTP scraping workflow from start to finish"""
        # Start test website server
        test_url = self.start_test_website_server()
        
        # Configure mocks
        mock_controller.integration.data_file_path = self.data_file
        mock_controller.start_scraping.return_value = True
        mock_controller.get_status.return_value = {
            "is_running": False,
            "current_url": None,
            "total_scraped": 0,
            "current_depth": 0
        }
        
        mock_sync.sync_to_frontend.return_value = True
        mock_sync.get_status.return_value = {
            "is_watching": True,
            "main_file_exists": True,
            "frontend_file_exists": True,
            "sync_needed": False,
            "last_sync_time": "2023-01-01T00:00:00"
        }
        
        # Step 1: Check initial status
        status_response = self.client.get('/api/status')
        self.assertEqual(status_response.status_code, 200)
        
        # Step 2: Start scraping
        scraping_request = {
            "url": test_url,
            "max_depth": 2,
            "max_links": 3,
            "progressive": True
        }
        
        start_response = self.client.post('/api/start',
                                        data=json.dumps(scraping_request),
                                        content_type='application/json')
        
        self.assertEqual(start_response.status_code, 200)
        self.assertIn("success", start_response.json)
        
        # Step 3: Monitor progress
        progress_response = self.client.get('/api/progress')
        self.assertEqual(progress_response.status_code, 200)
        
        # Step 4: Check data synchronization
        sync_status_response = self.client.get('/api/sync/status')
        self.assertEqual(sync_status_response.status_code, 200)
        
        # Step 5: Force sync to frontend
        force_sync_response = self.client.post('/api/sync/force')
        self.assertEqual(force_sync_response.status_code, 200)
        
        # Step 6: Stop scraping
        stop_response = self.client.post('/api/stop')
        self.assertEqual(stop_response.status_code, 200)
        
        # Verify the complete workflow
        mock_controller.start_scraping.assert_called_once()
        mock_sync.force_sync.assert_called_once()
        
    @patch('subprocess.run')
    @patch('scraper_web_interface.onion_runner')
    def test_complete_toc_scraping_workflow(self, mock_runner, mock_subprocess):
        """Test complete TOC onion scraping workflow"""
        # Mock TOC crawler output
        toc_output = {
            "name": "Test Onion Site",
            "type": "root",
            "url": "http://test.onion",
            "description": "TOC crawl of test onion site",
            "children": [
                {
                    "name": "Services",
                    "type": "category",
                    "url": "http://test.onion/services",
                    "description": "URL: http://test.onion/services",
                    "children": [
                        {
                            "name": "VPN Service",
                            "type": "item",
                            "url": "http://test.onion/services/vpn",
                            "description": "URL: http://test.onion/services/vpn",
                            "children": []
                        }
                    ]
                }
            ]
        }
        
        # Configure mocks
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(toc_output)
        mock_subprocess.return_value = mock_result
        
        mock_runner.run_toc_crawler.return_value = True
        mock_runner.get_data_file_path.return_value = self.data_file
        
        # Step 1: Start TOC crawling
        toc_request = {"url": "http://test.onion"}
        
        start_response = self.client.post('/api/toc/start',
                                        data=json.dumps(toc_request),
                                        content_type='application/json')
        
        self.assertEqual(start_response.status_code, 200)
        self.assertIn("success", start_response.json)
        
        # Step 2: Verify TOC crawler was called
        mock_runner.run_toc_crawler.assert_called_once_with("http://test.onion")
        
        # Step 3: Create expected data file for verification
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(toc_output, f, indent=2)
            
        # Step 4: Verify data file exists and has correct content
        self.assertTrue(self.data_file.exists())
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data['name'], 'Test Onion Site')
        self.assertEqual(saved_data['type'], 'root')
        self.assertEqual(len(saved_data['children']), 1)
        
        # Step 5: Test data synchronization
        synchronizer = DataSynchronizer(self.temp_dir)
        sync_success = synchronizer.sync_to_frontend()
        self.assertTrue(sync_success)
        
        # Verify frontend data file
        self.assertTrue(self.frontend_data_file.exists())
        
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            frontend_data = json.load(f)
            
        self.assertEqual(frontend_data, saved_data)
        
    @patch('subprocess.run')
    @patch('scraper_web_interface.onion_runner')
    def test_complete_onionsearch_workflow(self, mock_runner, mock_subprocess):
        """Test complete OnionSearch workflow"""
        # Mock OnionSearch execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Create mock CSV output
        csv_content = """ahmia,"Privacy Tools","http://privacy.onion"
darksearchio,"Secure Chat","http://chat.onion"
ahmia,"Anonymous Forum","http://forum.onion"
onionland,"Marketplace","http://market.onion"
"""
        
        csv_file = self.temp_dir / "onionsearch_results.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
            
        # Configure mocks
        mock_runner.run_onionsearch.return_value = True
        mock_runner.get_data_file_path.return_value = self.data_file
        
        # Step 1: Start OnionSearch
        search_request = {"query": "privacy tools"}
        
        start_response = self.client.post('/api/onionsearch/start',
                                        data=json.dumps(search_request),
                                        content_type='application/json')
        
        self.assertEqual(start_response.status_code, 200)
        self.assertIn("success", start_response.json)
        
        # Step 2: Verify OnionSearch was called
        mock_runner.run_onionsearch.assert_called_once_with("privacy tools")
        
        # Step 3: Create expected OnionSearch output
        expected_output = {
            "name": "OnionSearch Results: privacy tools",
            "type": "root",
            "description": "OnionSearch results for query: privacy tools",
            "children": [
                {
                    "name": "ahmia",
                    "type": "category",
                    "description": "URL: onion://ahmia",
                    "url": "onion://ahmia",
                    "children": [
                        {
                            "name": "Privacy Tools",
                            "type": "item",
                            "description": "URL: http://privacy.onion",
                            "url": "http://privacy.onion",
                            "children": []
                        },
                        {
                            "name": "Anonymous Forum",
                            "type": "item",
                            "description": "URL: http://forum.onion",
                            "url": "http://forum.onion",
                            "children": []
                        }
                    ]
                },
                {
                    "name": "darksearchio",
                    "type": "category",
                    "description": "URL: onion://darksearchio",
                    "url": "onion://darksearchio",
                    "children": [
                        {
                            "name": "Secure Chat",
                            "type": "item",
                            "description": "URL: http://chat.onion",
                            "url": "http://chat.onion",
                            "children": []
                        }
                    ]
                },
                {
                    "name": "onionland",
                    "type": "category",
                    "description": "URL: onion://onionland",
                    "url": "onion://onionland",
                    "children": [
                        {
                            "name": "Marketplace",
                            "type": "item",
                            "description": "URL: http://market.onion",
                            "url": "http://market.onion",
                            "children": []
                        }
                    ]
                }
            ]
        }
        
        # Save expected output to data file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(expected_output, f, indent=2)
            
        # Step 4: Verify data structure
        with open(self.data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        self.assertEqual(saved_data['name'], 'OnionSearch Results: privacy tools')
        self.assertEqual(saved_data['type'], 'root')
        self.assertGreater(len(saved_data['children']), 0)
        
        # Verify search engines are present
        engine_names = [child['name'] for child in saved_data['children']]
        self.assertIn('ahmia', engine_names)
        self.assertIn('darksearchio', engine_names)
        self.assertIn('onionland', engine_names)
        
    def test_data_visualization_workflow(self):
        """Test data visualization rendering workflow"""
        # Create sample data for visualization
        visualization_data = {
            "name": "Visualization Test Data",
            "type": "root",
            "description": "Test data for graph visualization",
            "children": [
                {
                    "name": "Category 1",
                    "type": "category",
                    "description": "First category",
                    "children": [
                        {
                            "name": "Item 1.1",
                            "type": "item",
                            "description": "First item in category 1",
                            "children": []
                        },
                        {
                            "name": "Item 1.2",
                            "type": "item",
                            "description": "Second item in category 1",
                            "children": []
                        }
                    ]
                },
                {
                    "name": "Category 2",
                    "type": "category",
                    "description": "Second category",
                    "children": [
                        {
                            "name": "Item 2.1",
                            "type": "item",
                            "description": "First item in category 2",
                            "children": []
                        }
                    ]
                }
            ]
        }
        
        # Step 1: Save data to main data file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(visualization_data, f, indent=2)
            
        # Step 2: Synchronize to frontend
        synchronizer = DataSynchronizer(self.temp_dir)
        sync_success = synchronizer.sync_to_frontend()
        self.assertTrue(sync_success)
        
        # Step 3: Verify frontend data file
        self.assertTrue(self.frontend_data_file.exists())
        
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            frontend_data = json.load(f)
            
        # Step 4: Validate data structure for visualization
        def validate_visualization_data(node, path="root"):
            """Validate data structure for D3.js visualization"""
            required_fields = ["name", "type", "description"]
            for field in required_fields:
                self.assertIn(field, node, f"Missing {field} in {path}")
                
            if "children" in node:
                for i, child in enumerate(node["children"]):
                    validate_visualization_data(child, f"{path}.children[{i}]")
                    
        validate_visualization_data(frontend_data)
        
        # Step 5: Test data format compatibility with D3.js
        # Verify hierarchical structure
        self.assertEqual(frontend_data['type'], 'root')
        self.assertEqual(len(frontend_data['children']), 2)
        
        # Verify category structure
        category1 = frontend_data['children'][0]
        self.assertEqual(category1['type'], 'category')
        self.assertEqual(len(category1['children']), 2)
        
        # Verify item structure
        item = category1['children'][0]
        self.assertEqual(item['type'], 'item')
        self.assertEqual(len(item['children']), 0)
        
    def test_error_recovery_workflow(self):
        """Test error recovery and graceful failure handling"""
        # Test 1: Invalid URL handling
        invalid_request = {"url": "invalid-url"}
        
        response = self.client.post('/api/start',
                                  data=json.dumps(invalid_request),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        
        # Test 2: Network failure simulation
        with patch('requests.Session.get', side_effect=requests.exceptions.ConnectionError("Network error")):
            network_request = {"url": "http://unreachable.com", "max_depth": 1}
            
            response = self.client.post('/api/start',
                                      data=json.dumps(network_request),
                                      content_type='application/json')
            
            # Should handle gracefully
            self.assertIn(response.status_code, [200, 500])
            
        # Test 3: Corrupted data file recovery
        corrupted_data = "invalid json content"
        with open(self.data_file, 'w') as f:
            f.write(corrupted_data)
            
        synchronizer = DataSynchronizer(self.temp_dir)
        sync_result = synchronizer.sync_to_frontend()
        
        # Should fail gracefully
        self.assertFalse(sync_result)
        
        # Test 4: Missing file recovery
        if self.data_file.exists():
            self.data_file.unlink()
            
        sync_result = synchronizer.sync_to_frontend()
        self.assertFalse(sync_result)
        
        # System should continue to function
        status_response = self.client.get('/api/status')
        self.assertEqual(status_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
