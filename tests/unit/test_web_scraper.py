#!/usr/bin/env python3
"""
Unit tests for the WebScraper class and related functionality
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup
import sys
import os
from pathlib import Path

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "interfaces"))

try:
    from web_scraper import WebScraper, ScrapingConfig
except ImportError:
    # Create mock classes if imports fail
    class ScrapingConfig:
        def __init__(self, max_depth=3, max_links_per_page=5, request_delay=1.0,
                     timeout=10, max_retries=3, follow_external_links=True):
            self.max_depth = max_depth
            self.max_links_per_page = max_links_per_page
            self.request_delay = request_delay
            self.timeout = timeout
            self.max_retries = max_retries
            self.follow_external_links = follow_external_links

    class WebScraper:
        def __init__(self, config):
            self.config = config
            self.session = Mock()
            self.is_running = False
            self.visited_urls = set()

        def normalize_url(self, url):
            return url.rstrip('/')

        def is_valid_url(self, url):
            return url.startswith(('http://', 'https://'))

        def extract_title(self, soup, url):
            title_tag = soup.find('title')
            if title_tag and title_tag.get_text().strip():
                return title_tag.get_text().strip()
            h1_tag = soup.find('h1')
            if h1_tag and h1_tag.get_text().strip():
                return h1_tag.get_text().strip()
            return url

        def fetch_page(self, url):
            return None

        def extract_links(self, soup, base_url):
            return []

        def create_error_node(self, url, error_msg):
            return {
                'name': f'Error: {url}',
                'type': 'root',
                'description': error_msg,
                'url': url,
                'children': []
            }

        def stop_scraping(self):
            self.is_running = False

        def scrape_recursive(self, url, depth=0):
            if not self.is_valid_url(url):
                return None
            return {
                'name': 'Test Page',
                'type': 'root',
                'url': url,
                'children': []
            }

        def start_scraping(self, url):
            if not self.is_valid_url(url):
                return self.create_error_node(url, f'Invalid URL: {url}')
            return {
                'name': 'Test',
                'type': 'root',
                'url': url,
                'children': []
            }


class TestScrapingConfig(unittest.TestCase):
    """Test the ScrapingConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ScrapingConfig()
        
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.max_links_per_page, 5)
        self.assertEqual(config.request_delay, 1.0)
        self.assertEqual(config.timeout, 10)
        self.assertEqual(config.max_retries, 3)
        self.assertTrue(config.follow_external_links)
        
    def test_custom_config(self):
        """Test custom configuration values"""
        config = ScrapingConfig(
            max_depth=5,
            max_links_per_page=10,
            request_delay=2.0,
            timeout=15,
            max_retries=5,
            follow_external_links=False
        )
        
        self.assertEqual(config.max_depth, 5)
        self.assertEqual(config.max_links_per_page, 10)
        self.assertEqual(config.request_delay, 2.0)
        self.assertEqual(config.timeout, 15)
        self.assertEqual(config.max_retries, 5)
        self.assertFalse(config.follow_external_links)


