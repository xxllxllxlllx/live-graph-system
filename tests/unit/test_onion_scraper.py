#!/usr/bin/env python3
"""
Unit tests for OnionScraper
Tests the onion web scraper functionality with mocked Tor connections
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from core.onion_scraper import OnionScraper, OnionScrapingConfig

class TestOnionScrapingConfig(unittest.TestCase):
    """Test OnionScrapingConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = OnionScrapingConfig()
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.max_links_per_page, 3)
        self.assertEqual(config.request_delay, 2.0)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 2)
        self.assertFalse(config.follow_external_links)
        self.assertEqual(config.tor_proxy_host, "127.0.0.1")
        self.assertEqual(config.tor_proxy_port, 9050)
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = OnionScrapingConfig(
            max_depth=3,
            max_links_per_page=5,
            request_delay=1.0,
            timeout=60,
            follow_external_links=True
        )
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.max_links_per_page, 5)
        self.assertEqual(config.request_delay, 1.0)
        self.assertEqual(config.timeout, 60)
        self.assertTrue(config.follow_external_links)

class TestOnionScraper(unittest.TestCase):
    """Test OnionScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = OnionScrapingConfig(request_delay=0)  # No delay for tests
        self.scraper = OnionScraper(self.config)
    
    def test_initialization(self):
        """Test scraper initialization"""
        self.assertIsInstance(self.scraper.config, OnionScrapingConfig)
        self.assertEqual(len(self.scraper.visited_urls), 0)
        self.assertFalse(self.scraper.is_running)
        self.assertEqual(self.scraper.total_scraped, 0)
        self.assertEqual(self.scraper.current_depth, 0)
        
        # Check session setup
        self.assertIsInstance(self.scraper.session, requests.Session)
        expected_proxy = f'socks5h://{self.config.tor_proxy_host}:{self.config.tor_proxy_port}'
        self.assertEqual(self.scraper.session.proxies['http'], expected_proxy)
        self.assertEqual(self.scraper.session.proxies['https'], expected_proxy)
    
    def test_normalize_url(self):
        """Test URL normalization"""
        # Test basic normalization
        url = "http://example.onion/path/"
        normalized = self.scraper.normalize_url(url)
        self.assertEqual(normalized, "http://example.onion/path")
        
        # Test with fragment removal
        url = "http://example.onion/path#fragment"
        normalized = self.scraper.normalize_url(url)
        self.assertEqual(normalized, "http://example.onion/path")
        
        # Test case normalization
        url = "HTTP://EXAMPLE.ONION/PATH"
        normalized = self.scraper.normalize_url(url)
        self.assertEqual(normalized, "http://example.onion/PATH")
        
        # Test root path
        url = "http://example.onion"
        normalized = self.scraper.normalize_url(url)
        self.assertEqual(normalized, "http://example.onion/")
    
    def test_is_valid_onion_url(self):
        """Test onion URL validation"""
        # Valid v2 onion URL
        self.assertTrue(self.scraper.is_valid_onion_url("http://duckduckgogg42ts72.onion"))

        # Valid v3 onion URL
        self.assertTrue(self.scraper.is_valid_onion_url("http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"))

        # Valid test domains
        self.assertTrue(self.scraper.is_valid_onion_url("http://test.onion"))
        self.assertTrue(self.scraper.is_valid_onion_url("http://example.onion"))

        # Invalid - not onion domain
        self.assertFalse(self.scraper.is_valid_onion_url("http://example.com"))

        # Invalid - too short
        self.assertFalse(self.scraper.is_valid_onion_url("http://abc.onion"))

        # Invalid - invalid characters
        self.assertFalse(self.scraper.is_valid_onion_url("http://invalid-chars.onion"))

        # Invalid - no scheme
        self.assertFalse(self.scraper.is_valid_onion_url("example.onion"))
    
    def test_extract_title(self):
        """Test title extraction from HTML"""
        # Test with title tag
        html = "<html><head><title>Test Onion Site</title></head><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = self.scraper.extract_title(soup, "http://test.onion")
        self.assertEqual(title, "Test Onion Site")
        
        # Test with h1 fallback
        html = "<html><body><h1>Main Heading</h1></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = self.scraper.extract_title(soup, "http://test.onion")
        self.assertEqual(title, "Main Heading")
        
        # Test with domain fallback
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = self.scraper.extract_title(soup, "http://test.onion")
        self.assertEqual(title, "Onion Site: test.onion")
    
    def test_extract_links(self):
        """Test link extraction from HTML"""
        base_url = "http://test.onion"
        html = """
        <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="http://test.onion/page2">Page 2</a>
            <a href="http://other.onion/page3">External</a>
            <a href="http://example.com">Regular site</a>
            <a href="#fragment">Fragment</a>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test with follow_external_links=False (default)
        links = self.scraper.extract_links(soup, base_url)
        expected_links = [
            "http://test.onion/page1",
            "http://test.onion/page2"
        ]
        self.assertEqual(len(links), 2)
        for link in expected_links:
            self.assertIn(link, links)
        
        # Test with follow_external_links=True
        self.scraper.config.follow_external_links = True
        links = self.scraper.extract_links(soup, base_url)
        self.assertIn("http://other.onion/page3", links)
    
    @patch('requests.Session.get')
    def test_fetch_onion_page_success(self, mock_get):
        """Test successful onion page fetching"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><title>Test</title></html>"
        mock_response.url = "http://test.onion"
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_onion_page("http://test.onion")
        
        self.assertIsNotNone(result)
        soup, final_url = result
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(final_url, "http://test.onion")
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_fetch_onion_page_failure(self, mock_get):
        """Test failed onion page fetching"""
        # Mock failed response
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = self.scraper.fetch_onion_page("http://test.onion")

        self.assertIsNone(result)
        # The scraper should retry max_retries times
        self.assertEqual(mock_get.call_count, self.config.max_retries)
    
    def test_create_error_node(self):
        """Test error node creation"""
        error_node = self.scraper.create_error_node("http://test.onion", "Test error")
        
        self.assertEqual(error_node["name"], "Error: test.onion")
        self.assertEqual(error_node["type"], "error")
        self.assertEqual(error_node["description"], "Test error")
        self.assertEqual(error_node["url"], "http://test.onion")
        self.assertEqual(error_node["children"], [])
    
    @patch.object(OnionScraper, 'check_tor_connection')
    @patch.object(OnionScraper, 'scrape_recursive')
    def test_start_scraping_success(self, mock_scrape, mock_tor_check):
        """Test successful scraping start"""
        mock_tor_check.return_value = True
        mock_scrape.return_value = {"name": "Test", "type": "onion_root", "children": []}
        
        result = self.scraper.start_scraping("http://test.onion")
        
        self.assertEqual(result["name"], "Test")
        self.assertTrue(mock_tor_check.called)
        self.assertTrue(mock_scrape.called)
    
    @patch.object(OnionScraper, 'check_tor_connection')
    def test_start_scraping_invalid_url(self, mock_tor_check):
        """Test scraping with invalid URL"""
        result = self.scraper.start_scraping("http://invalid.com")
        
        self.assertEqual(result["type"], "error")
        self.assertIn("Invalid onion URL", result["description"])
        self.assertFalse(mock_tor_check.called)
    
    @patch.object(OnionScraper, 'check_tor_connection')
    def test_start_scraping_no_tor(self, mock_tor_check):
        """Test scraping without Tor connection"""
        mock_tor_check.return_value = False
        
        result = self.scraper.start_scraping("http://test.onion")
        
        self.assertEqual(result["type"], "error")
        self.assertIn("Tor connection not available", result["description"])
    
    def test_stop_scraping(self):
        """Test stopping scraper"""
        self.scraper.is_running = True
        self.scraper.stop_scraping()
        self.assertFalse(self.scraper.is_running)

class TestOnionScraperIntegration(unittest.TestCase):
    """Integration tests for OnionScraper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = OnionScrapingConfig(
            max_depth=1,
            max_links_per_page=2,
            request_delay=0,
            max_retries=1
        )
        self.scraper = OnionScraper(self.config)
    
    @patch('requests.Session.get')
    def test_scrape_recursive_single_page(self, mock_get):
        """Test recursive scraping of a single page"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <head><title>Test Onion</title></head>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body>
        </html>
        """
        mock_response.url = "http://test.onion"
        mock_get.return_value = mock_response
        
        self.scraper.is_running = True
        result = self.scraper.scrape_recursive("http://test.onion")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Onion")
        self.assertEqual(result["type"], "onion_root")
        self.assertTrue(result["onion_site"])
        self.assertIsInstance(result["children"], list)

if __name__ == '__main__':
    unittest.main()
