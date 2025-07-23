# Legacy Random Data Generation System - ARCHIVED

## ⚠️ DEPRECATED

These files represent the legacy random data generation system that has been **replaced by the web scraper system**. They are archived here for reference purposes only.

## Archived Files

- `data-generator.js` - Node.js random data generator (replaced by `web_scraper.py`)
- `generator-control.js` - Web-based random data controller (replaced by `scraper_web_interface.py`)
- `live-controller.html` - Legacy control panel (replaced by Flask web interface)
- `package.json` - Node.js dependencies (replaced by `requirements.txt`)

## Migration Status

✅ **Fully Replaced**: All functionality has been migrated to the Python web scraper system
✅ **No Dependencies**: The main system no longer requires these files
✅ **Backward Compatibility**: Not maintained - use web scraper system instead

## Current System

The live graph system now uses:
- **Web Scraper**: `web_scraper.py` for hierarchical website crawling
- **Integration Layer**: `scraper_integration.py` for data transformation
- **Control Interfaces**: `scraper_cli.py` and `scraper_web_interface.py`
- **Dependencies**: Python packages listed in `requirements.txt`

## Restoration (If Needed)

If you need to restore the legacy system:
1. Move files back to the parent directory
2. Install Node.js dependencies: `npm install`
3. Update `index.html` to include `generator-control.js`
4. Start with: `node data-generator.js --start`

**Note**: This is not recommended as the web scraper provides superior functionality.

---
*Archived on: 2025-07-22*
*Reason: Replaced by web scraper system*
