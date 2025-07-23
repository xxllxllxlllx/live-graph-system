#!/usr/bin/env python3
"""
Pytest configuration and fixtures for the live graph system tests
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock, patch

# Add backend paths to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend" / "core"))
sys.path.append(str(project_root / "backend" / "interfaces"))
sys.path.append(str(project_root / "backend" / "config"))


@pytest.fixture
def project_root_path():
    """Fixture providing the project root path"""
    return Path(__file__).parent.parent


@pytest.fixture
def temp_data_file():
    """Fixture providing a temporary data file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            "name": "Test Root",
            "type": "root",
            "description": "Test data",
            "url": "http://test.com",
            "children": [
                {
                    "name": "Test Child",
                    "type": "category",
                    "description": "Test child",
                    "url": "http://test.com/child",
                    "children": []
                }
            ]
        }
        json.dump(test_data, f, indent=2)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_scraped_data():
    """Fixture providing sample scraped data"""
    return {
        "name": "Example Site",
        "type": "root",
        "description": "URL: http://example.com",
        "url": "http://example.com",
        "children": [
            {
                "name": "About Page",
                "type": "level1",
                "description": "URL: http://example.com/about",
                "url": "http://example.com/about",
                "children": [
                    {
                        "name": "Team Page",
                        "type": "level2",
                        "description": "URL: http://example.com/about/team",
                        "url": "http://example.com/about/team",
                        "children": []
                    }
                ]
            },
            {
                "name": "Contact Page",
                "type": "level1",
                "description": "URL: http://example.com/contact",
                "url": "http://example.com/contact",
                "children": []
            }
        ]
    }


@pytest.fixture
def sample_html_content():
    """Fixture providing sample HTML content for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Welcome to Test Page</h1>
        <nav>
            <a href="http://example.com/about">About</a>
            <a href="http://example.com/contact">Contact</a>
            <a href="http://example.com/services">Services</a>
            <a href="mailto:test@example.com">Email</a>
            <a href="#section1">Section 1</a>
            <a href="javascript:void(0)">JavaScript Link</a>
        </nav>
        <main>
            <p>This is a test page for web scraping.</p>
        </main>
    </body>
    </html>
    """


@pytest.fixture
def mock_requests_session():
    """Fixture providing a mocked requests session"""
    with patch('requests.Session') as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Configure default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html; charset=utf-8'}
        mock_response.content = b'<html><head><title>Test</title></head><body>Test content</body></html>'
        mock_response.url = 'http://example.com'
        mock_session.get.return_value = mock_response
        
        yield mock_session


@pytest.fixture
def mock_flask_app():
    """Fixture providing a mocked Flask app for testing"""
    from scraper_web_interface import app
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def sample_csv_data():
    """Fixture providing sample CSV data for onion search testing"""
    return """ahmia,"Privacy Tools","http://privacy.onion"
darksearchio,"Secure Chat","http://chat.onion"
ahmia,"Anonymous Forum","http://forum.onion"
onionland,"Marketplace","http://market.onion"
darksearchio,"News Site","http://news.onion"
"""


@pytest.fixture
def sample_toc_json():
    """Fixture providing sample TOC JSON output"""
    return {
        "name": "Test Onion Site",
        "type": "root",
        "url": "http://test.onion",
        "description": "Test onion site crawl",
        "children": [
            {
                "name": "Services",
                "type": "category",
                "url": "http://test.onion/services",
                "description": "Services page",
                "children": [
                    {
                        "name": "VPN Service",
                        "type": "item",
                        "url": "http://test.onion/services/vpn",
                        "description": "VPN service page",
                        "children": []
                    }
                ]
            }
        ]
    }


@pytest.fixture(autouse=True)
def reset_global_state():
    """Fixture to reset global state before each test"""
    # Reset progress updates
    try:
        from scraper_web_interface import progress_updates
        progress_updates.clear()
    except ImportError:
        pass
    
    yield
    
    # Cleanup after test
    try:
        from scraper_web_interface import progress_updates
        progress_updates.clear()
    except ImportError:
        pass


@pytest.fixture
def temp_directory():
    """Fixture providing a temporary directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_subprocess():
    """Fixture providing mocked subprocess functionality"""
    with patch('subprocess.run') as mock_run:
        # Configure default successful result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"name": "Test", "type": "root", "children": []}'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        yield mock_run


@pytest.fixture
def mock_file_system():
    """Fixture providing mocked file system operations"""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('builtins.open') as mock_open:
        
        # Configure default behavior
        mock_exists.return_value = True
        mock_mkdir.return_value = None
        
        yield {
            'exists': mock_exists,
            'mkdir': mock_mkdir,
            'open': mock_open
        }


# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