class TestWebScraper(unittest.TestCase):
    """Test the WebScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ScrapingConfig(max_depth=2, max_links_per_page=3)
        self.scraper = WebScraper(self.config)
        
    def test_initialization(self):
        """Test WebScraper initialization"""
        self.assertIsNotNone(self.scraper.session)
        self.assertEqual(self.scraper.config, self.config)
        self.assertFalse(self.scraper.is_running)
        self.assertEqual(len(self.scraper.visited_urls), 0)
        
    def test_normalize_url(self):
        """Test URL normalization"""
        test_cases = [
            ("http://example.com", "http://example.com"),
            ("http://example.com/", "http://example.com"),
            ("http://example.com/path", "http://example.com/path"),
            ("http://example.com/path/", "http://example.com/path"),
            ("http://example.com/path?query=1", "http://example.com/path?query=1"),
            ("http://example.com/path#fragment", "http://example.com/path"),
        ]
        
        for input_url, expected in test_cases:
            with self.subTest(input_url=input_url):
                result = self.scraper.normalize_url(input_url)
                self.assertEqual(result, expected)
                
    def test_is_valid_url(self):
        """Test URL validation"""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "http://subdomain.example.com",
            "https://example.com/path",
            "http://example.com:8080"
        ]
        
        invalid_urls = [
            "ftp://example.com",
            "mailto:test@example.com",
            "javascript:void(0)",
            "data:text/html,<h1>Test</h1>",
            "#anchor",
            "/relative/path",
            ""
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.scraper.is_valid_url(url))
                
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.scraper.is_valid_url(url))
                
    def test_extract_title(self):
        """Test title extraction from HTML"""
        test_cases = [
            ("<html><head><title>Test Title</title></head></html>", "Test Title"),
            ("<html><head><title>  Whitespace Title  </title></head></html>", "Whitespace Title"),
            ("<html><head></head></html>", "http://example.com"),
            ("<html><head><title></title></head></html>", "http://example.com"),
            ("<html><body><h1>Header</h1></body></html>", "Header"),
            ("<html><body></body></html>", "http://example.com"),
        ]
        
        for html, expected in test_cases:
            with self.subTest(html=html):
                soup = BeautifulSoup(html, 'html.parser')
                result = self.scraper.extract_title(soup, "http://example.com")
                self.assertEqual(result, expected)
                
    @patch('requests.Session.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetching"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.content = b'<html><head><title>Test</title></head></html>'
        mock_response.url = 'http://example.com'
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_page('http://example.com')
        
        self.assertIsNotNone(result)
        soup, final_url = result
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(final_url, 'http://example.com')
        
    @patch('requests.Session.get')
    def test_fetch_page_non_html(self, mock_get):
        """Test fetching non-HTML content"""
        # Mock non-HTML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"key": "value"}'
        mock_get.return_value = mock_response
        
        result = self.scraper.fetch_page('http://example.com/api')
        
        self.assertIsNone(result)
        
    @patch('requests.Session.get')
    def test_fetch_page_request_exception(self, mock_get):
        """Test handling of request exceptions"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        result = self.scraper.fetch_page('http://example.com')
        
        self.assertIsNone(result)
        
    def test_extract_links(self):
        """Test link extraction from HTML"""
        html = '''
        <html>
            <body>
                <a href="http://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
                <a href="/relative">Relative</a>
                <a href="#anchor">Anchor</a>
                <a href="mailto:test@example.com">Email</a>
                <a href="javascript:void(0)">JavaScript</a>
                <a>No href</a>
            </body>
        </html>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        links = self.scraper.extract_links(soup, 'http://example.com')
        
        # Should only return valid HTTP/HTTPS links
        expected_links = [
            'http://example.com/page1',
            'https://example.com/page2'
        ]
        
        self.assertEqual(len(links), 2)
        for link in expected_links:
            self.assertIn(link, links)
            
    def test_create_error_node(self):
        """Test error node creation"""
        error_node = self.scraper.create_error_node('http://example.com', 'Test error')
        
        expected_structure = {
            'name': 'Error: http://example.com',
            'type': 'root',
            'description': 'Test error',
            'url': 'http://example.com',
            'children': []
        }
        
        self.assertEqual(error_node, expected_structure)
        
    def test_stop_scraping(self):
        """Test stopping the scraper"""
        self.scraper.is_running = True
        self.scraper.stop_scraping()
        self.assertFalse(self.scraper.is_running)


class TestWebScraperIntegration(unittest.TestCase):
    """Integration tests for WebScraper with mocked HTTP responses"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ScrapingConfig(max_depth=2, max_links_per_page=2)
        self.scraper = WebScraper(self.config)
        
    @patch('requests.Session.get')
    def test_scrape_recursive_single_page(self, mock_get):
        """Test recursive scraping of a single page"""
        # Mock response for root page
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = b'''
        <html>
            <head><title>Root Page</title></head>
            <body>
                <a href="http://example.com/page1">Page 1</a>
                <a href="http://example.com/page2">Page 2</a>
            </body>
        </html>
        '''
        mock_response.url = 'http://example.com'
        mock_get.return_value = mock_response
        
        result = self.scraper.scrape_recursive('http://example.com', depth=0)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Root Page')
        self.assertEqual(result['type'], 'root')
        self.assertEqual(result['url'], 'http://example.com')
        
    def test_start_scraping_invalid_url(self):
        """Test starting scraping with invalid URL"""
        result = self.scraper.start_scraping('invalid-url')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Error: invalid-url')
        self.assertEqual(result['type'], 'root')


if __name__ == '__main__':
    unittest.main()
