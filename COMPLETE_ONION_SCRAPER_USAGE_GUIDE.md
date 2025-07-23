# Complete Onion Scraper Usage Guide - All 4 Sections

## 🎯 **Quick Start - All Issues Resolved**

### ✅ **Data Clearing**: Each new scraping session automatically clears both data.json files
### ✅ **Autorun Scripts**: Enhanced with help text and error handling  
### ✅ **4-Section Interface**: TorBot section properly integrated and visible

## 🚀 **Starting the Onion Scrapers**

### **Method 1: Web Interface (Recommended)**

1. **Start the complete system:**
```bash
# Windows
.\run.bat

# Linux/Mac  
./run.sh

# Select option 2: "Complete web interface"
# Navigate to http://localhost:5000
```

2. **Use any of the 4 scraper sections:**
   - **🌐 HTTP/HTTPS Scraper** (top-left)
   - **🧅 TOC Onion Crawler** (top-right)  
   - **🔍 OnionSearch Engine** (bottom-left)
   - **🤖 TorBot OSINT Crawler** (bottom-right)

### **Method 2: Direct Command Line**

**Get Help:**
```bash
.\run.bat --help        # Windows
./run.sh --help         # Linux/Mac
```

**Check Dependencies:**
```bash
.\run.bat --check-deps  # Windows
./run.sh --check-deps   # Linux/Mac
```

**Direct Scraper Execution:**
```bash
# TOC Onion Crawler
.\run.bat --toc "http://example.onion"
./run.sh --toc "http://example.onion"

# OnionSearch Engine
.\run.bat --onionsearch "privacy tools"
./run.sh --onionsearch "privacy tools"

# TorBot OSINT Crawler
.\run.bat --torbot "https://example.com"
./run.sh --torbot "https://example.com" 3  # depth=3
```

## 📋 **Prerequisites and Dependencies**

### **Universal Requirements**
- ✅ **Python 3.7+** (required for all scrapers)
- ✅ **Basic packages**: `requests`, `beautifulsoup4`

