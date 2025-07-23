# 🚀 Quick Start Guide

Get the Live Graph System running in under 5 minutes!

## ⚡ Super Quick Start

```bash
# 1. Setup (first time only)
python run.py --setup

# 2. Launch web interface
python run.py --web

# 3. Open browser to: http://localhost:5000
```

That's it! 🎉

## 📋 Step-by-Step

### Step 1: Setup Dependencies
```bash
python run.py --setup
```
This installs all required Python packages.

### Step 2: Choose Your Interface

#### Option A: Web Interface (Recommended)
```bash
python run.py --web
```
- Opens Flask web interface at `http://localhost:5000`
- User-friendly GUI for scraping control
- Real-time progress monitoring

#### Option B: Command Line Interface
```bash
python run.py --cli
```
- Interactive command-line interface
- Direct scraping commands
- Perfect for automation

#### Option C: Visualization Only
```bash
python run.py --viz
```
- Opens visualization at `http://localhost:8001`
- View previously scraped data
- No scraping controls

### Step 3: Start Scraping
1. Enter a website URL (e.g., `https://example.com`)
2. Set scraping depth (1-10 levels)
3. Set links per page (1-20 links)
4. Click "Start Scraping" or run CLI command
5. Watch the graph update in real-time!

## 🎯 Example Usage

### Web Interface
1. `python run.py --web`
2. Open `http://localhost:5000`
3. Enter URL: `https://news.ycombinator.com`
4. Set depth: `3`, links: `5`
5. Click "Start Scraping"
6. View live graph updates

### Command Line
```bash
python run.py --cli
# Then in interactive mode:
> scrape https://example.com --depth 3 --links 5
```

### Direct Command
```bash
cd backend/interfaces
python scraper_cli.py --url https://example.com --depth 3 --links 5
```

## 🔧 Alternative Launchers

### Windows
```cmd
run.bat
```

### Unix/Linux/Mac
```bash
chmod +x run.sh
./run.sh
```

### Interactive Menu
```bash
python run.py
# Choose from menu options 1-5
```

## 📊 What You'll See

### Web Interface Features
- 🎛️ **Control Panel**: Start/stop scraping, configure parameters
- 📈 **Progress Monitor**: Real-time scraping status and logs
- 🌐 **Live Graph**: Interactive D3.js visualization
- ⚙️ **Settings**: Adjustable depth, links, delays

### Graph Visualization Features
- 🖱️ **Click nodes** to expand/collapse branches
- 🔍 **Hover** for tooltips with URL information
- 🎨 **Smooth animations** as new nodes appear
- 📱 **Responsive design** works on all screen sizes
- ⌨️ **Keyboard shortcuts**: R to refresh, Escape to reset

## 🎨 Sample Websites to Try

### Good for Testing
- `https://example.com` - Simple structure
- `https://httpbin.org` - API testing site
- `https://quotes.toscrape.com` - Scraping practice site

### News Sites
- `https://news.ycombinator.com` - Tech news
- `https://lobste.rs` - Programming links

### Documentation Sites
- `https://docs.python.org` - Python docs
- `https://developer.mozilla.org` - Web docs

## ⚠️ Important Notes

### Respectful Scraping
- The system implements delays between requests
- Respects robots.txt files
- Uses proper User-Agent headers
- Limits concurrent requests

### Performance Tips
- Start with depth 2-3 for testing
- Use 3-5 links per page initially
- Monitor system resources
- Check logs for any issues

### Troubleshooting
- **Port conflicts**: Change ports in config files
- **Permission errors**: Ensure write access to `data/` folder
- **Import errors**: Run setup script again
- **Slow performance**: Reduce depth or links per page

## 📁 File Locations

After scraping, find your data:
- **Graph data**: `data/data.json`
- **Logs**: `data/scraper.log`
- **Visualization**: `frontend/index.html`

## 🆘 Need Help?

1. **Documentation**: Check `docs/README.md` for detailed info
2. **Development**: See `DEVELOPMENT.md` for technical details
3. **Issues**: Check log files in `data/logs/`
4. **Structure**: See `ORGANIZATION_SUMMARY.md` for file layout

## 🎉 You're Ready!

The Live Graph System is now organized and ready to use. Enjoy exploring website structures with beautiful, interactive visualizations!

---

*Happy scraping! 🕷️📊*
