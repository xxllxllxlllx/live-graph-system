# Development Guide

This guide is for developers who want to contribute to or modify the Live Graph System.

## 🏗️ Project Structure

The project follows a clean, modular architecture:

```
live-graph-system/
├── frontend/           # Client-side visualization
├── backend/           # Server-side scraping logic
├── data/             # Runtime data and logs
├── docs/             # Documentation
├── tests/            # Test files and sample data
└── archive/          # Legacy files
```

## 🔧 Development Setup

### Prerequisites
- Python 3.7+
- Modern web browser
- Git (for version control)

### Quick Setup
```bash
# Clone and setup
git clone <repository-url>
cd live-graph-system

# Setup dependencies
python run.py --setup

# Or manually:
cd backend/interfaces
python setup_scraper.py
```

## 📁 Module Overview

### Frontend (`frontend/`)
- **Technology**: HTML5, CSS3, JavaScript, D3.js v3
- **Main Files**:
  - `index.html` - Main visualization page
  - `assets/js/graph.js` - D3.js visualization logic
  - `assets/css/style.css` - Styling and responsive design
  - `assets/js/d3.v3.min.js` - D3.js library

### Backend (`backend/`)

#### Core (`backend/core/`)
- **`web_scraper.py`** - Main scraping engine
  - `WebScraper` class with hierarchical crawling
  - URL validation and filtering
  - Respectful crawling with delays
  
- **`scraper_integration.py`** - Integration layer
  - `LiveScraperIntegration` class for real-time updates
  - `ScraperController` for high-level control
  - Data transformation for D3.js compatibility

#### Interfaces (`backend/interfaces/`)
- **`scraper_cli.py`** - Command-line interface
- **`scraper_web_interface.py`** - Flask web interface
- **`setup_scraper.py`** - Dependency installation

#### Config (`backend/config/`)
- **`scraper_config.py`** - Configuration settings
- **`requirements.txt`** - Python dependencies

## 🔄 Data Flow

1. **User Input** → CLI or Web Interface
2. **Scraping** → WebScraper crawls websites
3. **Processing** → Data transformed to D3.js format
4. **Storage** → JSON saved to `data/data.json`
5. **Visualization** → Frontend polls and displays data

## 🧪 Testing

### Running Tests
```bash
cd tests
python test_websites.py
```

### Test Websites
Sample websites are provided in `tests/test-websites/` for development and testing.

## 🎨 Frontend Development

### Modifying Visualizations
- Edit `frontend/assets/js/graph.js`
- D3.js v3 syntax (for compatibility)
- Real-time polling every 1 second
- Smooth animations with 750ms duration

### Styling Changes
- Edit `frontend/assets/css/style.css`
- Responsive design principles
- Matches OSINT Framework aesthetics

### Adding New Visualizations
1. Create new JS file in `frontend/assets/js/`
2. Update `index.html` to include new script
3. Ensure compatibility with existing data format

## 🐍 Backend Development

### Adding New Scrapers
1. Extend `WebScraper` class in `web_scraper.py`
2. Implement new scraping methods
3. Update data transformation in `scraper_integration.py`

### Modifying Data Format
1. Update transformation in `scraper_integration.py`
2. Ensure frontend compatibility
3. Update documentation

### Adding New Interfaces
1. Create new file in `backend/interfaces/`
2. Import core modules: `from ..core import ScraperController`
3. Follow existing patterns for consistency

## 📊 Configuration

### Scraper Settings
Edit `backend/config/scraper_config.py`:
- Maximum depth levels
- Links per page limits
- Request delays and timeouts
- User agent strings

### Adding Dependencies
1. Add to `backend/config/requirements.txt`
2. Update `setup_scraper.py` if needed
3. Test installation process

## 🔍 Debugging

### Common Issues
1. **Import Errors**: Check Python path and module structure
2. **Port Conflicts**: Change ports in web interface files
3. **Permission Errors**: Ensure write access to `data/` directory

### Logging
- Scraper logs: `data/scraper.log`
- Additional logs: `data/logs/`
- Console output for real-time debugging

## 🚀 Deployment

### Local Development
```bash
python run.py --web    # Web interface
python run.py --viz    # Visualization only
```

### Production Considerations
- Use proper WSGI server for Flask app
- Configure reverse proxy for static files
- Set up log rotation
- Monitor resource usage

## 🤝 Contributing

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex logic

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

### Commit Messages
- Use clear, descriptive messages
- Reference issues when applicable
- Follow conventional commit format

## 📝 Documentation

### Updating Docs
- Main docs in `docs/` directory
- Update `README.md` for user-facing changes
- Update this file for developer changes
- Keep `SYSTEM_STATUS.md` current

### API Documentation
- Add docstrings to all public methods
- Use type hints where appropriate
- Include usage examples

## 🔐 Security

### Best Practices
- Validate all user inputs
- Sanitize URLs before scraping
- Respect robots.txt files
- Implement rate limiting
- Use HTTPS where possible

### Reporting Issues
- Report security issues privately
- Include reproduction steps
- Provide system information

---

*Happy coding! 🎉*
