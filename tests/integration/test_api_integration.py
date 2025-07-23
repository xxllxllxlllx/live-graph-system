#!/usr/bin/env python3
"""
Integration tests for API endpoints with backend services
Tests the complete API integration with scraper and data services
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

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from scraper_web_interface import app, scraper_controller, onion_runner, data_synchronizer


class TestAPIIntegration(unittest.TestCase):
    """Test API integration with backend services"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Set up temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        self.frontend_data_file = self.temp_dir / "frontend" / "data" / "data.json"
        
        # Create directories
        self.frontend_data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Clear progress updates
        from scraper_web_interface import progress_updates
        progress_updates.clear()
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('requests.Session.get')
    def test_complete_scraping_api_flow(self, mock_get):
        """Test complete scraping flow through API"""
        # Mock HTTP response
        mock_get.return_value = Mock(
            status_code=200,
            headers={'content-type': 'text/html'},
            content=b'''
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <a href="http://example.com/page1">Page 1</a>
                    <a href="http://example.com/page2">Page 2</a>
                </body>
            </html>
            ''',
            url='http://example.com'
        )
        
        # Override data file path for testing
        scraper_controller.integration.data_file_path = self.data_file
        
        # Start scraping via API
        request_data = {
            "url": "http://example.com",
            "max_depth": 2,
            "max_links": 2,
            "progressive": True
        }
        
        response = self.client.post('/api/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        
        # Wait for scraping to complete
        time.sleep(0.5)
        
        # Check status
        status_response = self.client.get('/api/status')
        self.assertEqual(status_response.status_code, 200)
        
        # Verify data file was created
        self.assertTrue(self.data_file.exists())
        
        # Verify data content
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertEqual(data['name'], 'Test Page')
        self.assertEqual(data['type'], 'root')
        
        # Stop scraping
        stop_response = self.client.post('/api/stop')
        self.assertEqual(stop_response.status_code, 200)
        
    def test_progress_updates_integration(self):
        """Test progress updates through API"""
        from scraper_web_interface import progress_updates, progress_callback
        
        # Simulate progress updates
        progress_callback({"type": "progress", "message": "Starting scrape"})
        progress_callback({"type": "progress", "message": "Found 5 links"})
        progress_callback({"type": "completion", "status": "success", "message": "Completed"})
        
        # Get progress via API
        response = self.client.get('/api/progress')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        
        # Verify progress content
        progress_data = response.json
        self.assertEqual(progress_data[0]["message"], "Starting scrape")
        self.assertEqual(progress_data[1]["message"], "Found 5 links")
        self.assertEqual(progress_data[2]["status"], "success")
        
    @patch('subprocess.run')
    def test_toc_scraper_api_integration(self, mock_subprocess):
        """Test TOC scraper integration through API"""
        # Mock successful TOC execution
        toc_output = {
            "name": "Test Onion Site",
            "type": "root",
            "url": "http://test.onion",
            "children": []
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(toc_output)
        mock_subprocess.return_value = mock_result
        
        # Override data file path
        onion_runner.project_root = self.temp_dir
        
        # Start TOC scraper via API
        request_data = {"url": "http://test.onion"}
        
        response = self.client.post('/api/toc/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        
        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        
        # Verify data file was created
        data_file = self.temp_dir / "data" / "data.json"
        self.assertTrue(data_file.exists())
        
        # Verify data content
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertEqual(data['name'], 'Test Onion Site')
        
    @patch('subprocess.run')
    def test_onionsearch_api_integration(self, mock_subprocess):
        """Test OnionSearch integration through API"""
        # Mock successful OnionSearch execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        # Create mock CSV output
        csv_file = self.temp_dir / "onions" / "OnionSearch-master" / "results.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('ahmia,"Test Site","http://test.onion"\n')
            
        # Override paths
        onion_runner.project_root = self.temp_dir
        
        # Mock file existence check
        with patch.object(Path, 'exists', return_value=True):
            request_data = {"query": "test query"}
            
            response = self.client.post('/api/onionsearch/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json)
        
        # Verify data file was created
        data_file = self.temp_dir / "data" / "data.json"
        self.assertTrue(data_file.exists())
        
    def test_data_sync_api_integration(self):
        """Test data synchronization through API"""
        # Create initial data
        initial_data = {
            "name": "Test Data",
            "type": "root",
            "description": "Test sync",
            "children": []
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
            
        # Override synchronizer paths
        data_synchronizer.project_root = self.temp_dir
        data_synchronizer.main_data_file = self.data_file
        data_synchronizer.frontend_data_file = self.frontend_data_file
        
        # Get sync status
        status_response = self.client.get('/api/sync/status')
        self.assertEqual(status_response.status_code, 200)
        
        status_data = status_response.json
        self.assertIn('main_file_exists', status_data)
        self.assertIn('sync_needed', status_data)
        
        # Force sync
        sync_response = self.client.post('/api/sync/force')
        self.assertEqual(sync_response.status_code, 200)
        
        # Verify frontend file was created
        self.assertTrue(self.frontend_data_file.exists())
        
        # Verify synchronized data
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            synced_data = json.load(f)
            
        self.assertEqual(synced_data, initial_data)
        
    def test_error_handling_in_api_integration(self):
        """Test error handling in API integration"""
        # Test invalid URL
        request_data = {"url": "invalid-url"}
        
        response = self.client.post('/api/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        
        # Test missing required fields
        request_data = {}
        
        response = self.client.post('/api/toc/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        # Test subprocess failure
        with patch('subprocess.run') as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stderr = "Error message"
            mock_subprocess.return_value = mock_result
            
            request_data = {"url": "http://test.onion"}
            
            response = self.client.post('/api/toc/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
            
    def test_concurrent_api_requests(self):
        """Test handling of concurrent API requests"""
        # Mock successful responses
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'<html><head><title>Test</title></head><body>Test</body></html>',
                url='http://example.com'
            )
            
            # Override data file path
            scraper_controller.integration.data_file_path = self.data_file
            
            # Make concurrent requests
            request_data = {
                "url": "http://example.com",
                "max_depth": 1,
                "max_links": 1
            }
            
            # First request should succeed
            response1 = self.client.post('/api/start',
                                       data=json.dumps(request_data),
                                       content_type='application/json')
            
            self.assertEqual(response1.status_code, 200)
            
            # Second request should fail (already running)
            response2 = self.client.post('/api/start',
                                       data=json.dumps(request_data),
                                       content_type='application/json')
            
            self.assertEqual(response2.status_code, 400)
            self.assertIn("already running", response2.json["error"])
            
    def test_api_data_consistency(self):
        """Test data consistency across API operations"""
        # Create initial data through scraping API
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                headers={'content-type': 'text/html'},
                content=b'<html><head><title>Consistency Test</title></head><body>Test</body></html>',
                url='http://example.com'
            )
            
            scraper_controller.integration.data_file_path = self.data_file
            
            request_data = {
                "url": "http://example.com",
                "max_depth": 1,
                "max_links": 1
            }
            
            response = self.client.post('/api/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            
            # Wait for completion
            time.sleep(0.5)
            
            # Verify data through sync API
            data_synchronizer.project_root = self.temp_dir
            data_synchronizer.main_data_file = self.data_file
            data_synchronizer.frontend_data_file = self.frontend_data_file
            
            sync_response = self.client.post('/api/sync/force')
            self.assertEqual(sync_response.status_code, 200)
            
            # Verify both files have same content
            with open(self.data_file, 'r', encoding='utf-8') as f:
                main_data = json.load(f)
                
            with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
                frontend_data = json.load(f)
                
            self.assertEqual(main_data, frontend_data)
            self.assertEqual(main_data['name'], 'Consistency Test')


if __name__ == '__main__':
    unittest.main()
