#!/usr/bin/env python3
"""
Unit tests for the Flask API endpoints
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os
from pathlib import Path

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

# Import Flask app and components
from scraper_web_interface import app, scraper_controller, onion_runner, progress_updates


class TestFlaskAPIEndpoints(unittest.TestCase):
    """Test Flask API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear progress updates
        global progress_updates
        progress_updates.clear()
        
    def test_index_route(self):
        """Test the main index route"""
        with patch('scraper_web_interface.render_template') as mock_render:
            mock_render.return_value = "<html>Test Template</html>"

            response = self.client.get('/')

            self.assertEqual(response.status_code, 200)
            mock_render.assert_called_once_with('scraper_interface.html')
            
    def test_status_route(self):
        """Test the status API endpoint"""
        mock_status = {
            "is_running": False,
            "current_url": None,
            "total_scraped": 0,
            "current_depth": 0
        }
        
        with patch.object(scraper_controller, 'get_status', return_value=mock_status):
            response = self.client.get('/api/status')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, mock_status)
            
    def test_start_scraping_success(self):
        """Test successful scraping start"""
        request_data = {
            "url": "http://example.com",
            "max_depth": 3,
            "max_links": 5,
            "progressive": True
        }
        
        with patch.object(scraper_controller, 'start_scraping', return_value=True):
            with patch.object(scraper_controller.integration, 'is_running', False):
                response = self.client.post('/api/start', 
                                          data=json.dumps(request_data),
                                          content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                self.assertIn("success", response.json)
                
    def test_start_scraping_missing_url(self):
        """Test scraping start with missing URL"""
        request_data = {
            "max_depth": 3,
            "max_links": 5
        }
        
        response = self.client.post('/api/start', 
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("URL is required", response.json["error"])
        
    def test_start_scraping_invalid_url(self):
        """Test scraping start with invalid URL"""
        request_data = {
            "url": "invalid-url",
            "max_depth": 3
        }
        
        response = self.client.post('/api/start', 
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("must start with http", response.json["error"])
        
    def test_start_scraping_already_running(self):
        """Test scraping start when already running"""
        request_data = {
            "url": "http://example.com",
            "max_depth": 3
        }
        
        with patch.object(scraper_controller.integration, 'is_running', True):
            response = self.client.post('/api/start', 
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            self.assertIn("error", response.json)
            self.assertIn("already running", response.json["error"])
            
    def test_stop_scraping(self):
        """Test scraping stop"""
        with patch.object(scraper_controller, 'stop_scraping'):
            response = self.client.post('/api/stop')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            
    def test_progress_route(self):
        """Test progress updates route"""
        # Add some test progress updates
        import scraper_web_interface
        scraper_web_interface.progress_updates.extend([
            {"type": "progress", "message": "Starting scrape"},
            {"type": "progress", "message": "Found 5 links"},
            {"type": "completion", "status": "success", "message": "Scraping completed"}
        ])
        
        response = self.client.get('/api/progress')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)
        self.assertEqual(response.json[0]["message"], "Starting scrape")
        
    def test_toc_start_success(self):
        """Test TOC scraper start"""
        request_data = {"url": "http://test.onion"}
        
        with patch.object(onion_runner, 'run_toc_crawler', return_value=True):
            response = self.client.post('/api/toc/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            
    def test_toc_start_missing_url(self):
        """Test TOC scraper start with missing URL"""
        request_data = {}
        
        response = self.client.post('/api/toc/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        
    def test_toc_start_failure(self):
        """Test TOC scraper start failure"""
        request_data = {"url": "http://test.onion"}
        
        with patch.object(onion_runner, 'run_toc_crawler', return_value=False):
            response = self.client.post('/api/toc/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.json)
            
    def test_onionsearch_start_success(self):
        """Test OnionSearch start"""
        request_data = {"query": "test query"}
        
        with patch.object(onion_runner, 'run_onionsearch', return_value=True):
            response = self.client.post('/api/onionsearch/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            
    def test_onionsearch_start_missing_query(self):
        """Test OnionSearch start with missing query"""
        request_data = {}
        
        response = self.client.post('/api/onionsearch/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        
    def test_onionsearch_start_failure(self):
        """Test OnionSearch start failure"""
        request_data = {"query": "test query"}
        
        with patch.object(onion_runner, 'run_onionsearch', return_value=False):
            response = self.client.post('/api/onionsearch/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.json)
            
    def test_data_sync_status(self):
        """Test data sync status endpoint"""
        mock_status = {
            "is_watching": True,
            "main_file_exists": True,
            "frontend_file_exists": True,
            "sync_needed": False,
            "last_sync_time": "2023-01-01T00:00:00"
        }
        
        with patch('scraper_web_interface.data_synchronizer') as mock_sync:
            mock_sync.get_status.return_value = mock_status
            
            response = self.client.get('/api/sync/status')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, mock_status)
            
    def test_force_sync(self):
        """Test force sync endpoint"""
        with patch('scraper_web_interface.data_synchronizer') as mock_sync:
            mock_sync.force_sync.return_value = True
            
            response = self.client.post('/api/sync/force')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("success", response.json)
            
    def test_force_sync_failure(self):
        """Test force sync failure"""
        with patch('scraper_web_interface.data_synchronizer') as mock_sync:
            mock_sync.force_sync.return_value = False
            
            response = self.client.post('/api/sync/force')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.json)
            
    def test_invalid_json_request(self):
        """Test handling of invalid JSON requests"""
        response = self.client.post('/api/start',
                                  data="invalid json",
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = self.client.post('/api/start',
                                  data='{"url": "http://example.com"}')
        
        # Should still work as Flask can handle this
        self.assertIn(response.status_code, [200, 400])  # Depends on implementation
        
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get('/api/status')
        
        # CORS should be enabled
        self.assertIn('Access-Control-Allow-Origin', response.headers)


class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/api/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        
    def test_method_not_allowed(self):
        """Test method not allowed error"""
        response = self.client.get('/api/start')  # Should be POST
        
        self.assertEqual(response.status_code, 405)
        
    @patch.object(scraper_controller, 'get_status', side_effect=Exception("Test error"))
    def test_internal_server_error(self, mock_status):
        """Test internal server error handling"""
        response = self.client.get('/api/status')
        
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
