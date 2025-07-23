# Live Graph System with Web Scraper

A comprehensive web scraping and graph visualization system that crawls websites hierarchically and displays the data as interactive, animated graphs in real-time.

## 🙏 Acknowledgments

This project builds upon several excellent open-source technologies:

- **[D3.js](https://d3js.org/)** by Mike Bostock - The powerful data visualization library that powers our interactive graphs
- **[OSINT Framework](https://github.com/lockfale/OSINT-Framework)** by lockfale - Original inspiration for the tree visualization structure
- **Graph Animation Concepts** - Inspired by various D3.js tree and network visualization examples from the D3.js community
- **Python Libraries**: requests, BeautifulSoup, Flask, and their respective maintainers for robust web scraping capabilities

## 🚀 Features

### Core Visualization
- **Interactive Tree Graph**: Click nodes to expand/collapse branches
- **Responsive Design**: Adapts to different screen sizes and devices
- **Clean Styling**: Matches the original OSINT Framework's simple black and white node design
- **Smooth Animations**: Enhanced animated transitions with fade-in effects for new nodes
- **Tooltips**: Hover over nodes to see descriptions

### Web Scraping System (NEW!)
- **Hierarchical Website Crawling**: Recursively scrapes websites up to 10 depth levels
- **Smart URL Extraction**: Intelligently extracts and filters valid webpage links
- **Duplicate Prevention**: Avoids re-scraping the same URLs
- **Respectful Crawling**: Implements delays, respects robots.txt, and proper User-Agent headers
- **Real-time Integration**: Scraped data immediately reflects in the live graph visualization
- **Error Handling**: Robust handling of timeouts, failed requests, and invalid URLs

### Web Scraping Data Generation
- **Real-time Updates**: Automatic detection and reflection of scraped data changes
- **Hierarchical Website Crawling**: Recursively scrapes websites up to 10 depth levels
- **Smart URL Extraction**: Intelligently extracts and filters valid webpage links
- **Controlled Execution**: Configurable depth and link limits for scraping
- **Duplicate Prevention**: Avoids re-scraping the same URLs
- **Realistic Content**: Uses actual website titles and URLs as node content

### Control Systems
- **Web Scraper Interface**: Dedicated Flask-based control panel for web scraping
- **Command-line Interface**: Python CLI tools with interactive and direct modes
- **Interactive Mode**: Python CLI with interactive commands for scraping control
- **Start/Stop Controls**: Full control over the scraping process
- **Real-time Monitoring**: Live activity logs and status updates for scraping progress
- **Configurable Parameters**: Adjustable depth, links per page, delays, and scraping modes

## 📁 Project Structure

```
live-graph-system/
├── Core Visualization (D3.js-based)
│   ├── index.html                # Main graph visualization page
│   ├── graph.js                  # Enhanced D3.js visualization with live updates
│   ├── style.css                 # Responsive CSS styling
│   ├── d3.v3.min.js             # D3.js library v3 by Mike Bostock
│   └── data.json                # Dynamic hierarchical data (updated by scraper)
│
├── Web Scraper System (Python)
│   ├── web_scraper.py            # Core web scraping engine
│   ├── scraper_integration.py    # Integration layer for scraper
│   ├── scraper_cli.py            # Command-line interface for scraper
│   ├── scraper_web_interface.py  # Flask web interface for scraper
│   ├── setup_scraper.py          # Setup script for scraper dependencies
│   ├── requirements.txt          # Python dependencies
│   └── scraper_config.py         # Configuration file
│
├── Web Interface Templates
│   └── templates/
│       └── scraper_interface.html # Web scraper control panel
│
├── Documentation & Logs
│   ├── README.md                 # This documentation
│   ├── WEB_SCRAPER_GUIDE.md      # Detailed scraper documentation
│   ├── CLEANUP_SUMMARY.md        # System cleanup documentation
│   └── logs/                     # Log files directory
│
└── Legacy Archive (Cleaned/Deprecated)
    └── legacy_archive/
        └── README_LEGACY.md      # Legacy system documentation
```

## 🎮 Usage Options

### Option 1: Web Scraper Interface (Recommended)
1. Install Python dependencies:
   ```bash
   python setup_scraper.py
   ```

2. Start the web scraper interface:
   ```bash
   python scraper_web_interface.py
   ```

3. Open the scraper control panel:
   ```
   http://localhost:5000
   ```

4. Use the interface to:
   - Enter a starting URL (e.g., https://example.com)
   - Configure scraping parameters (depth, links per page)
   - Start/stop the web scraping process
   - Monitor real-time scraping progress
   - View the live graph visualization with scraped data

### Option 2: Command Line Web Scraper
1. Interactive mode:
   ```bash
   python scraper_cli.py --interactive
   ```

2. Direct scraping:
   ```bash
   python scraper_cli.py --url https://example.com --depth 3 --links 5
   ```

3. Progressive scraping with real-time updates:
   ```bash
   python scraper_cli.py --url https://news.ycombinator.com --progressive
   ```

### Option 3: Direct Graph Visualization
1. Start a local web server:
   ```bash
   python -m http.server 8001
   ```

2. Open the graph directly:
   ```
   http://localhost:8001/index.html
   ```

3. The graph will display data from the most recent scraping session
   (Run scraper first to populate data.json)

## ⚙️ Configuration Options

### Scraping Parameters
- **Max Depth**: 1-10 levels (default: 3)
- **Links per Page**: 1-20 links (default: 5)
- **Request Delay**: 0.5-5 seconds between requests (default: 1.0)
- **Progressive Mode**: Real-time updates during scraping (default: enabled)

### Data Structure
Each scraped node follows this structure:
```json
{
  "name": "Website Page Title",
  "type": "root|category|subcategory|item",
  "description": "URL: https://example.com/page",
  "url": "https://example.com/page",
  "children": []  // Optional array of child nodes
}
```

## 🔧 Technical Implementation

### Web Scraping Engine
- Hierarchical website crawling with configurable depth limits
- Smart URL extraction and filtering (excludes images, PDFs, etc.)
- Duplicate URL prevention with visited URL tracking
- Respectful crawling with delays and robots.txt compliance

### Real-time Data Integration
- Polls `data.json` every 1 second for changes
- Uses simple hash comparison to detect updates
- Triggers smooth graph updates when scraping completes

### Animation System
- Enhanced entrance animations for new scraped nodes
- Fade-in effects with opacity transitions
- Smooth positioning transitions using D3.js
- Maintains existing expand/collapse animations

### Data Transformation
- Converts scraped website data to D3.js-compatible format
- Maps scraping depths to graph node types
- Uses actual website titles and URLs as node content
- Maintains proper tree structure (root → category → subcategory → item)

### Error Handling & Monitoring
- Comprehensive logging system with file and console output
- Graceful handling of network timeouts and failed requests
- Real-time progress updates and status monitoring
- Configurable retry logic and error recovery

## 🎯 Web Scraping Strategy

The system uses a sophisticated approach to crawl websites hierarchically:

1. **URL Analysis**: Extracts and validates all links from each webpage
2. **Smart Filtering**: Excludes non-webpage content (images, PDFs, etc.)
3. **Depth Control**: Recursively crawls up to configurable depth levels
4. **Duplicate Prevention**: Tracks visited URLs to avoid re-scraping
5. **Content Extraction**: Uses actual page titles and URLs as node data
6. **Real-time Updates**: Progressively updates the graph as scraping proceeds

## 🚦 System Requirements

- **Python 3.7+** for web scraping functionality
- **Modern web browser** with JavaScript enabled and D3.js support
- **Local web server** (Python HTTP server recommended)
- **Internet connection** for website crawling
- **Python packages**: requests, beautifulsoup4, lxml, flask, flask-cors

### Browser Compatibility
- Chrome/Chromium 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- Any browser with ES6 and SVG support for D3.js visualizations

## 🎨 Customization

### Modifying Scraping Behavior
Edit the `ScrapingConfig` class in `web_scraper.py` to adjust:
- Maximum depth levels
- Links per page limits
- Request delays and timeouts
- User agent strings

### Customizing Data Transformation
Modify the `transform_scraped_data` function in `scraper_integration.py` to change how scraped data is converted to graph format.

### Adjusting Animation Timing
Edit the `duration` variable in `graph.js` to change animation speed.

### Adding URL Filters
Extend the `is_valid_url` method in `web_scraper.py` to add custom URL filtering rules.

## 📜 Credits and Licenses

### Core Technologies

#### D3.js - Data-Driven Documents
- **Author**: Mike Bostock
- **License**: BSD 3-Clause License
- **Website**: https://d3js.org/
- **GitHub**: https://github.com/d3/d3
- **Usage**: Powers all graph visualizations, animations, and interactive features
- **Version**: 3.x (included as d3.v3.min.js)

#### OSINT Framework Inspiration
- **Author**: lockfale
- **License**: MIT License
- **GitHub**: https://github.com/lockfale/OSINT-Framework
- **Usage**: Original inspiration for hierarchical tree visualization structure

### Python Libraries

#### Web Scraping Stack
- **requests** - HTTP library for Python (Apache 2.0 License)
- **BeautifulSoup4** - HTML/XML parsing library (MIT License)
- **lxml** - XML and HTML processing library (BSD License)

#### Web Interface Stack
- **Flask** - Micro web framework (BSD 3-Clause License)
- **Flask-CORS** - Cross-Origin Resource Sharing extension (MIT License)

### Visualization Concepts
- **Tree Layout Algorithm**: Based on D3.js hierarchical layouts
- **Animation Techniques**: Inspired by D3.js community examples and Mike Bostock's work
- **Interactive Graph Patterns**: Following D3.js best practices for data visualization

### Original Contributions
- **Web Scraping Engine**: Custom Python implementation for hierarchical website crawling
- **Data Integration Layer**: Custom transformation between scraped data and D3.js format
- **Real-time Update System**: Custom polling and animation integration
- **Flask Control Interface**: Custom web interface for scraper management
- **CLI Tools**: Custom command-line interface for scraper control

## 📄 License

This project is released under the MIT License, maintaining compatibility with all included open-source components.

### Third-Party License Compliance
- D3.js (BSD 3-Clause) - Compatible with MIT
- Flask ecosystem (BSD/MIT) - Compatible with MIT
- Python libraries (Apache 2.0/MIT/BSD) - Compatible with MIT

## 🤝 Contributing

Contributions are welcome! Please ensure any contributions:
1. Maintain compatibility with existing D3.js visualizations
2. Follow Python PEP 8 style guidelines for scraper components
3. Include appropriate tests for new functionality
4. Respect the licenses of all included third-party components

## 📞 Support

For issues related to:
- **D3.js visualizations**: Refer to [D3.js documentation](https://d3js.org/)
- **Web scraping**: Check Python requests and BeautifulSoup documentation
- **System integration**: Review the WEB_SCRAPER_GUIDE.md

---

*Built with ❤️ using D3.js, Python, and open-source technologies*
