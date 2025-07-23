# Complete Onion Scraper Usage Guide

## 🎯 **Current System Status**
✅ **Python Dependencies**: All packages installed successfully  
✅ **OnionSearch**: requests, beautifulsoup4, PySocks, tqdm  
✅ **TorBot**: httpx[socks], treelib, tabulate, toml, validators  
❌ **Go**: Not installed (required for TOC crawler)  
❌ **TOR Proxy**: Not running (required for .onion sites)  

## 🔧 **Prerequisites & Setup**

### **1. Install Go (Required for TOC Onion Crawler)**
```bash
# Windows
1. Download Go from https://golang.org/dl/
2. Download the Windows installer (.msi file) - Latest version 1.21+
3. Run the installer and follow the setup wizard
4. Restart command prompt/PowerShell
5. Verify installation: go version

# Linux/Mac
# Option 1: Package manager
sudo apt install golang-go  # Ubuntu/Debian
brew install go             # macOS with Homebrew

# Option 2: Manual installation
wget https://golang.org/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

### **2. Install TOR Proxy (Required for Onion Scrapers)**
```bash
# Windows - Method 1: Tor Browser (Easiest)
1. Download Tor Browser from https://www.torproject.org/
2. Install and run Tor Browser
3. TOR proxy will run on 127.0.0.1:9050 automatically
4. Keep Tor Browser running while using onion scrapers

# Windows - Method 2: Tor daemon only
1. Download Tor Expert Bundle from https://www.torproject.org/download/tor/
2. Extract to C:\tor\
3. Create torrc config file in C:\tor\Data\Tor\
4. Run: C:\tor\Tor\tor.exe

# Linux
sudo apt install tor
sudo systemctl start tor
sudo systemctl enable tor
# Tor will run on 127.0.0.1:9050

# macOS
brew install tor
brew services start tor
# Tor will run on 127.0.0.1:9050
```

### **3. Verify TOR Proxy is Running**
```bash
# Check if TOR proxy is accessible
python run.py --check-deps
# Should show: ✅ TOR proxy: Running on 127.0.0.1:9050

# Manual check (Windows)
netstat -an | findstr 9050

# Manual check (Linux/Mac)
netstat -an | grep 9050
```

## 🧅 **TOC Onion Crawler**

### **Description**
Deep onion network crawler that traverses .onion sites through TOR proxy and builds hierarchical link structures.

### **Prerequisites**
- ✅ Go 1.19+ installed
- ✅ TOR proxy running on 127.0.0.1:9050
- ✅ Valid .onion URL

### **Web Interface Usage**
1. **Start Web Interface**: `python run.py --web`
2. **Navigate to**: http://localhost:5000
3. **Find TOC Section**: Top-right section "🧅 TOC Onion Crawler"
4. **Configure**:
   - **Starting .onion URL**: Enter valid .onion address
   - **SOCKS5 Proxy**: Default 127.0.0.1:9050 (leave as-is)
5. **Click**: "START TOC CRAWLING"
6. **Monitor**: Real-time progress in Activity Log
7. **View Results**: Graph visualization updates automatically

### **Command Line Usage**
```bash
# Direct execution
python run.py --toc "http://example.onion"

# Interactive menu
python run.py
# Choose option 4: TOC Onion Crawler (direct)
# Enter .onion URL when prompted
```

### **Example .onion URLs for Testing**
```bash
# DuckDuckGo Onion (Search Engine)
python run.py --toc "https://duckduckgogg42ts72.onion"

# Facebook Onion
python run.py --toc "https://facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion"

# ProPublica Onion (News)
python run.py --toc "https://p53lf57qovyuvwsc6xnrppddxpr23otqjweq6cd4qc4sw7lk7u7r5qqd.onion"

# The New York Times Onion
python run.py --toc "https://nytimes3xbfgragh.onion"
```

### **Expected Output**
- **Format**: Hierarchical JSON structure in `data/data.json`
- **Content**: Nested site structure with discovered links
- **Graph**: Real-time visualization of crawled network

## 🔍 **OnionSearch Engine**

### **Description**
Multi-engine onion search aggregator that queries various dark web search engines simultaneously.

### **Prerequisites**
- ✅ Python packages: requests, beautifulsoup4, PySocks, tqdm
- ✅ TOR proxy (optional but recommended)

### **Web Interface Usage**
1. **Start Web Interface**: `python run.py --web`
2. **Navigate to**: http://localhost:5000
3. **Find OnionSearch Section**: Bottom-left section "🔍 OnionSearch Engine"
4. **Configure**:
   - **Search Query**: Enter search terms
   - **Search Engines**: Select engines (Ahmia, DarkSearch.io, etc.)
   - **Results Limit**: Set maximum results (default: 3)
5. **Click**: "START ONIONSEARCH"
6. **Monitor**: Progress in Activity Log
7. **View Results**: Aggregated results in graph visualization

### **Command Line Usage**
```bash
# Direct execution
python run.py --onionsearch "privacy tools"

