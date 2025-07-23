# Live Graph System - Onion Scraper Integration

## Overview

The Live Graph System has been enhanced with a comprehensive 3-part scraper interface that supports:

1. **HTTP/HTTPS Scraper** - Traditional web scraping for regular websites
2. **TOC Onion Crawler** - Deep onion network crawling using the toc-main Go scraper
3. **OnionSearch Engine** - Multi-engine onion search using the OnionSearch-master Python tool

All three scrapers output data in the same standardized JSON format compatible with the live graph visualization.

## Architecture

### Data Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │───▶│  Backend APIs    │───▶│ Data Converters │
│   (3 Sections)  │    │  (Flask Routes)  │    │ (Format Unify)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Graph Visualiz. │◀───│   data.json      │◀───│ JSON Output     │
│ (D3.js iframe)  │    │ (Unified Format) │    │ (Standardized)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components

#### 1. Frontend (Web Interface)
- **File**: `backend/interfaces/scraper_web_interface.py` (HTML template)
- **Features**: 
  - Modern black/white monotone theme
  - Responsive 3-section layout
  - Real-time status indicators
  - Individual controls for each scraper type
  - Unified activity log
  - Embedded graph visualization

#### 2. Backend APIs
- **File**: `backend/interfaces/scraper_web_interface.py` (Flask routes)
- **Endpoints**:
  - `/api/start` - HTTP/HTTPS scraper (existing)
  - `/api/toc/start` - TOC onion crawler (new)
  - `/api/toc/stop` - Stop TOC crawler (new)
  - `/api/onionsearch/start` - OnionSearch engine (new)
  - `/api/onionsearch/stop` - Stop OnionSearch (new)

#### 3. Data Converters
- **File**: `backend/core/onion_data_converters.py`
- **Classes**:
  - `OnionSearchConverter` - Converts CSV output to JSON
  - `TocMainConverter` - Handles TOC JSON output
  - `OnionScraperRunner` - Executes scrapers and manages output

## Scraper Details

### 1. HTTP/HTTPS Scraper
- **Purpose**: Traditional web crawling for regular websites
- **Technology**: Python-based hierarchical crawler
- **Input**: Starting URL, depth, links per page
- **Output**: Direct JSON in target format
- **Features**: Progressive mode, real-time updates

### 2. TOC Onion Crawler
- **Purpose**: Deep crawling of .onion sites
- **Technology**: Go-based crawler with TOR proxy support
- **Location**: `onions/toc-main/`
- **Input**: .onion URL, SOCKS5 proxy settings
- **Output**: JSON format (already compatible from previous modifications)
- **Features**: 
  - Hierarchical link traversal
  - Automatic node type classification
  - TOR network integration

### 3. OnionSearch Engine
- **Purpose**: Search multiple onion search engines
- **Technology**: Python-based multi-engine searcher
- **Location**: `onions/OnionSearch-master/`
- **Input**: Search query, engine selection, result limits
- **Output**: CSV converted to JSON format
- **Supported Engines**:
  - Ahmia
  - DarkSearch.io
  - OnionLand
  - Phobos
  - Haystack
  - Tor66
  - And more...

## Data Format Standardization

All scrapers output data in the unified format:

```json
{
  "name": "Root Node Name",
  "type": "root|category|subcategory|item",
  "description": "URL: http://example.com",
  "url": "http://example.com",
  "children": [
    {
      "name": "Child Node",
      "type": "category",
      "description": "URL: http://child.com",
      "url": "http://child.com",
      "children": []
    }
  ]
}
```

### Node Type Classification
- **root**: Top-level entry point
- **category**: Major sections (search engines, main site areas)
- **subcategory**: Sub-sections within categories
- **item**: Individual pages/results

## Usage Instructions

### Starting the System
1. Run the Live Graph System:
   ```bash
   python run.py --web
   ```
2. Navigate to `http://localhost:5000`
3. The interface shows 3 scraper sections

### Using Each Scraper

#### HTTP/HTTPS Scraper
1. Enter a regular website URL (https://example.com)
2. Set maximum depth and links per page
3. Enable/disable progressive mode
4. Click "Start HTTP Scraping"

#### TOC Onion Crawler
1. Enter a .onion URL (http://example.onion)
2. Configure SOCKS5 proxy (default: 127.0.0.1:9050)
3. Ensure TOR is running locally
4. Click "Start TOC Crawling"

#### OnionSearch Engine
1. Enter search terms
2. Select search engines (or leave empty for all)
3. Set result limit per engine
4. Click "Start OnionSearch"

### Prerequisites

#### For TOC Crawler
- Go programming language installed
- TOR daemon running with SOCKS5 proxy on port 9050
- Access to .onion networks

#### For OnionSearch
- Python 3.7+
- Required packages: requests, bs4, PySocks, tqdm
- TOR proxy for accessing onion search engines

## Technical Implementation

### Data Conversion Process

1. **OnionSearch**: CSV → JSON conversion
   - Groups results by search engine
   - Creates hierarchical structure
   - Converts to standardized format

2. **TOC Crawler**: JSON → JSON validation
   - Already outputs correct format
   - Validates structure
   - Ensures compatibility

3. **HTTP Scraper**: Direct JSON output
   - Native format compatibility
   - Real-time structure building

### Error Handling
- Graceful failure handling for each scraper
- Clear error messages in UI
- Automatic cleanup of temporary files
- Process management for background tasks

### Performance Optimizations
- Background threading for long-running tasks
- Progress updates without blocking UI
- Efficient data structure management
- Memory-conscious log handling

## Security Considerations

### TOR Integration
- Proper SOCKS5 proxy configuration
- No direct network exposure
- Isolated process execution

### Data Handling
- Temporary file cleanup
- Sanitized input validation
- Safe subprocess execution

## Testing

Run the integration test suite:
```bash
python test_onion_integration.py
```

Tests verify:
- Data converter functionality
- CSV to JSON conversion
- JSON structure validation
- Web interface template creation
- API endpoint availability

## Future Enhancements

### Planned Features
- Concurrent scraper execution
- Result merging and deduplication
- Advanced filtering options
- Export capabilities
- Scheduling and automation

### Extensibility
- Plugin architecture for new scrapers
- Custom data format converters
- Additional visualization options
- API integration capabilities

## Troubleshooting

### Common Issues

1. **TOR Connection Failed**
   - Ensure TOR daemon is running
   - Check SOCKS5 proxy settings
   - Verify network connectivity

2. **Go Build Errors**
   - Install Go programming language
   - Check GOPATH configuration
   - Verify dependencies

3. **OnionSearch Timeout**
   - Increase timeout limits
   - Check TOR proxy status
   - Verify search engine availability

4. **Data Format Errors**
   - Run validation tests
   - Check input parameters
   - Verify file permissions

The integrated onion scraper system provides a comprehensive solution for exploring both the regular web and the dark web through a unified, modern interface with real-time graph visualization.
