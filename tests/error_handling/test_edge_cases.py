#!/usr/bin/env python3
"""
Comprehensive error handling and edge case tests
Tests invalid inputs, network failures, timeouts, and malformed requests
"""

import pytest
import unittest
import json
import tempfile
import time
import threading
import requests
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import socket

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from scraper_web_interface import app
from web_scraper import WebScraper, ScrapingConfig
from scraper_integration import LiveScraperIntegration
from data_sync import DataSynchronizer
from onion_data_converters import OnionSearchConverter, TocMainConverter


class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_invalid_url_inputs(self):
        """Test handling of various invalid URL inputs"""
        invalid_urls = [
            "",  # Empty string
            "   ",  # Whitespace only
            "not-a-url",  # No protocol
            "ftp://example.com",  # Wrong protocol
            "http://",  # Incomplete URL
            "https://",  # Incomplete URL
            "javascript:alert('xss')",  # JavaScript injection
            "data:text/html,<script>alert('xss')</script>",  # Data URL
            "file:///etc/passwd",  # File URL
            "mailto:test@example.com",  # Email URL
            "tel:+1234567890",  # Phone URL
            "http://[invalid-ipv6",  # Malformed IPv6
            "http://256.256.256.256",  # Invalid IP
            "http://example.com:99999",  # Invalid port
            "http://example.com/path with spaces",  # Unencoded spaces
            "http://example.com/\x00null",  # Null byte
            "http://example.com/" + "a" * 10000,  # Extremely long URL
        ]
        
        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url):
                request_data = {"url": invalid_url, "max_depth": 1}
                
                response = self.client.post('/api/start',
                                          data=json.dumps(request_data),
                                          content_type='application/json')
                
                # Should return error for invalid URLs
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json)
                
    def test_malformed_json_requests(self):
        """Test handling of malformed JSON requests"""
        malformed_requests = [
            "",  # Empty string
            "{",  # Incomplete JSON
            '{"url": "http://example.com",}',  # Trailing comma
            '{"url": "http://example.com" "depth": 3}',  # Missing comma
            '{"url": http://example.com}',  # Unquoted value
            '{"url": "http://example.com", "depth": }',  # Missing value
            b'\xff\xfe',  # Invalid UTF-8
            '{"url": "http://example.com", "depth": NaN}',  # Invalid number
            '{"url": "http://example.com", "depth": Infinity}',  # Invalid number
        ]
        
        for malformed_json in malformed_requests:
            with self.subTest(json_data=repr(malformed_json)):
                response = self.client.post('/api/start',
                                          data=malformed_json,
                                          content_type='application/json')
                
                # Should return 400 for malformed JSON
                self.assertEqual(response.status_code, 400)
                
    def test_network_failure_scenarios(self):
        """Test handling of various network failure scenarios"""
        config = ScrapingConfig(max_depth=1, max_retries=1, timeout=1)
        scraper = WebScraper(config)
        
        # Test connection timeout
        with patch('requests.Session.get', side_effect=requests.exceptions.ConnectTimeout("Connection timeout")):
            result = scraper.fetch_page("http://example.com")
            self.assertIsNone(result)
            
        # Test read timeout
        with patch('requests.Session.get', side_effect=requests.exceptions.ReadTimeout("Read timeout")):
            result = scraper.fetch_page("http://example.com")
            self.assertIsNone(result)
            
        # Test connection error
        with patch('requests.Session.get', side_effect=requests.exceptions.ConnectionError("Connection failed")):
            result = scraper.fetch_page("http://example.com")
            self.assertIsNone(result)
            
        # Test HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        with patch('requests.Session.get', return_value=mock_response):
            result = scraper.fetch_page("http://example.com")
            self.assertIsNone(result)
            
        # Test SSL error
        with patch('requests.Session.get', side_effect=requests.exceptions.SSLError("SSL verification failed")):
            result = scraper.fetch_page("https://example.com")
            self.assertIsNone(result)
            
    def test_large_response_handling(self):
        """Test handling of extremely large responses"""
        config = ScrapingConfig(max_depth=1)
        scraper = WebScraper(config)
        
        # Create a very large HTML response
        large_html = "<html><body>" + "A" * (10 * 1024 * 1024) + "</body></html>"  # 10MB
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = large_html.encode('utf-8')
        mock_response.url = 'http://example.com'
        
        with patch('requests.Session.get', return_value=mock_response):
            # Should handle large responses gracefully
            result = scraper.fetch_page("http://example.com")
            
            # Should still return result but may be slow
            self.assertIsNotNone(result)
            soup, final_url = result
            self.assertEqual(final_url, 'http://example.com')
            
    def test_infinite_redirect_handling(self):
        """Test handling of infinite redirect loops"""
        config = ScrapingConfig(max_depth=1, max_retries=1)
        scraper = WebScraper(config)
        
        # Mock infinite redirect
        with patch('requests.Session.get', side_effect=requests.exceptions.TooManyRedirects("Too many redirects")):
            result = scraper.fetch_page("http://example.com")
            self.assertIsNone(result)
            
    def test_memory_exhaustion_scenarios(self):
        """Test handling of memory exhaustion scenarios"""
        # Test with extremely deep recursion
        config = ScrapingConfig(max_depth=1000, max_links_per_page=1000)  # Unrealistic values
        scraper = WebScraper(config)
        
        # Mock response that would cause deep recursion
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = b'<html><body><a href="http://example.com/1">Link</a></body></html>'
        mock_response.url = 'http://example.com'
        
        with patch('requests.Session.get', return_value=mock_response):
            # Should handle gracefully without stack overflow
            result = scraper.start_scraping("http://example.com")
            self.assertIsNotNone(result)
            
    def test_concurrent_access_conflicts(self):
        """Test handling of concurrent access conflicts"""
        integration = LiveScraperIntegration(str(self.data_file))
        
        # Simulate concurrent writes to the same file
        def write_data(data, delay=0):
            time.sleep(delay)
            return integration.save_data(data)
            
        data1 = {"name": "Data 1", "type": "root", "children": []}
        data2 = {"name": "Data 2", "type": "root", "children": []}
        
        # Start concurrent writes
        thread1 = threading.Thread(target=write_data, args=(data1, 0.1))
        thread2 = threading.Thread(target=write_data, args=(data2, 0.2))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # File should exist and contain valid JSON (last write wins)
        self.assertTrue(self.data_file.exists())
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
            
        # Should be one of the two data sets
        self.assertIn(final_data['name'], ['Data 1', 'Data 2'])
        
    def test_disk_space_exhaustion(self):
        """Test handling of disk space exhaustion"""
        integration = LiveScraperIntegration(str(self.data_file))
        
        # Mock disk space error
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            result = integration.save_data({"name": "test", "type": "root", "children": []})
            self.assertFalse(result)
            
    def test_permission_denied_scenarios(self):
        """Test handling of permission denied scenarios"""
        # Test read permission denied
        synchronizer = DataSynchronizer(self.temp_dir)
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = synchronizer._read_json_file(self.data_file)
            self.assertIsNone(result)
            
        # Test write permission denied
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = synchronizer._write_json_file(self.data_file, {"test": "data"})
            self.assertFalse(result)
            
    def test_corrupted_data_recovery(self):
        """Test recovery from corrupted data files"""
        # Create corrupted JSON file
        with open(self.data_file, 'w') as f:
            f.write('{"name": "test", "type": "root", "children": [')  # Incomplete JSON
            
        synchronizer = DataSynchronizer(self.temp_dir)
        
        # Should handle corrupted JSON gracefully
        result = synchronizer._read_json_file(self.data_file)
        self.assertIsNone(result)
        
        # Should not crash the system
        sync_result = synchronizer.sync_to_frontend()
        self.assertFalse(sync_result)
        
    def test_unicode_and_encoding_issues(self):
        """Test handling of Unicode and encoding issues"""
        # Test various Unicode characters
        unicode_data = {
            "name": "Test with Unicode: 🕷️🌐🔍",
            "type": "root",
            "description": "Unicode test: αβγδε 中文 العربية עברית",
            "children": [
                {
                    "name": "Emoji test: 🚀🔥💻",
                    "type": "category",
                    "description": "More Unicode: ñáéíóú",
                    "children": []
                }
            ]
        }
        
        integration = LiveScraperIntegration(str(self.data_file))
        result = integration.save_data(unicode_data)
        self.assertTrue(result)
        
        # Verify data was saved correctly
        with open(self.data_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            
        self.assertEqual(loaded_data, unicode_data)
        
    def test_extremely_long_inputs(self):
        """Test handling of extremely long inputs"""
        # Test very long URL
        long_url = "http://example.com/" + "a" * 5000
        
        request_data = {"url": long_url, "max_depth": 1}
        response = self.client.post('/api/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])
        
        # Test very long search query
        long_query = "a" * 10000
        
        request_data = {"query": long_query}
        response = self.client.post('/api/onionsearch/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])
        
    def test_null_and_undefined_values(self):
        """Test handling of null and undefined values"""
        null_value_requests = [
            {"url": None, "max_depth": 3},
            {"url": "http://example.com", "max_depth": None},
            {"url": "http://example.com"},  # Missing max_depth
            {},  # Empty request
        ]
        
        for request_data in null_value_requests:
            with self.subTest(request=request_data):
                response = self.client.post('/api/start',
                                          data=json.dumps(request_data),
                                          content_type='application/json')
                
                # Should handle null values gracefully
                self.assertIn(response.status_code, [200, 400])
                
    def test_type_mismatch_errors(self):
        """Test handling of type mismatch errors"""
        type_mismatch_requests = [
            {"url": 123, "max_depth": 3},  # URL as number
            {"url": "http://example.com", "max_depth": "three"},  # Depth as string
            {"url": ["http://example.com"], "max_depth": 3},  # URL as array
            {"url": "http://example.com", "max_depth": 3.14},  # Depth as float
            {"url": True, "max_depth": 3},  # URL as boolean
        ]
        
        for request_data in type_mismatch_requests:
            with self.subTest(request=request_data):
                response = self.client.post('/api/start',
                                          data=json.dumps(request_data),
                                          content_type='application/json')
                
                # Should handle type mismatches gracefully
                self.assertIn(response.status_code, [200, 400])
                
    def test_resource_exhaustion_scenarios(self):
        """Test handling of resource exhaustion scenarios"""
        # Test with many concurrent requests
        def make_request():
            request_data = {"url": "http://example.com", "max_depth": 1}
            return self.client.post('/api/start',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        # Start many concurrent requests
        threads = []
        for _ in range(50):  # 50 concurrent requests
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
            
        # Wait for all to complete
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
            
        # System should remain responsive
        status_response = self.client.get('/api/status')
        self.assertEqual(status_response.status_code, 200)
        
    def test_subprocess_failure_handling(self):
        """Test handling of subprocess failures"""
        # Test TOC subprocess failure
        with patch('subprocess.run', side_effect=FileNotFoundError("Command not found")):
            request_data = {"url": "http://test.onion"}
            response = self.client.post('/api/toc/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            # Should handle subprocess failure gracefully
            self.assertIn(response.status_code, [500, 400])
            
        # Test subprocess timeout
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("cmd", 30)):
            request_data = {"url": "http://test.onion"}
            response = self.client.post('/api/toc/start',
                                      data=json.dumps(request_data),
                                      content_type='application/json')
            
            # Should handle timeout gracefully
            self.assertIn(response.status_code, [500, 400])
            
    def test_data_converter_edge_cases(self):
        """Test edge cases in data converters"""
        # Test OnionSearch converter with empty CSV
        converter = OnionSearchConverter("test")
        
        empty_csv = self.temp_dir / "empty.csv"
        with open(empty_csv, 'w') as f:
            f.write("")  # Empty file
            
        result = converter.convert_csv_to_json(str(empty_csv))
        # Should handle empty CSV gracefully
        self.assertFalse(result)
        
        # Test with malformed CSV
        malformed_csv = self.temp_dir / "malformed.csv"
        with open(malformed_csv, 'w') as f:
            f.write('incomplete,line\nwith,"too,many,fields,here"\n')
            
        result = converter.convert_csv_to_json(str(malformed_csv))
        # Should handle malformed CSV gracefully
        self.assertFalse(result)
        
        # Test TOC converter with invalid JSON
        toc_converter = TocMainConverter("http://test.onion")
        result = toc_converter.process_toc_output("invalid json")
        self.assertFalse(result)
        
        # Test with empty JSON
        result = toc_converter.process_toc_output("{}")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
