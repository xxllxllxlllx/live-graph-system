# Quick Start Guide - 4-Section Scraper System

## 🚀 **Instant Setup**

### **1. Start Complete Web Interface**
```bash
# Windows
.\run.bat

# Linux/Mac
./run.sh

# Select option 2: "Complete web interface"
# Open browser to http://localhost:5000
```

### **2. Check Dependencies**
```bash
# Windows
.\run.bat --check-deps

# Linux/Mac
./run.sh --check-deps
```

## 🕷️ **4 Scraper Sections**

### **Section 1: HTTP/HTTPS Scraper** 🌐
**Purpose**: Regular website crawling
**Input**: Any HTTP/HTTPS URL
**Example**: `https://example.com`
**Features**: 
- Progressive crawling
- Configurable depth (1-10)
- Real-time updates

### **Section 2: TOC Onion Crawler** 🧅
**Purpose**: Deep .onion site exploration
**Input**: .onion URLs
**Example**: `http://example.onion`
**Requirements**: 
- TOR proxy (127.0.0.1:9050)
- Go programming language
**Features**:
- Hierarchical link traversal
- TOR network integration

### **Section 3: OnionSearch Engine** 🔍
**Purpose**: Multi-engine onion search
**Input**: Search terms
**Example**: `"privacy tools"`
**Features**:
- 15+ search engines
- Configurable result limits
- Automatic aggregation

### **Section 4: TorBot OSINT Crawler** 🤖
**Purpose**: Advanced intelligence gathering
**Input**: Any URL (HTTP/HTTPS or .onion)
**Example**: `https://example.com`
**Features**:
- ML content classification
- Email/phone extraction
- OSINT metadata analysis

## ⚡ **Direct Command Line**

### **Quick Dependency Check**
```bash
.\run.bat --check-deps    # Windows
./run.sh --check-deps     # Linux/Mac
```

### **Direct Scraper Execution**
```bash
# TOC Onion Crawler
.\run.bat --toc "http://example.onion"
./run.sh --toc "http://example.onion"

# OnionSearch Engine  
.\run.bat --onionsearch "search terms"
./run.sh --onionsearch "search terms"

# TorBot OSINT Crawler
.\run.bat --torbot "https://example.com"
./run.sh --torbot "https://example.com" 2  # depth=2
```

## 📋 **Prerequisites**

### **Required (Always)**
- ✅ Python 3.7+
- ✅ Basic Python packages (requests, beautifulsoup4)

### **For TOC Crawler**
- 🔧 Go 1.19+
- 🔧 TOR daemon (127.0.0.1:9050)

### **For OnionSearch**
- 🔧 PySocks package
- 🔧 TOR proxy (optional but recommended)

### **For TorBot**
- 🔧 httpx[socks], treelib, tabulate, toml
- 🔧 TOR proxy (optional)

## 🔧 **Quick Installation**

### **Install Missing Packages**
```bash
# OnionSearch requirements
pip install requests beautifulsoup4 PySocks tqdm

# TorBot requirements  
pip install httpx[socks] treelib tabulate toml validators

# Data synchronization (optional)
pip install watchdog
```

### **Install TOR**
```bash
# Ubuntu/Debian
sudo apt install tor && sudo systemctl start tor

# macOS
brew install tor && brew services start tor

# Windows: Download Tor Browser or Expert Bundle
```

### **Install Go (for TOC)**
```bash
# Download from https://golang.org/dl/
# Linux: sudo apt install golang-go
# macOS: brew install go
```

## 🎯 **Usage Patterns**

### **Research Workflow**
1. **Start with HTTP scraper** for surface web analysis
2. **Use OnionSearch** to find relevant .onion sites
3. **Deep dive with TOC crawler** on specific .onion sites
4. **Apply TorBot OSINT** for intelligence gathering

### **Quick Analysis**
1. **Check dependencies** first
2. **Use direct command line** for single-target analysis
3. **Web interface** for interactive exploration

### **Comprehensive Investigation**
1. **Web interface** with all 4 sections
2. **Progressive data building** across multiple scrapers
3. **Real-time graph visualization** for pattern recognition

## 📊 **Data Output**

### **All Scrapers Output To**
- **Primary**: `data/data.json`
- **Frontend**: `frontend/data/data.json` (auto-synced)
- **Format**: Unified hierarchical JSON

### **Graph Visualization**
- **URL**: http://localhost:8001
- **Updates**: Real-time automatic refresh
- **Features**: Interactive D3.js visualization

## 🚨 **Troubleshooting**

### **Common Issues**

**404 data.json Error**: ✅ **FIXED** - Automatic data synchronization
**TOR Connection Failed**: Check if TOR daemon is running on 127.0.0.1:9050
**Go Not Found**: Install Go from https://golang.org/dl/
**Python Packages Missing**: Run `pip install` commands above
**Permission Denied**: Run with appropriate user permissions

### **Quick Fixes**
```bash
# Restart TOR
sudo systemctl restart tor  # Linux
brew services restart tor   # macOS

# Check TOR status
nc -z 127.0.0.1 9050       # Should connect if TOR is running

# Verify Python packages
python -c "import requests, bs4, httpx, treelib"
```

## 🎉 **Success Indicators**

### **System Ready When**
- ✅ Dependency check shows all green checkmarks
- ✅ Web interface loads at http://localhost:5000
- ✅ Graph visualization loads at http://localhost:8001
- ✅ All 4 scraper sections show "Ready" status

### **Scraping Success When**
- ✅ Status indicators turn green with "Running"
- ✅ Activity log shows progress messages
- ✅ Graph visualization updates with new data
- ✅ data.json file contains hierarchical structure

## 🔗 **Quick Links**

- **Web Interface**: http://localhost:5000
- **Graph Visualization**: http://localhost:8001
- **Main Data File**: `data/data.json`
- **Activity Logs**: Web interface activity panel
- **Documentation**: `COMPLETE_4_SECTION_SCRAPER_INTEGRATION.md`

## 💡 **Pro Tips**

1. **Always check dependencies first** with `--check-deps`
2. **Start TOR before using onion scrapers**
3. **Use progressive mode** for HTTP scraping
4. **Monitor activity log** for real-time status
5. **Refresh graph visualization** if data doesn't appear
6. **Use appropriate depth settings** to avoid overwhelming results
7. **Combine scrapers** for comprehensive intelligence gathering

The Live Graph System now provides the most comprehensive web intelligence platform available, combining surface web, deep web, and dark web scraping capabilities in a single, unified interface.
