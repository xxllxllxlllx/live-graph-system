# Install Missing Dependencies Guide

## 🎯 **Current Status**
✅ **Python Dependencies**: All installed  
❌ **Go**: Not installed (required for TOC crawler)  
❌ **TOR Proxy**: Not running (required for .onion sites)  

## 🔧 **Step 1: Install Go Programming Language**

### **Windows Installation**
1. **Download Go**:
   - Visit: https://golang.org/dl/
   - Download: `go1.21.x.windows-amd64.msi` (latest version)

2. **Install Go**:
   - Run the downloaded .msi installer
   - Follow the installation wizard (default settings are fine)
   - Go will be installed to `C:\Program Files\Go`

3. **Verify Installation**:
   ```cmd
   # Open new Command Prompt or PowerShell
   go version
   # Should show: go version go1.21.x windows/amd64
   ```

4. **Test Go Installation**:
   ```cmd
   cd E:\augment-vault\augment-projects\graphs\live-graph-system
   python run.py --check-deps
   # Should now show: ✅ Go: go version go1.21.x windows/amd64
   ```

### **Linux Installation**
```bash
# Method 1: Package Manager (Ubuntu/Debian)
sudo apt update
sudo apt install golang-go

# Method 2: Manual Installation (Latest Version)
wget https://golang.org/dl/go1.21.0.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# Verify
go version
```

### **macOS Installation**
```bash
# Method 1: Homebrew
brew install go

# Method 2: Manual Download
# Download from https://golang.org/dl/
# Install the .pkg file

# Verify
go version
```

## 🧅 **Step 2: Install TOR Proxy**

### **Windows Installation (Method 1: Tor Browser - Easiest)**
1. **Download Tor Browser**:
   - Visit: https://www.torproject.org/
   - Click "Download Tor Browser"
   - Download for Windows

2. **Install and Run**:
   - Run the installer
   - Launch Tor Browser
   - Wait for connection to establish
   - **Keep Tor Browser running** while using onion scrapers

3. **Verify TOR Proxy**:
   ```cmd
   # Check if port 9050 is listening
   netstat -an | findstr 9050
   # Should show: TCP    127.0.0.1:9050         0.0.0.0:0              LISTENING
   
   # Or use the dependency check
   python run.py --check-deps
   # Should show: ✅ TOR proxy: Running on 127.0.0.1:9050
   ```

### **Windows Installation (Method 2: Tor Daemon Only)**
1. **Download Tor Expert Bundle**:
   - Visit: https://www.torproject.org/download/tor/
   - Download "Expert Bundle" for Windows

2. **Setup Tor Daemon**:
   ```cmd
   # Extract to C:\tor\
   # Create directory structure
   mkdir C:\tor\Data\Tor
   
   # Create torrc config file in C:\tor\Data\Tor\torrc
   # Content:
   DataDirectory C:\tor\Data\Tor
   SocksPort 127.0.0.1:9050
   ```

3. **Run Tor Daemon**:
   ```cmd
   cd C:\tor\Tor
   tor.exe
   # Keep this running in background
   ```

### **Linux Installation**
```bash
# Install Tor
sudo apt update
sudo apt install tor

# Start Tor service
sudo systemctl start tor
sudo systemctl enable tor

# Verify Tor is running
sudo systemctl status tor
netstat -an | grep 9050

# Check with dependency checker
python run.py --check-deps
```

### **macOS Installation**
```bash
# Install Tor using Homebrew
brew install tor

# Start Tor service
brew services start tor

# Verify
netstat -an | grep 9050
python run.py --check-deps
```

## 🔍 **Step 3: Verify All Dependencies**

After installing Go and TOR, run the complete dependency check:

```bash
python run.py --check-deps
```

**Expected Output:**
```
🔍 Checking System Dependencies...
==================================================
✅ Python: 3.13.5
✅ Go: go version go1.21.x windows/amd64
✅ TOR proxy: Running on 127.0.0.1:9050

OnionSearch packages:
  ✅ requests
  ✅ bs4
  ✅ socks
  ✅ tqdm

TorBot packages:
  ✅ httpx
  ✅ treelib
  ✅ tabulate
  ✅ toml
  ✅ validators
```

## 🚀 **Step 4: Test Each Scraper**

Once all dependencies are installed, test each scraper:

### **Test TOC Onion Crawler**
```bash
# This requires Go and TOR proxy
python run.py --toc "https://duckduckgogg42ts72.onion"
```

### **Test OnionSearch Engine**
```bash
# This works with or without TOR proxy
python run.py --onionsearch "privacy tools"
```

### **Test TorBot OSINT Crawler**
```bash
# Test with regular website (no TOR needed)
python run.py --torbot "https://github.com" --depth 1

# Test with .onion site (TOR needed)
python run.py --torbot "https://duckduckgogg42ts72.onion" --depth 1
```

## 🌐 **Step 5: Launch Web Interface**

With all dependencies installed, launch the complete web interface:

```bash
python run.py --web
```

Navigate to http://localhost:5000 and you should see all 4 scraper sections:
- 🌐 HTTP/HTTPS Scraper (top-left)
- 🧅 TOC Onion Crawler (top-right)
- 🔍 OnionSearch Engine (bottom-left)
- 🤖 TorBot OSINT Crawler (bottom-right)

## ⚠️ **Troubleshooting**

### **Go Installation Issues**
```bash
# If 'go' command not found after installation
# Windows: Restart Command Prompt/PowerShell
# Linux/Mac: Run 'source ~/.bashrc' or restart terminal

# Check PATH
echo $PATH  # Linux/Mac
echo %PATH% # Windows
```

### **TOR Proxy Issues**
```bash
# Check if TOR is running
netstat -an | grep 9050    # Linux/Mac
netstat -an | findstr 9050 # Windows

# If TOR not running:
# Windows: Restart Tor Browser or tor.exe
# Linux: sudo systemctl restart tor
# Mac: brew services restart tor
```

### **Permission Issues**
```bash
# Linux: If tor service fails to start
sudo chown -R debian-tor:debian-tor /var/lib/tor
sudo systemctl restart tor
```

## 📋 **Quick Reference**

### **Essential Commands**
```bash
# Check all dependencies
python run.py --check-deps

# Launch web interface
python run.py --web

# Test individual scrapers
python run.py --toc "https://duckduckgogg42ts72.onion"
python run.py --onionsearch "privacy tools"
python run.py --torbot "https://github.com" --depth 1
```

### **Required Ports**
- **TOR Proxy**: 127.0.0.1:9050
- **Web Interface**: localhost:5000
- **Graph Visualization**: localhost:8001

### **File Locations**
- **Data Output**: `data/data.json`
- **Frontend Data**: `frontend/data/data.json`
- **Logs**: Console output and Activity Log in web interface
