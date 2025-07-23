# 🧅 Tor Integration Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_tor.txt
```

### 2. Setup Tor Browser
1. **Download Tor Browser**: https://www.torproject.org/download/
2. **Install and Start** Tor Browser
3. **Wait for Connection**: Let Tor Browser fully connect (green onion icon)
4. **Keep Running**: Leave Tor Browser open while using the scraper

### 3. Test Integration
```bash
python test_tor_integration.py
```

## Detailed Setup

### Understanding Tor vs VPN

**Tor is NOT a VPN!** Here's the difference:

| Feature | VPN | Tor |
|---------|-----|-----|
| **Routing** | You → VPN Server → Internet | You → Entry → Middle → Exit → Internet |
| **Encryption** | Single tunnel | Multiple layers (onion routing) |
| **Anonymity** | VPN provider knows your traffic | No single node knows source + destination |
| **Speed** | Fast | Slower (multiple hops) |
| **Use Case** | Privacy, geo-blocking | Anonymity, .onion sites |

### How Tor Proxying Works

1. **Tor Client** (Browser/Service) creates SOCKS5 proxy on `127.0.0.1:9050`
2. **Your Application** connects to this proxy instead of direct internet
3. **Entry Node** receives encrypted request, removes outer layer
4. **Middle Node** removes another layer, forwards to exit node
5. **Exit Node** removes final layer, makes actual request
6. **For .onion sites**: No exit node needed, stays within Tor network

### Installation Options

#### Option 1: Tor Browser (Recommended for Testing)
- **Pros**: Easy setup, includes proxy automatically
- **Cons**: Must keep browser open
- **Setup**: Download, install, start, wait for connection

#### Option 2: Tor Service (For Production)
- **Pros**: Runs as background service
- **Cons**: More complex setup
- **Windows**: Download Tor Expert Bundle
- **Linux**: `sudo apt install tor` or `sudo yum install tor`
- **macOS**: `brew install tor`

### Troubleshooting

#### ❌ "Tor is not running on 127.0.0.1:9050"
**Solutions:**
- Start Tor Browser and wait for full connection
- Check if another application is using port 9050
- Restart Tor Browser
- Check firewall settings

#### ❌ "SOCKSHTTPSConnectionPool failed"
**Solutions:**
- Install SOCKS support: `pip install requests[socks]`
- Verify Tor Browser is connected (green onion icon)
- Try different onion URLs (they change frequently)
- Check if your ISP blocks Tor

#### ❌ "getaddrinfo failed"
**Solutions:**
- Onion URL might be outdated
- Tor network might be congested
- Try again later
- Use bridge relays if Tor is blocked

### Testing Connectivity

#### Test 1: Check Tor Proxy
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 9050))
print("Tor running:" if result == 0 else "Tor not running")
```

#### Test 2: Test with Regular Site
```python
import requests
proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}
response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())  # Should show Tor exit node IP
```

#### Test 3: Test Onion Site
```python
response = requests.get('https://duckduckgogg42ts72.onion', proxies=proxies)
print(response.status_code)  # Should be 200
```

### Popular Onion Sites

| Site | URL | Status |
|------|-----|--------|
| DuckDuckGo | `duckduckgogg42ts72.onion` | Usually stable |
| Facebook | `facebookcorewwwi.onion` | Usually stable |
| Ahmia Search | `juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion` | Search engine |
| ProtonMail | `protonirockerxow.onion` | Email service |

**Note**: Onion URLs change frequently. If one doesn't work, try others or search for updated URLs.

### Security Considerations

#### ✅ Good Practices
- Always use HTTPS when possible (even for .onion)
- Keep Tor Browser updated
- Don't download files through Tor
- Use VPN + Tor for extra security (advanced)

#### ❌ Avoid
- Don't log sensitive data when using Tor
- Don't use personal information on onion sites
- Don't trust all onion sites (many are malicious)
- Don't use Tor for high-bandwidth activities

### Integration with Live Graph System

The system automatically:
1. **Detects Tor**: Checks if proxy is running on 127.0.0.1:9050
2. **Routes .onion requests**: Through Tor proxy automatically
3. **Falls back**: Uses direct connection for regular sites
4. **Handles errors**: Provides helpful error messages

### Performance Tips

- **Patience**: Tor is slower than direct connections
- **Timeouts**: Increase timeout values for onion sites
- **Retry Logic**: Implement retries for failed connections
- **Caching**: Cache results to avoid repeated requests

### Legal and Ethical Use

- **Legal**: Using Tor is legal in most countries
- **Ethical**: Respect robots.txt and rate limits
- **Responsible**: Don't overload onion services
- **Privacy**: Tor protects your privacy, use it responsibly
