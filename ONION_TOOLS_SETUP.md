# 🧅 Onion Tools Setup Guide

## Overview
The Live Graph System supports multiple onion scraping approaches:
1. **Built-in Tor Integration** (recommended) - Direct SOCKS5 proxy connection
2. **External Tools** (optional) - TOC, OnionSearch, TorBot binaries

## Quick Start (Built-in Integration)
```bash
# Install Tor dependencies
pip install requests[socks] PySocks

# Start Tor Browser (creates proxy on 127.0.0.1:9050)
# System automatically detects and uses Tor proxy
```

## Advanced Setup (External Tools)

### 1. Create Onions Directory
```bash
mkdir onions
cd onions
```

### 2. Download Scraper Tools

#### TOC (The Onion Crawler)
```bash
git clone https://github.com/s-rah/toc.git toc-main
cd toc-main
# Follow their build instructions
go build -o toc main.go
cd ..
```

#### OnionSearch
```bash
git clone https://github.com/megadose/OnionSearch.git OnionSearch-master
cd OnionSearch-master
pip install -r requirements.txt
cd ..
```

#### TorBot
```bash
git clone https://github.com/DedSecInside/TorBot.git TorBot-dev
cd TorBot-dev
pip install -r requirements.txt
cd ..
```

### 3. Verify Structure
```
onions/
├── toc-main/
│   ├── main.go
│   └── toc (executable)
├── OnionSearch-master/
│   ├── onionsearch/
│   └── requirements.txt
└── TorBot-dev/
    ├── torbot/
    └── requirements.txt
```

## Fallback Strategy

The system automatically handles missing tools:

1. **Tool Available**: Uses external binary
2. **Tool Missing**: Falls back to built-in Tor integration
3. **Tor Unavailable**: Uses mock data for testing
4. **All Fail**: Provides clear error messages

## Handling Repository Changes

### Automatic Detection
The system checks for:
- Expected file structures
- Required executables
- Configuration files

### Update Strategy
```bash
# Update all tools
cd onions
git -C toc-main pull
git -C OnionSearch-master pull  
git -C TorBot-dev pull

# Rebuild if needed
cd toc-main && go build -o toc main.go
```

### Version Compatibility
- System tests tool compatibility on startup
- Logs warnings for structural changes
- Falls back to built-in integration if tools break

## Configuration

### Environment Variables
```bash
export ONION_TOOLS_PATH="/path/to/onions"
export TOR_PROXY_HOST="127.0.0.1"
export TOR_PROXY_PORT="9050"
export FALLBACK_TO_BUILTIN="true"
```

### Config File (config/onion_tools.json)
```json
{
  "tools_directory": "./onions",
  "fallback_enabled": true,
  "tor_proxy": {
    "host": "127.0.0.1",
    "port": 9050
  },
  "tool_configs": {
    "toc": {
      "executable": "toc",
      "required_files": ["main.go"]
    },
    "onionsearch": {
      "module": "onionsearch.core",
      "required_files": ["requirements.txt"]
    },
    "torbot": {
      "module": "torbot",
      "required_files": ["requirements.txt"]
    }
  }
}
```

## Troubleshooting

### Tool Not Found
```
⚠️ TOC tool not found in onions/toc-main/
💡 Falling back to built-in Tor integration
🔧 To fix: Follow setup instructions in ONION_TOOLS_SETUP.md
```

### Structure Changed
```
⚠️ OnionSearch structure changed - expected onionsearch/core.py
💡 Using built-in search via Ahmia
🔧 To fix: Update tool or check for new version
```

### Tor Not Available
```
❌ Tor proxy not available on 127.0.0.1:9050
💡 Using mock data for demonstration
🔧 To fix: Start Tor Browser or Tor service
```

## Best Practices

1. **Pin Tool Versions**: Use specific commits/tags
2. **Test After Updates**: Run system tests after tool updates
3. **Monitor Logs**: Check for compatibility warnings
4. **Backup Configs**: Save working tool configurations
5. **Document Changes**: Note any custom modifications
