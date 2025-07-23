#!/usr/bin/env python3
"""
Performance tests for the live graph system
Tests response times, memory usage, and scalability
"""

import pytest
import unittest
import json
import tempfile
import time
import threading
import psutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import gc
import tracemalloc

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from scraper_web_interface import app
from web_scraper import WebScraper, ScrapingConfig
from scraper_integration import LiveScraperIntegration
from data_sync import DataSynchronizer
from onion_data_converters import OnionSearchConverter


class TestPerformance(unittest.TestCase):
    """Test performance characteristics of the system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        
        # Start memory tracking
        tracemalloc.start()
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Stop memory tracking
        tracemalloc.stop()
        
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Force garbage collection
        gc.collect()
        
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
        
    def measure_memory(self, func, *args, **kwargs):
        """Measure memory usage of a function"""
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory snapshot
        snapshot_before = tracemalloc.take_snapshot()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Get final memory snapshot
        snapshot_after = tracemalloc.take_snapshot()
        
        # Calculate memory difference
        top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        total_memory = sum(stat.size_diff for stat in top_stats)
        
        return result, total_memory
        
    def test_api_response_times(self):
        """Test API endpoint response times"""
        # Test status endpoint
        start_time = time.time()
        response = self.client.get('/api/status')
        status_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(status_time, 0.1)  # Should respond in under 100ms
        
        # Test progress endpoint
        start_time = time.time()
        response = self.client.get('/api/progress')
        progress_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(progress_time, 0.1)  # Should respond in under 100ms
        
        # Test sync status endpoint
        start_time = time.time()
        response = self.client.get('/api/sync/status')
        sync_status_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(sync_status_time, 0.2)  # Should respond in under 200ms
        
    @patch('requests.Session.get')
    def test_scraping_performance(self, mock_get):
        """Test web scraping performance with various dataset sizes"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.url = 'http://example.com'
        
        # Test with small dataset
        small_html = '''
        <html>
            <head><title>Small Page</title></head>
            <body>
                <a href="http://example.com/1">Link 1</a>
                <a href="http://example.com/2">Link 2</a>
            </body>
        </html>
        '''
        
        mock_response.content = small_html.encode('utf-8')
        mock_get.return_value = mock_response
        
        config = ScrapingConfig(max_depth=2, max_links_per_page=5, request_delay=0)
        scraper = WebScraper(config)
        
        result, scraping_time = self.measure_time(scraper.start_scraping, "http://example.com")
        
        self.assertIsNotNone(result)
        self.assertLess(scraping_time, 5.0)  # Should complete in under 5 seconds
        
        # Test with medium dataset
        medium_html = '''
        <html>
            <head><title>Medium Page</title></head>
            <body>
        ''' + ''.join([f'<a href="http://example.com/{i}">Link {i}</a>' for i in range(20)]) + '''
            </body>
        </html>
        '''
        
        mock_response.content = medium_html.encode('utf-8')
        
        result, scraping_time = self.measure_time(scraper.start_scraping, "http://example.com")
        
        self.assertIsNotNone(result)
        self.assertLess(scraping_time, 10.0)  # Should complete in under 10 seconds
        
    def test_data_synchronization_performance(self):
        """Test data synchronization performance with various file sizes"""
        synchronizer = DataSynchronizer(self.temp_dir)
        
        # Test with small data file
        small_data = {
            "name": "Small Data",
            "type": "root",
            "children": [
                {"name": f"Item {i}", "type": "item", "description": f"Item {i}", "children": []}
                for i in range(10)
            ]
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(small_data, f, indent=2)
            
        result, sync_time = self.measure_time(synchronizer.sync_to_frontend)
        
        self.assertTrue(result)
        self.assertLess(sync_time, 1.0)  # Should sync in under 1 second
        
        # Test with large data file
        large_data = {
            "name": "Large Data",
            "type": "root",
            "children": []
        }
        
        # Generate 1000 items
        for i in range(1000):
            large_data["children"].append({
                "name": f"Item {i}",
                "type": "item",
                "description": f"Description for item {i} with some additional text to increase size",
                "url": f"http://example.com/item/{i}",
                "children": []
            })
            
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(large_data, f, indent=2)
            
        result, sync_time = self.measure_time(synchronizer.sync_to_frontend)
        
        self.assertTrue(result)
        self.assertLess(sync_time, 5.0)  # Should sync in under 5 seconds
        
    def test_memory_usage_during_operations(self):
        """Test memory usage during various operations"""
        # Test memory usage during data conversion
        converter = OnionSearchConverter("performance test")
        
        # Add many search results
        for engine in ['ahmia', 'darksearch', 'onionland']:
            results = [
                {"title": f"Result {i}", "url": f"http://test{i}.onion"}
                for i in range(100)
            ]
            converter.add_search_engine_result(engine, results)
            
        result, memory_used = self.measure_memory(converter.save_to_file, str(self.data_file))
        
        self.assertTrue(result)
        # Memory usage should be reasonable (less than 50MB for this test)
        self.assertLess(memory_used, 50 * 1024 * 1024)
        
    def test_concurrent_request_performance(self):
        """Test performance under concurrent load"""
        num_threads = 20
        request_times = []
        
        def make_request():
            start_time = time.time()
            response = self.client.get('/api/status')
            end_time = time.time()
            
            request_times.append(end_time - start_time)
            return response.status_code
            
        # Start concurrent requests
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
            
        # Wait for all requests to complete
        for thread in threads:
            thread.join()
            
        # Analyze performance
        avg_response_time = sum(request_times) / len(request_times)
        max_response_time = max(request_times)
        
        # Average response time should be reasonable
        self.assertLess(avg_response_time, 0.5)  # Under 500ms average
        
        # Maximum response time should not be excessive
        self.assertLess(max_response_time, 2.0)  # Under 2 seconds max
        
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create a very large dataset
        large_dataset = {
            "name": "Very Large Dataset",
            "type": "root",
            "description": "Performance test with large dataset",
            "children": []
        }
        
        # Generate hierarchical data: 50 categories with 100 items each
        for cat_i in range(50):
            category = {
                "name": f"Category {cat_i}",
                "type": "category",
                "description": f"Category {cat_i} description",
                "children": []
            }
            
            for item_i in range(100):
                item = {
                    "name": f"Item {cat_i}-{item_i}",
                    "type": "item",
                    "description": f"Item {cat_i}-{item_i} with detailed description and metadata",
                    "url": f"http://example.com/category/{cat_i}/item/{item_i}",
                    "children": []
                }
                category["children"].append(item)
                
            large_dataset["children"].append(category)
            
        # Test JSON serialization performance
        result, serialization_time = self.measure_time(json.dumps, large_dataset)
        
        self.assertIsNotNone(result)
        self.assertLess(serialization_time, 2.0)  # Should serialize in under 2 seconds
        
        # Test file I/O performance
        result, write_time = self.measure_time(
            lambda: self._write_json_file(self.data_file, large_dataset)
        )
        
        self.assertTrue(result)
        self.assertLess(write_time, 3.0)  # Should write in under 3 seconds
        
        # Test file reading performance
        result, read_time = self.measure_time(
            lambda: self._read_json_file(self.data_file)
        )
        
        self.assertIsNotNone(result)
        self.assertLess(read_time, 2.0)  # Should read in under 2 seconds
        
    def _write_json_file(self, file_path, data):
        """Helper method to write JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
        
    def _read_json_file(self, file_path):
        """Helper method to read JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def test_cpu_usage_during_operations(self):
        """Test CPU usage during intensive operations"""
        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        
        # Perform CPU-intensive operation
        config = ScrapingConfig(max_depth=3, max_links_per_page=10, request_delay=0)
        scraper = WebScraper(config)
        
        # Mock many HTTP responses
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.content = b'''
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <a href="http://example.com/1">Link 1</a>
                    <a href="http://example.com/2">Link 2</a>
                    <a href="http://example.com/3">Link 3</a>
                </body>
            </html>
            '''
            mock_response.url = 'http://example.com'
            mock_get.return_value = mock_response
            
            start_time = time.time()
            result = scraper.start_scraping("http://example.com")
            end_time = time.time()
            
        # Get final CPU usage
        final_cpu = process.cpu_percent()
        
        self.assertIsNotNone(result)
        
        # CPU usage should not be excessive
        # Note: This test may be flaky depending on system load
        operation_time = end_time - start_time
        if operation_time > 1.0:  # Only check if operation took significant time
            self.assertLess(final_cpu, 90.0)  # Should not use more than 90% CPU
            
    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations"""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform repeated operations
        for i in range(100):
            # Create and destroy objects repeatedly
            converter = OnionSearchConverter(f"test query {i}")
            converter.add_search_engine_result("test_engine", [
                {"title": f"Result {j}", "url": f"http://test{j}.onion"}
                for j in range(10)
            ])
            
            # Save to temporary file
            temp_file = self.temp_dir / f"temp_{i}.json"
            converter.save_to_file(str(temp_file))
            
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
                
            # Force garbage collection every 10 iterations
            if i % 10 == 0:
                gc.collect()
                
        # Force final garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
        
    def test_database_operation_performance(self):
        """Test performance of database-like operations"""
        # Create a dataset that simulates database operations
        data = {
            "name": "Database Test",
            "type": "root",
            "children": []
        }
        
        # Add 1000 records
        for i in range(1000):
            record = {
                "name": f"Record {i}",
                "type": "item",
                "description": f"Record {i} description",
                "id": i,
                "timestamp": time.time(),
                "children": []
            }
            data["children"].append(record)
            
        # Test "insert" performance (adding new records)
        start_time = time.time()
        for i in range(100):
            new_record = {
                "name": f"New Record {i}",
                "type": "item",
                "description": f"New record {i} description",
                "id": 1000 + i,
                "timestamp": time.time(),
                "children": []
            }
            data["children"].append(new_record)
        insert_time = time.time() - start_time
        
        self.assertLess(insert_time, 1.0)  # Should insert 100 records in under 1 second
        
        # Test "search" performance (finding records)
        start_time = time.time()
        found_records = []
        for child in data["children"]:
            if "Record 5" in child["name"]:
                found_records.append(child)
        search_time = time.time() - start_time
        
        self.assertLess(search_time, 0.1)  # Should search in under 100ms
        self.assertGreater(len(found_records), 0)
        
        # Test "update" performance (modifying records)
        start_time = time.time()
        for child in data["children"][:100]:  # Update first 100 records
            child["description"] = f"Updated: {child['description']}"
            child["last_modified"] = time.time()
        update_time = time.time() - start_time
        
        self.assertLess(update_time, 0.5)  # Should update 100 records in under 500ms


if __name__ == '__main__':
    unittest.main()
