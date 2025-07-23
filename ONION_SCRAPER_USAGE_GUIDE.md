# Live Graph System - Complete Usage Guide

## Overview

The Live Graph System now provides a fully integrated solution for web scraping and graph visualization with support for:

1. **HTTP/HTTPS Scraping** - Regular web crawling
2. **TOC Onion Crawler** - Deep .onion site exploration  
3. **OnionSearch Engine** - Multi-engine onion search
4. **Real-time Graph Visualization** - Live D3.js visualization with automatic data synchronization

## Quick Start

### Method 1: Web Interface (Recommended)
```bash
# Windows
.\run.bat

# Linux/Mac
./run.sh

# Select option 2: "Complete web interface"
# Navigate to http://localhost:5000
```

### Method 2: Direct Command Line
```bash
# Windows
.\run.bat --web

# Linux/Mac  
./run.sh --web
```

## Data Synchronization Fix

✅ **FIXED**: The 404 data.json error has been resolved:

- **Automatic Data Sync**: Data files are now automatically synchronized between the main `data/` directory and the frontend
- **Real-time Updates**: Changes to data.json are immediately reflected in the graph visualization
- **Fallback Support**: Works with or without the watchdog library (polling mode as fallback)
- **Error Handling**: Clear error messages when data files are missing

## Enhanced Autorun Scripts

### New Command-Line Options

#### Dependency Check
```bash
# Check all dependencies and system requirements
.\run.bat --check-deps    # Windows
./run.sh --check-deps     # Linux/Mac
```

#### Direct TOC Crawler
```bash
# Run TOC onion crawler directly
.\run.bat --toc "http://example.onion"    # Windows
./run.sh --toc "http://example.onion"     # Linux/Mac
```

#### Direct OnionSearch
```bash
# Run OnionSearch directly
.\run.bat --onionsearch "privacy tools"    # Windows
./run.sh --onionsearch "privacy tools"     # Linux/Mac
```

## Prerequisites and Dependencies

### For HTTP/HTTPS Scraping
- ✅ Python 3.7+ (automatically checked)
- ✅ Standard Python libraries (included)

### For TOC Onion Crawler
- 🔧 **Go 1.19+** - [Download from golang.org](https://golang.org/dl/)
- 🔧 **TOR Daemon** - Running on 127.0.0.1:9050
  - Windows: [Tor Browser](https://www.torproject.org/download/) or [Tor Expert Bundle](https://www.torproject.org/download/tor/)
  - Linux: `sudo apt install tor && sudo systemctl start tor`
  - macOS: `brew install tor && brew services start tor`

### For OnionSearch Engine
- ✅ Python 3.7+ (automatically checked)
- 🔧 **Required packages**: `pip install requests beautifulsoup4 PySocks tqdm`
- 🔧 **TOR Proxy** - For accessing onion search engines

### Dependency Installation Commands

#### Install Go (if missing)
```bash
# Windows: Download installer from https://golang.org/dl/
# Linux
sudo apt update && sudo apt install golang-go

# macOS
brew install go
```

#### Install Python Packages
```bash
pip install requests beautifulsoup4 PySocks tqdm watchdog
```

#### Install and Start TOR
```bash
# Ubuntu/Debian
sudo apt install tor
sudo systemctl start tor
sudo systemctl enable tor

# macOS
brew install tor
brew services start tor

# Windows: Download Tor Browser or Expert Bundle
```

## Usage Examples

### 1. Web Interface (Complete Experience)
```bash
# Start the complete system
python run.py --web

# Or use autorun scripts
.\run.bat        # Windows
./run.sh         # Linux/Mac

# Then select option 2
# Navigate to http://localhost:5000
# Use any of the 3 scraper sections
```

### 2. HTTP/HTTPS Scraping
- Enter regular website URL (https://example.com)
- Set crawl depth and links per page
- Enable progressive mode for real-time updates
- Click "Start HTTP Scraping"

### 3. TOC Onion Crawler
- Ensure TOR is running (check with dependency checker)
- Enter .onion URL (http://example.onion)
- Configure SOCKS5 proxy (default: 127.0.0.1:9050)
- Click "Start TOC Crawling"

### 4. OnionSearch Engine
- Enter search terms
- Select search engines (or leave empty for all)
- Set result limit per engine (1-10)
- Click "Start OnionSearch"

### 5. Direct Command Line Usage
```bash
# Check what's available
.\run.bat --check-deps

# Direct TOC crawling
.\run.bat --toc "http://facebookcorewwwi.onion"

# Direct OnionSearch
.\run.bat --onionsearch "secure messaging"
```

## Data Output Format

All scrapers output data in the unified JSON format:

```json
{
  "name": "Root Node Name",
  "type": "root|category|subcategory|item", 
  "description": "URL: http://example.com",
  "url": "http://example.com",
  "children": [...]
}
```

**Node Types:**
- `root`: Entry point
- `category`: Major sections (search engines, site areas)
- `subcategory`: Sub-sections
- `item`: Individual pages/results

## Troubleshooting

### 404 Data.json Error
✅ **FIXED**: Automatic data synchronization now handles this

### TOR Connection Issues
```bash
# Check if TOR is running
.\run.bat --check-deps

# Start TOR manually
# Linux: sudo systemctl start tor
# macOS: brew services start tor
# Windows: Start Tor Browser or daemon
```

### Go Not Found
```bash
# Install Go from https://golang.org/dl/
# Add to PATH: export PATH=$PATH:/usr/local/go/bin
```

### Python Package Missing
```bash
# Install missing packages
pip install requests beautifulsoup4 PySocks tqdm watchdog
```

### OnionSearch Timeout
- Ensure TOR proxy is running
- Check internet connection
- Try with fewer search engines
- Increase timeout in settings

## File Structure

```
live-graph-system/
├── run.py                 # Main launcher
├── run.bat               # Windows autorun script (enhanced)
├── run.sh                # Unix autorun script (enhanced)
├── data/
│   └── data.json         # Main data file
├── frontend/
│   ├── data/             # Synchronized data (auto-created)
│   │   └── data.json     # Frontend copy (auto-synced)
│   └── index.html        # Graph visualization
├── backend/
│   ├── core/
│   │   ├── data_sync.py          # Data synchronization
│   │   └── onion_data_converters.py  # Format converters
│   └── interfaces/
│       └── scraper_web_interface.py  # Web interface
└── onions/
    ├── toc-main/         # TOC onion crawler
    └── OnionSearch-master/  # OnionSearch engine
```

## Advanced Features

### Data Synchronization
- Automatic sync between `data/data.json` and `frontend/data/data.json`
- Real-time updates in graph visualization
- Polling fallback when watchdog unavailable
- Error recovery and status reporting

### Multi-Engine OnionSearch
- Supports 15+ onion search engines
- Ahmia, DarkSearch.io, OnionLand, Phobos, Haystack, Tor66, etc.
- Configurable result limits
- Automatic result aggregation and formatting

### TOC Deep Crawling
- Hierarchical link traversal
- Automatic node classification
- TOR proxy integration
- Configurable crawl parameters

## Security Notes

- All onion scraping goes through TOR proxy
- No direct network exposure
- Isolated process execution
- Temporary file cleanup
- Safe subprocess handling

## Performance Tips

- Use progressive mode for real-time HTTP scraping
- Limit OnionSearch results for faster processing
- Monitor TOR connection stability
- Check system resources during deep crawls

The Live Graph System now provides a complete, professional solution for exploring both the regular web and the dark web through a unified interface with real-time visualization capabilities.