### **TOC Onion Crawler Requirements**
- 🔧 **Go 1.19+**: [Download from golang.org](https://golang.org/dl/)
- 🔧 **TOR Daemon**: Running on 127.0.0.1:9050
  ```bash
  # Ubuntu/Debian
  sudo apt install tor && sudo systemctl start tor
  
  # macOS
  brew install tor && brew services start tor
  
  # Windows: Download Tor Browser or Expert Bundle
  ```

### **OnionSearch Engine Requirements**
- 🔧 **Python packages**: 
  ```bash
  pip install requests beautifulsoup4 PySocks tqdm
  ```
- 🔧 **TOR Proxy** (optional but recommended for accessing onion search engines)

### **TorBot OSINT Crawler Requirements**
- 🔧 **Python packages**:
  ```bash
  pip install httpx[socks] beautifulsoup4 treelib tabulate toml validators
  ```
- 🔧 **TOR Proxy** (optional, can run with `--disable-socks5`)

## 🖥️ **Web Interface Usage**

### **4-Section Layout**
```
┌─────────────────────┬─────────────────────┐
│  🌐 HTTP/HTTPS      │  🧅 TOC Onion       │
│     Scraper         │     Crawler         │
├─────────────────────┼─────────────────────┤
│  🔍 OnionSearch     │  🤖 TorBot OSINT    │
│     Engine          │     Crawler         │
└─────────────────────┴─────────────────────┘
```

### **Section 1: HTTP/HTTPS Scraper** 🌐
- **Input**: Regular website URL (`https://example.com`)
- **Controls**: URL, max depth (1-10), links per page, progressive mode
- **Use Case**: Surface web crawling and analysis

### **Section 2: TOC Onion Crawler** 🧅
- **Input**: .onion URL (`http://example.onion`)
- **Controls**: URL, SOCKS5 proxy settings (127.0.0.1:9050)
- **Use Case**: Deep exploration of onion sites

### **Section 3: OnionSearch Engine** 🔍
- **Input**: Search terms (`"privacy tools"`)
- **Controls**: Search query, engines selection, results limit
- **Use Case**: Finding onion sites across multiple search engines

### **Section 4: TorBot OSINT Crawler** 🤖
- **Input**: Any URL (HTTP/HTTPS or .onion)
- **Controls**: URL, crawl depth, SOCKS5 proxy, disable proxy option
- **Use Case**: Advanced intelligence gathering with ML analysis

## 📱 **Enhanced Autorun Scripts**

### **New Help System**
```bash
# Get complete usage guide
.\run.bat --help        # Windows
./run.sh --help         # Linux/Mac
```

**Output includes:**
- Standard usage options
- Onion scraper direct usage
- Practical examples
- Requirements summary
- Setup guidance

### **Improved Error Handling**

**Missing Arguments:**
```bash
# Before: Silent failure or unclear error
# Now: Clear usage instructions with examples

.\run.bat --toc
# ERROR: Please provide a .onion URL
# Usage: run.bat --toc "http://example.onion"
# Example: run.bat --toc "http://facebookcorewwwi.onion"
```

**Missing Dependencies:**
```bash
# Before: Cryptic error messages
# Now: Clear dependency guidance

.\run.bat --torbot "https://example.com"
# ERROR: Required Python packages not found
# Please install: pip install httpx[socks] beautifulsoup4 treelib tabulate toml
```

**Directory Not Found:**
```bash
# Before: Generic error
# Now: Specific path and solution

.\run.bat --toc "http://example.onion"
# ERROR: TOC directory not found at onions\toc-main
# Please ensure the toc-main directory exists
```

## 🔄 **Data Management**

### **Automatic Data Clearing**
- ✅ **Every new scraping session** automatically clears both data.json files
- ✅ **Main file**: `data/data.json` 
- ✅ **Frontend file**: `frontend/data/data.json`
- ✅ **Fresh start**: No data contamination between sessions

### **Real-time Synchronization**
- 📊 **Automatic sync** between main and frontend data files
- 👁️ **File watcher** with polling fallback
- 🔄 **Instant updates** in graph visualization

## 🎯 **Usage Examples**

### **Complete Web Interface Session**
```bash
# 1. Start system
.\run.bat
# Select option 2

# 2. Open browser to http://localhost:5000
# 3. Use any of the 4 scraper sections
# 4. View real-time results at http://localhost:8001
```

### **Command Line Research Workflow**
```bash
# 1. Check system readiness
.\run.bat --check-deps

# 2. Search for onion sites
.\run.bat --onionsearch "secure messaging"

# 3. Deep crawl specific site
.\run.bat --toc "http://discovered-site.onion"

# 4. OSINT analysis
.\run.bat --torbot "http://target-site.onion" 2
```

### **Mixed Usage Pattern**
```bash
# 1. Quick command line search
.\run.bat --onionsearch "privacy tools"

# 2. Switch to web interface for detailed analysis
.\run.bat --web
# Use TOC and TorBot sections for discovered sites
```

## 🔧 **Troubleshooting**

### **TorBot Section Not Visible**
✅ **FIXED**: Template regenerated with proper 4-section layout

### **Data Not Clearing**
✅ **FIXED**: Automatic clearing implemented for all scrapers

### **Autorun Scripts Confusing**
✅ **FIXED**: Added comprehensive help and error handling

### **Common Issues**
```bash
# TOR not running
.\run.bat --check-deps  # Check TOR status

# Missing packages
pip install httpx[socks] treelib tabulate toml validators

# Go not installed
# Download from https://golang.org/dl/
```

## 🎉 **System Status**

### **All Issues Resolved**
- ✅ **Data clearing**: Automatic on each new session
- ✅ **Autorun help**: Comprehensive usage instructions
- ✅ **4-section interface**: TorBot properly integrated
- ✅ **Error handling**: Clear messages and solutions
- ✅ **Cross-platform**: Works on Windows, Linux, macOS

### **Ready for Production Use**
The Live Graph System now provides a complete, professional-grade platform for comprehensive web intelligence gathering with all requested enhancements implemented and tested.
