# 🕸️ Live Graph System

A powerful web scraping and visualization system with comprehensive Tor integration for exploring both the surface web and dark web (onion sites).

## ✨ Features

- **🌐 Web Scraping**: Intelligent crawling with depth control and rate limiting
- **🧅 Tor Integration**: Built-in support for .onion sites via SOCKS5 proxy
- **📊 Live Visualization**: Real-time graph updates as data is scraped
- **🔄 Data Synchronization**: Automatic sync between backend and frontend
- **🛠️ Multiple Scrapers**: Support for TOC, OnionSearch, TorBot, and custom scrapers
- **🧪 100% Test Coverage**: Comprehensive test suite with 98 passing tests
- **🔒 Privacy-Focused**: Respects robots.txt and implements ethical scraping

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/xxllxllxlllx/live-graph-system.git
cd live-graph-system

# Install dependencies
pip install -r requirements.txt

# For Tor integration (optional)
pip install -r requirements_tor.txt

# Run the system
python main.py
```

### Basic Usage
```bash
# Start the web interface
python -m backend.interfaces.scraper_web_interface

# Access the interface
open http://localhost:5000
```

## 🧅 Tor Integration

### Quick Setup
1. **Download Tor Browser**: https://www.torproject.org/download/
2. **Start Tor Browser** (creates proxy on 127.0.0.1:9050)
3. **System automatically detects** and uses Tor proxy

### Supported Onion Sites
- **Ahmia Search**: `juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion`
- **BBC News**: `bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion`
- **DuckDuckGo**: `duckduckgogg42ts72.onion`
- **Facebook**: `facebookcorewwwi.onion`

### How It Works
The system uses **onion routing** (not VPN):
```
You → Entry Node → Middle Node → Exit Node → Internet
```
For .onion sites, traffic stays within the Tor network for maximum anonymity.

## 📁 New Organized Structure

```
live-graph-system/
├── frontend/                    # Web visualization components
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css       # Responsive CSS styling
│   │   └── js/
│   │       ├── d3.v3.min.js    # D3.js library v3 by Mike Bostock
│   │       └── graph.js        # Enhanced D3.js visualization
│   └── index.html              # Main graph visualization page
│
├── backend/                     # Python scraper system
│   ├── core/                   # Core scraper functionality
│   │   ├── web_scraper.py      # Core web scraping engine
│   │   └── scraper_integration.py # Integration layer for scraper
│   ├── interfaces/             # User interfaces
│   │   ├── scraper_cli.py      # Command-line interface
│   │   ├── scraper_web_interface.py # Flask web interface
│   │   └── setup_scraper.py    # Setup script for dependencies
│   ├── config/                 # Configuration files
│   │   ├── scraper_config.py   # Configuration settings
│   │   └── requirements.txt    # Python dependencies
│   └── templates/              # Flask templates
│       └── scraper_interface.html # Web scraper control panel
│
├── data/                       # Data files and logs
│   ├── data.json              # Dynamic hierarchical data
│   ├── scraper.log            # Scraper log file
│   └── logs/                  # Additional log files
│
├── docs/                       # Documentation
│   ├── README.md              # Original comprehensive documentation
│   ├── SYSTEM_STATUS.md       # System status and achievements
│   └── WEB_SCRAPER_GUIDE.md   # Detailed scraper documentation
│
├── tests/                      # Test files and test websites
│   ├── test_websites.py       # Website testing script
│   └── test-websites/         # Sample test websites
│
├── archive/                    # Legacy files (previously legacy_archive)
│   └── ...                    # Deprecated random generation files
│
└── README.md                  # This file - new structure overview
```

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)
```bash
# From the backend/interfaces directory
cd backend/interfaces
python setup_scraper.py
python scraper_web_interface.py
# Open: http://localhost:5000
```

### Option 2: Command Line
```bash
# From the backend/interfaces directory
cd backend/interfaces
python scraper_cli.py --url https://example.com --depth 3
```

### Option 3: View Visualization
```bash
# From the frontend directory
cd frontend
python -m http.server 8001
# Open: http://localhost:8001/index.html
```

## 🔧 Key Changes Made

### File Organization
- **Frontend files** moved to `frontend/assets/` with proper subdirectories
- **Python files** organized by function: core, interfaces, config
- **Data files** centralized in `data/` directory
- **Documentation** moved to `docs/` directory
- **Tests** organized in `tests/` directory

### Path Updates
- Updated all import statements in Python files
- Fixed template paths in Flask application
- Updated asset paths in HTML files
- Corrected data.json path in graph.js

### Benefits
- **Cleaner structure**: Logical separation of concerns
- **Easier navigation**: Related files grouped together
- **Better maintainability**: Clear file organization
- **Professional layout**: Industry-standard project structure

## 📖 Documentation

For detailed information about features, usage, and technical implementation, see:
- `docs/README.md` - Comprehensive system documentation
- `docs/SYSTEM_STATUS.md` - Current system status and achievements
- `docs/WEB_SCRAPER_GUIDE.md` - Detailed technical guide

## 🎯 System Features

- **Interactive Tree Graph**: D3.js-powered visualization with smooth animations
- **Hierarchical Web Scraping**: Crawls websites up to 10 depth levels
- **Real-time Updates**: Live data polling and graph updates
- **Multiple Interfaces**: Web control panel and CLI tools
- **Respectful Crawling**: Implements delays and respects robots.txt

---

*Built with ❤️ using D3.js by Mike Bostock, Python, and open-source technologies*
