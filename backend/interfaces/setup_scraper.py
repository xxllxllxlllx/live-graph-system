#!/usr/bin/env python3
"""
Setup Script for Web Scraper System
Installs dependencies and sets up the scraping environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {command}")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 3.7 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required Python packages"""
    requirements_file = Path("../config/requirements.txt")
    if not requirements_file.exists():
        print("✗ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r ../config/requirements.txt",
        "Installing Python dependencies"
    )

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        "requests",
        "bs4",
        "flask",
        "flask_cors"
    ]
    
    print("\nTesting module imports...")
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    
    return True

def create_sample_config():
    """Create a sample configuration file"""
    config_content = '''# Web Scraper Configuration
# This file contains sample configurations for the web scraper

# Default scraping parameters
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_LINKS_PER_PAGE = 5
DEFAULT_REQUEST_DELAY = 1.0
DEFAULT_TIMEOUT = 10

# Sample URLs for testing
SAMPLE_URLS = [
    "https://example.com",
    "https://httpbin.org",
    "https://quotes.toscrape.com"
]

# User agent string
USER_AGENT = "LiveGraphScraper/1.0 (Educational Purpose)"

# Respect robots.txt
RESPECT_ROBOTS_TXT = True
'''
    
    with open("scraper_config.py", "w") as f:
        f.write(config_content)
    
    print("✓ Created sample configuration file: scraper_config.py")
    return True

def main():
    """Main setup function"""
    print("Web Scraper System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependency installation failed. You may need to install manually:")
        print("   pip install requests beautifulsoup4 lxml flask flask-cors")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n✗ Some required modules are not available")
        print("Please install missing dependencies and run setup again")
        sys.exit(1)
    
    # Create sample config
    create_sample_config()
    
    print("\n" + "=" * 40)
    print("✓ Setup completed successfully!")
    print("\nNext steps - Choose one of these options:")
    print("\n🚀 OPTION 1: Easy Launcher (Recommended)")
    print("   cd ../../")
    print("   python run.py --web     # Web interface")
    print("   python run.py --cli     # Command line")
    print("   python run.py --viz     # Visualization only")
    print("\n🌐 OPTION 2: Web Interface")
    print("   python scraper_web_interface.py")
    print("   Then open: http://localhost:5000")
    print("\n💻 OPTION 3: Command Line")
    print("   python scraper_cli.py --url https://example.com --depth 3")
    print("   python scraper_cli.py --interactive")
    print("\n📊 OPTION 4: Graph Visualization")
    print("   cd ../../frontend/")
    print("   python -m http.server 8001")
    print("   Then open: http://localhost:8001")
    print("\n💡 TIP: The web interface includes built-in graph visualization!")

if __name__ == "__main__":
    main()