# Interactive menu
python run.py
# Choose option 5: OnionSearch Engine (direct)
# Enter search query when prompted
```

### **Best Search Terms for Testing**
```bash
# Privacy & Security
python run.py --onionsearch "privacy tools"
python run.py --onionsearch "secure messaging"
python run.py --onionsearch "anonymous email"

# News & Information
python run.py --onionsearch "news sites"
python run.py --onionsearch "journalism"
python run.py --onionsearch "whistleblowing"

# Technology
python run.py --onionsearch "cryptocurrency"
python run.py --onionsearch "linux distributions"
python run.py --onionsearch "open source"
```

### **Expected Output**
- **Format**: Hierarchical JSON with search results
- **Content**: Aggregated results from multiple search engines
- **Structure**: Organized by search engine and relevance

## 🤖 **TorBot OSINT Crawler**

### **Description**
Advanced OSINT tool for intelligence gathering that analyzes content, extracts metadata, and classifies sites using machine learning.

### **Prerequisites**
- ✅ Python packages: httpx[socks], treelib, tabulate, toml, validators
- ✅ TOR proxy (optional, can be disabled)

### **Web Interface Usage**
1. **Start Web Interface**: `python run.py --web`
2. **Navigate to**: http://localhost:5000
3. **Find TorBot Section**: Bottom-right section "🤖 TorBot OSINT Crawler"
4. **Configure**:
   - **Target URL**: Regular HTTP/HTTPS or .onion URL
   - **Crawl Depth**: 1-5 levels (default: 2)
   - **SOCKS5 Settings**: Host/port or disable proxy
   - **Info Mode**: Enable to extract emails/phones
   - **Output Format**: JSON, Tree, or Table
5. **Click**: "Start TorBot OSINT"
6. **Monitor**: Live output panel with real-time statistics
7. **View Results**: Detailed OSINT data in graph

### **Command Line Usage**
```bash
# Basic usage
python run.py --torbot "https://example.com"

# With custom depth
python run.py --torbot "https://example.com" --depth 3

# Interactive menu
python run.py
# Choose option 6: TorBot OSINT Crawler (direct)
# Enter URL and depth when prompted
```

### **URL Examples for Testing**
```bash
# Regular websites (OSINT gathering)
python run.py --torbot "https://github.com" --depth 2
python run.py --torbot "https://stackoverflow.com" --depth 1
python run.py --torbot "https://reddit.com" --depth 2

# .onion sites (with TOR proxy)
python run.py --torbot "https://duckduckgogg42ts72.onion" --depth 1
python run.py --torbot "https://facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion" --depth 1

# News sites (information gathering)
python run.py --torbot "https://www.bbc.com" --depth 2
python run.py --torbot "https://www.reuters.com" --depth 1
```

### **Configuration Options**
- **Crawl Depth**: 1-5 levels (higher = more comprehensive, slower)
- **SOCKS5 Proxy**: Use TOR proxy for anonymity
- **Info Mode**: Extract emails, phone numbers, metadata
- **Output Format**: JSON (structured), Tree (hierarchical), Table (tabular)

### **Expected Output**
- **Format**: Comprehensive JSON with OSINT intelligence
- **Content**: Links, metadata, extracted information, site classification
- **Statistics**: Links found, emails extracted, phone numbers, analysis depth

## 📊 **Data Format Compatibility**

All three onion scrapers write to the same hierarchical JSON format in `data/data.json`:

```json
{
  "name": "Root Node Name",
  "type": "root",
  "description": "Description of the crawl/search",
  "url": "starting_url",
  "children": [
    {
      "name": "Child Node Name",
      "type": "category",
      "description": "URL: child_url",
      "url": "child_url",
      "children": [...]
    }
  ]
}
```

This ensures seamless integration with the graph visualization system.

## 🚀 **Quick Start Commands**

```bash
# Check all dependencies
python run.py --check-deps

# Test each scraper (after installing Go and TOR)
python run.py --toc "https://duckduckgogg42ts72.onion"
python run.py --onionsearch "privacy tools"  
python run.py --torbot "https://github.com" --depth 2

# Launch complete web interface
python run.py --web
# Navigate to http://localhost:5000
```

## ⚠️ **Important Notes**

1. **Legal Compliance**: Only crawl sites you have permission to access
2. **TOR Proxy**: Required for .onion sites, optional for regular sites
3. **Rate Limiting**: Scrapers include delays to avoid overwhelming servers
4. **Data Persistence**: Results automatically saved to `data/data.json`
5. **Graph Updates**: Visualization updates in real-time during crawling
