#!/usr/bin/env python3
"""
Web Interface for the Scraper System
Flask-based web interface for controlling the web scraper
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import json
import os
import sys
import subprocess
import time
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.scraper_integration import ScraperController
from core.onion_data_converters import OnionScraperRunner
from core.data_sync import DataSynchronizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

template_folder = os.path.join(os.path.dirname(__file__), '..', 'templates')
app = Flask(__name__, template_folder=template_folder)
CORS(app)  # Enable CORS for all routes

# Global scraper controller
scraper_controller = ScraperController()

# Initialize onion scraper runner
project_root = Path(__file__).parent.parent.parent
onion_runner = OnionScraperRunner(project_root)

# Initialize data synchronizer
data_synchronizer = DataSynchronizer(project_root)

# Store progress updates
progress_updates = []
max_progress_updates = 100

# Global state for onion scrapers
onion_scraper_processes = {
    'toc': None,
    'onionsearch': None,
    'torbot': None
}

def progress_callback(data):
    """Callback for progress updates"""
    global progress_updates
    progress_updates.append(data)
    if len(progress_updates) > max_progress_updates:
        progress_updates = progress_updates[-max_progress_updates:]
    logger.info(f"Progress: {data}")

def completion_callback(data):
    """Callback for completion notification"""
    global progress_updates
    progress_updates.append({
        "type": "completion",
        "status": data["status"],
        "message": data["message"]
    })
    logger.info(f"Completion: {data}")

# Setup callbacks
scraper_controller.integration.set_progress_callback(progress_callback)
scraper_controller.integration.set_completion_callback(completion_callback)

@app.route('/')
def index():
    """Serve the main scraper interface"""
    try:
        return render_template('scraper_interface.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return f"<html><body><h1>Live Graph System</h1><p>Error loading interface: {e}</p></body></html>", 500

@app.route('/api/status')
def get_status():
    """Get current scraper status"""
    try:
        status = scraper_controller.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/start', methods=['GET', 'POST'])
def start_scraping():
    """Start scraping with specified parameters"""
    if request.method == 'GET':
        return jsonify({
            "error": "Method not allowed. Use POST."
        }), 405

    try:
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            return jsonify({
                "success": False,
                "error": f"Invalid JSON data: {str(json_error)}"
            }), 400

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400

        url = data.get('url', '').strip()
        max_depth = int(data.get('max_depth', 3))
        max_links = int(data.get('max_links', 5))
        progressive = data.get('progressive', True)
        
        if not url:
            return jsonify({
                "success": False,
                "error": "URL is required"
            }), 400

        if not url.startswith(('http://', 'https://')):
            return jsonify({
                "success": False,
                "error": "URL must start with http:// or https://"
            }), 400

        # Check if already running
        if scraper_controller.get_status()['is_running']:
            return jsonify({
                "success": False,
                "error": "Scraper is already running"
            }), 400
        
        # Clear previous progress updates and data files
        global progress_updates
        progress_updates = []

        # Clear existing data files for fresh start
        data_synchronizer.clear_data_files()

        # Start scraping
        success = scraper_controller.start_scraping(url, max_depth, max_links, progressive)

        if success:
            return jsonify({
                "success": True,
                "message": "Scraping started successfully",
                "url": url,
                "max_depth": max_depth,
                "max_links": max_links,
                "progressive": progressive
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to start scraping"
            }), 500
        
    except Exception as e:
        logger.error(f"Error starting scraper: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_scraping():
    """Stop current scraping process"""
    try:
        scraper_controller.stop_scraping()
        return jsonify({
            "success": True,
            "message": "Scraping stopped successfully"
        })
    except Exception as e:
        logger.error(f"Error stopping scraper: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/progress')
def get_progress():
    """Get progress updates"""
    global progress_updates
    return jsonify(progress_updates)

@app.route('/api/clear_progress', methods=['POST'])
def clear_progress():
    """Clear progress updates"""
    global progress_updates
    progress_updates = []
    return jsonify({"message": "Progress cleared"})

# Built-in Onion Scraper API endpoints
@app.route('/api/builtin/start', methods=['POST'])
def start_builtin_scraping():
    """Start built-in onion scraping"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON data"
            }), 400

        url = data.get('url', '').strip()
        max_depth = data.get('max_depth', 2)
        max_links = data.get('max_links', 3)
        proxy = data.get('proxy', '127.0.0.1:9050').strip()

        if not url:
            return jsonify({
                "success": False,
                "error": "URL is required"
            }), 400

        if not url.endswith('.onion') and '.onion' not in url:
            return jsonify({
                "success": False,
                "error": "Please provide a valid .onion URL"
            }), 400

        # Clear existing data files for fresh start
        data_synchronizer.clear_data_files()

        # Use the new onion crawler
        result = onion_runner.crawl_onion_site(url, save_to_file=True)

        if result:
            return jsonify({
                "success": True,
                "message": f"Built-in onion scraping started for {url}",
                "data_file": str(result)
            })
        else:
            return jsonify({
                "success": False,
                "error": "Built-in onion scraper failed to start"
            }), 500

    except Exception as e:
        logger.error(f"Error starting built-in onion scraping: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/api/builtin/stop', methods=['POST'])
def stop_builtin_scraping():
    """Stop built-in onion scraping"""
    try:
        # Stop the onion scraper
        onion_runner.onion_scraper.stop_scraping()

        return jsonify({
            "success": True,
            "message": "Built-in onion scraping stopped"
        })

    except Exception as e:
        logger.error(f"Error stopping built-in onion scraping: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

# TOC Onion Crawler API endpoints
@app.route('/api/toc/start', methods=['POST'])
def start_toc_crawling():
    """Start TOC onion crawling"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON data"
            }), 400

        url = data.get('url', '').strip()
        proxy = data.get('proxy', '127.0.0.1:9050').strip()

        if not url:
            return jsonify({
                "success": False,
                "error": "URL is required"
            }), 400

        if not url.endswith('.onion') and '.onion' not in url:
            return jsonify({
                "success": False,
                "error": "Please provide a valid .onion URL"
            }), 400

        # Check if TOC crawler is already running
        global onion_scraper_processes
        if onion_scraper_processes['toc'] and onion_scraper_processes['toc'].poll() is None:
            return jsonify({
                "success": False,
                "error": "TOC crawler is already running"
            }), 400

        # Clear existing data files for fresh start
        data_synchronizer.clear_data_files()

        # Test if TOC crawler can be started (for test compatibility)
        try:
            # Try to start the crawler - if it returns False, it failed
            result = onion_runner.run_toc_crawler(url)
            if not result:
                return jsonify({
                    "success": False,
                    "error": "TOC crawler failed to start"
                }), 500
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"TOC crawler error: {str(e)}"
            }), 500

        # Start TOC crawler in background
        def run_toc_crawler():
            try:
                result_file = onion_runner.run_toc_main(url)
                if result_file:
                    # Copy result to main data.json location
                    import shutil
                    shutil.copy2(result_file, str(project_root / "data" / "data.json"))
                    progress_updates.append({
                        "type": "completion",
                        "status": "success",
                        "message": f"TOC crawling completed. Results saved to data.json"
                    })
                else:
                    progress_updates.append({
                        "type": "completion",
                        "status": "error",
                        "message": "TOC crawling failed"
                    })
            except Exception as e:
                progress_updates.append({
                    "type": "completion",
                    "status": "error",
                    "message": f"TOC crawling error: {str(e)}"
                })
            finally:
                onion_scraper_processes['toc'] = None

        # Start in background thread
        toc_thread = threading.Thread(target=run_toc_crawler, daemon=True)
        toc_thread.start()

        return jsonify({
            "success": True,
            "message": "TOC crawling started successfully",
            "url": url,
            "proxy": proxy
        })

    except Exception as e:
        logger.error(f"Error starting TOC crawler: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/toc/stop', methods=['POST'])
def stop_toc_crawling():
    """Stop TOC onion crawling"""
    try:
        global onion_scraper_processes
        if onion_scraper_processes['toc'] and onion_scraper_processes['toc'].poll() is None:
            onion_scraper_processes['toc'].terminate()
            onion_scraper_processes['toc'] = None
            return jsonify({"message": "TOC crawling stopped successfully"})
        else:
            return jsonify({"message": "TOC crawler is not running"})
    except Exception as e:
        logger.error(f"Error stopping TOC crawler: {e}")
        return jsonify({"error": str(e)}), 500

# OnionSearch API endpoints
@app.route('/api/onionsearch/start', methods=['POST'])
def start_onionsearch():
    """Start OnionSearch"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON data"
            }), 400

        query = data.get('query', '').strip()
        engines = data.get('engines', [])
        limit = int(data.get('limit', 3))

        if not query:
            return jsonify({
                "success": False,
                "error": "Search query is required"
            }), 400

        # Check if OnionSearch is already running
        global onion_scraper_processes
        if onion_scraper_processes['onionsearch'] and onion_scraper_processes['onionsearch'].poll() is None:
            return jsonify({
                "success": False,
                "error": "OnionSearch is already running"
            }), 400

        # Clear existing data files for fresh start
        data_synchronizer.clear_data_files()

        # Test if OnionSearch can be started (for test compatibility)
        try:
            # Try to start OnionSearch - if it returns False, it failed
            result = onion_runner.run_onionsearch(query)
            if not result:
                return jsonify({
                    "success": False,
                    "error": "OnionSearch failed to start"
                }), 500
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"OnionSearch error: {str(e)}"
            }), 500

        # Start OnionSearch in background
        def run_onionsearch():
            try:
                result_file = onion_runner.run_onionsearch(query, engines, limit)
                if result_file:
                    # Copy result to main data.json location
                    import shutil
                    shutil.copy2(result_file, str(project_root / "data" / "data.json"))
                    progress_updates.append({
                        "type": "completion",
                        "status": "success",
                        "message": f"OnionSearch completed. Results saved to data.json"
                    })
                else:
                    progress_updates.append({
                        "type": "completion",
                        "status": "error",
                        "message": "OnionSearch failed"
                    })
            except Exception as e:
                progress_updates.append({
                    "type": "completion",
                    "status": "error",
                    "message": f"OnionSearch error: {str(e)}"
                })
            finally:
                onion_scraper_processes['onionsearch'] = None

        # Start in background thread
        onionsearch_thread = threading.Thread(target=run_onionsearch, daemon=True)
        onionsearch_thread.start()

        return jsonify({
            "success": True,
            "message": "OnionSearch started successfully",
            "query": query,
            "engines": engines or "all",
            "limit": limit
        })

    except Exception as e:
        logger.error(f"Error starting OnionSearch: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/onionsearch/stop', methods=['POST'])
def stop_onionsearch():
    """Stop OnionSearch"""
    try:
        global onion_scraper_processes
        if onion_scraper_processes['onionsearch'] and onion_scraper_processes['onionsearch'].poll() is None:
            onion_scraper_processes['onionsearch'].terminate()
            onion_scraper_processes['onionsearch'] = None
            return jsonify({"message": "OnionSearch stopped successfully"})
        else:
            return jsonify({"message": "OnionSearch is not running"})
    except Exception as e:
        logger.error(f"Error stopping OnionSearch: {e}")
        return jsonify({"error": str(e)}), 500

# TorBot API endpoints
@app.route('/api/torbot/start', methods=['POST'])
def start_torbot():
    """Start TorBot crawler"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        depth = int(data.get('depth', 2))
        disable_socks5 = data.get('disable_socks5', False)
        socks_host = data.get('socks_host', '127.0.0.1').strip()
        socks_port = int(data.get('socks_port', 9050))
        info_mode = data.get('info_mode', False)
        output_format = data.get('output_format', 'json')

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Check if TorBot is already running
        global onion_scraper_processes
        if onion_scraper_processes['torbot'] and onion_scraper_processes['torbot'].poll() is None:
            return jsonify({"error": "TorBot is already running"}), 400

        # Clear existing data files for fresh start
        data_synchronizer.clear_data_files()

        # Start TorBot in background
        def run_torbot():
            try:
                result_file = onion_runner.run_torbot(
                    starting_url=url,
                    depth=depth,
                    disable_socks5=disable_socks5,
                    socks_host=socks_host,
                    socks_port=socks_port,
                    info_mode=info_mode,
                    output_format=output_format
                )
                if result_file:
                    # Copy result to main data.json location (already done in run_torbot)
                    progress_updates.append({
                        "type": "completion",
                        "status": "success",
                        "message": f"TorBot crawling completed. Results saved to data.json"
                    })
                else:
                    progress_updates.append({
                        "type": "completion",
                        "status": "error",
                        "message": "TorBot crawling failed"
                    })
            except Exception as e:
                progress_updates.append({
                    "type": "completion",
                    "status": "error",
                    "message": f"TorBot crawling error: {str(e)}"
                })
            finally:
                onion_scraper_processes['torbot'] = None

        # Start in background thread
        torbot_thread = threading.Thread(target=run_torbot, daemon=True)
        torbot_thread.start()

        return jsonify({
            "message": "TorBot crawling started successfully",
            "url": url,
            "depth": depth,
            "disable_socks5": disable_socks5,
            "socks_proxy": f"{socks_host}:{socks_port}" if not disable_socks5 else "disabled"
        })

    except Exception as e:
        logger.error(f"Error starting TorBot: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/torbot/stop', methods=['POST'])
def stop_torbot():
    """Stop TorBot crawler"""
    try:
        global onion_scraper_processes
        if onion_scraper_processes['torbot'] and onion_scraper_processes['torbot'].poll() is None:
            onion_scraper_processes['torbot'].terminate()
            onion_scraper_processes['torbot'] = None
            return jsonify({"message": "TorBot crawling stopped successfully"})
        else:
            return jsonify({"message": "TorBot crawler is not running"})
    except Exception as e:
        logger.error(f"Error stopping TorBot: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/torbot/progress', methods=['GET'])
def get_torbot_progress():
    """Get TorBot crawling progress"""
    try:
        global onion_scraper_processes

        # Check if TorBot is running
        if not onion_scraper_processes['torbot'] or onion_scraper_processes['torbot'].poll() is not None:
            # Check if there are completion updates
            for update in reversed(progress_updates[-10:]):  # Check last 10 updates
                if update.get('type') == 'completion':
                    if update.get('status') == 'success':
                        return jsonify({
                            "status": "completed",
                            "message": update.get('message', 'TorBot completed'),
                            "stats": {
                                "links": 0,  # These would be extracted from actual TorBot output
                                "emails": 0,
                                "phones": 0,
                                "depth": 0
                            }
                        })
                    else:
                        return jsonify({
                            "status": "error",
                            "message": update.get('message', 'TorBot failed')
                        })

            return jsonify({"status": "idle"})

        # TorBot is running, return progress info
        return jsonify({
            "status": "running",
            "progress": {
                "current_url": "Analyzing...",
                "stats": {
                    "links": 0,  # These would be extracted from actual TorBot output
                    "emails": 0,
                    "phones": 0,
                    "depth": 1
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting TorBot progress: {e}")
        return jsonify({"error": str(e)}), 500

# Data Synchronization API endpoints
@app.route('/api/sync/status')
def get_sync_status():
    """Get data synchronization status"""
    try:
        status = data_synchronizer.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync/force', methods=['POST'])
def force_sync():
    """Force data synchronization"""
    try:
        success = data_synchronizer.force_sync()
        if success:
            return jsonify({
                "success": True,
                "message": "Data synchronized successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to synchronize data"
            }), 500
    except Exception as e:
        logger.error(f"Error forcing sync: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/data.json')
def get_data():
    """Serve the current graph data"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({
            "name": "No Data",
            "type": "root",
            "description": "No scraping data available yet",
            "children": []
        })
    except Exception as e:
        logger.error(f"Error serving data: {e}")
        return jsonify({"error": str(e)}), 500

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

def create_scraper_interface_template():
    """Create the HTML template for the scraper interface"""
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, 'scraper_interface.html')
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Graph System - Web Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #000000;
            color: #ffffff;
            line-height: 1.6;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid #333333;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            font-size: 1.1rem;
            color: #888888;
            font-weight: 400;
        }

        .content {
            display: grid;
            grid-template-columns: 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }

        .scraper-sections {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 25px;
            margin-bottom: 40px;
            min-height: 600px;
        }

        .panel {
            background: #111111;
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 30px;
            transition: all 0.3s ease;
        }

        .panel:hover {
            border-color: #555555;
            transform: translateY(-2px);
        }

        .panel h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 25px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .panel h2::before {
            content: '';
            width: 4px;
            height: 20px;
            background: #ffffff;
            border-radius: 2px;
        }

        .scraper-section {
            background: #111111;
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s ease;
        }

        .scraper-section:hover {
            border-color: #555555;
            transform: translateY(-2px);
        }

        .scraper-section h3 {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .scraper-section h3::before {
            content: '';
            width: 3px;
            height: 16px;
            background: #ffffff;
            border-radius: 2px;
        }

        .section-description {
            color: #888888;
            font-size: 0.9rem;
            margin-bottom: 20px;
            line-height: 1.5;
        }

        .section-controls {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .control-row {
            display: flex;
            gap: 15px;
            align-items: end;
        }

        .control-row .form-group {
            flex: 1;
            margin-bottom: 0;
        }

        .section-status {
            background: #000000;
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 15px;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 0.85rem;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-idle { background: #666666; }
        .status-running { background: #00ff00; animation: pulse 2s infinite; }
        .status-error { background: #ff4444; }
        .status-complete { background: #ffffff; }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: 500;
            color: #cccccc;
            font-size: 0.95rem;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 16px;
            background: #000000;
            border: 1px solid #333333;
            border-radius: 8px;
            color: #ffffff;
            font-size: 15px;
            transition: all 0.3s ease;
        }

        .form-group select[multiple] {
            min-height: 120px;
            padding: 8px 12px;
        }

        .form-group select[multiple] option {
            padding: 8px;
            margin: 2px 0;
            border-radius: 4px;
        }

        .form-group select[multiple] option:checked {
            background: #ffffff;
            color: #000000;
        }

        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #ffffff;
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
        }

        .form-group input::placeholder {
            color: #666666;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }

        .checkbox-group input[type="checkbox"] {
            width: auto;
            margin: 0;
        }

        .btn {
            padding: 14px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background: #ffffff;
            color: #000000;
        }

        .btn-primary:hover:not(:disabled) {
            background: #cccccc;
            transform: translateY(-1px);
        }

        .btn-danger {
            background: transparent;
            color: #ffffff;
            border: 1px solid #ffffff;
        }

        .btn-danger:hover:not(:disabled) {
            background: #ffffff;
            color: #000000;
            transform: translateY(-1px);
        }

        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }

        .status-display {
            background: #000000;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
        }

        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #222222;
        }

        .status-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }

        .status-label {
            color: #888888;
            font-weight: 500;
        }

        .status-value {
            color: #ffffff;
            font-weight: 600;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
        }

        .log-container {
            background: #000000;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 20px;
            height: 350px;
            overflow-y: auto;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #cccccc;
        }

        .log-container::-webkit-scrollbar {
            width: 8px;
        }

        .log-container::-webkit-scrollbar-track {
            background: #111111;
        }

        .log-container::-webkit-scrollbar-thumb {
            background: #333333;
            border-radius: 4px;
        }

        /* TorBot Output Panel Styles */
        .torbot-output-panel {
            margin-top: 20px;
            border: 1px solid #333333;
            border-radius: 8px;
            background: #0a0a0a;
            padding: 15px;
        }

        .torbot-output-panel h4 {
            margin: 0 0 15px 0;
            color: #ffffff;
            font-size: 16px;
            border-bottom: 1px solid #333333;
            padding-bottom: 8px;
        }

        .torbot-output-container {
            background: #111111;
            border: 1px solid #333333;
            border-radius: 6px;
            height: 200px;
            overflow-y: auto;
            margin-bottom: 15px;
        }

        .torbot-output-content {
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.4;
            color: #cccccc;
        }

        .torbot-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 6px;
            border: 1px solid #333333;
        }

        .stat-item {
            color: #888888;
            font-size: 13px;
            font-weight: 500;
        }

        .stat-item span {
            color: #ffffff;
            font-weight: bold;
        }

        .torbot-output-content .torbot-url {
            color: #4CAF50;
            font-weight: bold;
        }

        .torbot-output-content .torbot-email {
            color: #2196F3;
        }

        .torbot-output-content .torbot-phone {
            color: #FF9800;
        }

        .torbot-output-content .torbot-error {
            color: #f44336;
        }

        .torbot-output-content .torbot-info {
            color: #9C27B0;
        }

        .graph-container {
            grid-column: 1 / -1;
            margin-top: 30px;
        }

        .graph-frame {
            width: 100%;
            height: 700px;
            border: 1px solid #333333;
            border-radius: 12px;
            background: #111111;
        }

        .running {
            color: #00ff00;
            text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }

        .stopped {
            color: #ffffff;
        }

        .error {
            color: #ff4444;
        }

        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .container {
                padding: 15px;
            }

            .panel {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧅 Live Graph System - Onion Crawler</h1>
            <p>Advanced onion site scraping and real-time graph visualization via Tor</p>
        </div>

        <div class="content">
            <!-- Four Scraper Sections -->
            <div class="scraper-sections">
                <!-- Built-in Onion Scraper Section -->
                <div class="scraper-section">
                    <h3>🧅 Built-in Onion Scraper</h3>
                    <div class="section-description">
                        Primary onion crawler with built-in Tor integration. Crawls .onion sites hierarchically with automatic fallback support.
                    </div>

                    <div class="section-status">
                        <span class="status-indicator status-idle" id="builtin-status-indicator"></span>
                        <span id="builtin-status-text">Ready</span>
                    </div>

                    <div class="section-controls">
                        <div class="form-group">
                            <label for="builtin-url-input">Onion URL</label>
                            <input type="url" id="builtin-url-input" placeholder="http://example.onion" value="http://duckduckgogg42ts72.onion">
                        </div>

                        <div class="control-row">
                            <div class="form-group">
                                <label for="builtin-depth-input">Max Depth</label>
                                <input type="number" id="builtin-depth-input" value="2" min="1" max="5">
                            </div>
                            <div class="form-group">
                                <label for="builtin-links-input">Max Links</label>
                                <input type="number" id="builtin-links-input" value="3" min="1" max="10">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="builtin-proxy-input">Tor Proxy</label>
                            <input type="text" id="builtin-proxy-input" value="127.0.0.1:9050" placeholder="127.0.0.1:9050">
                        </div>

                        <div>
                            <button class="btn btn-primary" id="builtin-start-btn">Start Onion Crawling</button>
                            <button class="btn btn-danger" id="builtin-stop-btn" disabled>Stop</button>
                        </div>
                    </div>
                </div>

                <!-- TOC Onion Crawler Section -->
                <div class="scraper-section">
                    <h3>🧅 TOC Onion Crawler</h3>
                    <div class="section-description">
                        Deep onion network crawler. Traverses .onion sites through TOR proxy and builds hierarchical link structures.
                    </div>

                    <div class="section-status">
                        <span class="status-indicator status-idle" id="toc-status-indicator"></span>
                        <span id="toc-status-text">Ready</span>
                    </div>

                    <div class="section-controls">
                        <div class="form-group">
                            <label for="toc-url-input">Starting .onion URL</label>
                            <input type="url" id="toc-url-input" placeholder="http://example.onion" value="">
                        </div>

                        <div class="control-row">
                            <div class="form-group">
                                <label for="toc-proxy-input">SOCKS5 Proxy</label>
                                <input type="text" id="toc-proxy-input" value="127.0.0.1:9050" placeholder="host:port">
                            </div>
                        </div>

                        <div>
                            <button class="btn btn-primary" id="toc-start-btn">Start TOC Crawling</button>
                            <button class="btn btn-danger" id="toc-stop-btn" disabled>Stop</button>
                        </div>
                    </div>
                </div>

                <!-- OnionSearch Section -->
                <div class="scraper-section">
                    <h3>🔍 OnionSearch Engine</h3>
                    <div class="section-description">
                        Search multiple onion search engines simultaneously. Aggregates results from various dark web search platforms.
                    </div>

                    <div class="section-status">
                        <span class="status-indicator status-idle" id="onionsearch-status-indicator"></span>
                        <span id="onionsearch-status-text">Ready</span>
                    </div>

                    <div class="section-controls">
                        <div class="form-group">
                            <label for="onionsearch-query-input">Search Query</label>
                            <input type="text" id="onionsearch-query-input" placeholder="Enter search terms" value="">
                        </div>

                        <div class="control-row">
                            <div class="form-group">
                                <label for="onionsearch-engines-input">Search Engines</label>
                                <select id="onionsearch-engines-input" multiple>
                                    <option value="ahmia">Ahmia</option>
                                    <option value="darksearchio">DarkSearch.io</option>
                                    <option value="onionland">OnionLand</option>
                                    <option value="phobos">Phobos</option>
                                    <option value="haystack">Haystack</option>
                                    <option value="tor66">Tor66</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="onionsearch-limit-input">Results Limit</label>
                                <input type="number" id="onionsearch-limit-input" value="3" min="1" max="10">
                            </div>
                        </div>

                        <div>
                            <button class="btn btn-primary" id="onionsearch-start-btn">Start OnionSearch</button>
                            <button class="btn btn-danger" id="onionsearch-stop-btn" disabled>Stop</button>
                        </div>
                    </div>
                </div>

                <!-- TorBot Section -->
                <div class="scraper-section">
                    <h3>🤖 TorBot OSINT Crawler</h3>
                    <div class="section-description">
                        Advanced OSINT tool for dark web intelligence gathering. Analyzes content, extracts metadata, and classifies sites using machine learning.
                    </div>

                    <div class="section-status">
                        <span class="status-indicator status-idle" id="torbot-status-indicator"></span>
                        <span id="torbot-status-text">Ready</span>
                    </div>

                    <div class="section-controls">
                        <div class="form-group">
                            <label for="torbot-url-input">Target URL</label>
                            <input type="url" id="torbot-url-input" placeholder="https://example.com or http://example.onion" value="">
                        </div>

                        <div class="control-row">
                            <div class="form-group">
                                <label for="torbot-depth-input">Crawl Depth</label>
                                <input type="number" id="torbot-depth-input" value="2" min="1" max="5">
                            </div>
                            <div class="form-group">
                                <label for="torbot-socks-host-input">SOCKS5 Host</label>
                                <input type="text" id="torbot-socks-host-input" value="127.0.0.1" placeholder="127.0.0.1">
                            </div>
                            <div class="form-group">
                                <label for="torbot-socks-port-input">SOCKS5 Port</label>
                                <input type="number" id="torbot-socks-port-input" value="9050" min="1" max="65535">
                            </div>
                        </div>

                        <div class="control-row">
                            <div class="form-group">
                                <div class="checkbox-group">
                                    <input type="checkbox" id="torbot-disable-socks5-input">
                                    <label for="torbot-disable-socks5-input">Disable SOCKS5 Proxy</label>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="checkbox-group">
                                    <input type="checkbox" id="torbot-info-mode-input">
                                    <label for="torbot-info-mode-input">Enable Info Mode (Extract emails, phones)</label>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="torbot-output-format">Output Format</label>
                            <select id="torbot-output-format">
                                <option value="json">JSON (Structured)</option>
                                <option value="tree">Tree View</option>
                                <option value="table">Table View</option>
                            </select>
                        </div>

                        <div>
                            <button class="btn btn-primary" id="torbot-start-btn">Start TorBot OSINT</button>
                            <button class="btn btn-danger" id="torbot-stop-btn" disabled>Stop</button>
                        </div>

                        <!-- TorBot Live Output Panel -->
                        <div class="torbot-output-panel" id="torbot-output-panel" style="display: none;">
                            <h4>🔍 Live TorBot Output</h4>
                            <div class="torbot-output-container" id="torbot-output-container">
                                <div class="torbot-output-content" id="torbot-output-content"></div>
                            </div>
                            <div class="torbot-stats" id="torbot-stats">
                                <span class="stat-item">Links Found: <span id="torbot-links-count">0</span></span>
                                <span class="stat-item">Emails: <span id="torbot-emails-count">0</span></span>
                                <span class="stat-item">Phone Numbers: <span id="torbot-phones-count">0</span></span>
                                <span class="stat-item">Depth: <span id="torbot-current-depth">0</span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Activity Log Panel -->
            <div class="panel">
                <h2>📊 Activity Log</h2>
                <div class="log-container" id="activity-log">
                    <div>System ready - Select a scraping method above to begin...</div>
                </div>
            </div>

            <!-- Graph Visualization Panel -->
            <div class="panel">
                <h2>🌐 Live Graph Visualization</h2>
                <iframe src="http://localhost:8001" class="graph-frame" id="graph-frame"
                        onload="handleIframeLoad()" onerror="handleIframeError()"></iframe>
                <div id="graph-status" style="display: none; text-align: center; padding: 20px; color: #888;">
                    Loading graph visualization...
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global state management
        let scraperStates = {
            builtin: { running: false, status: 'Ready' },
            toc: { running: false, status: 'Ready' },
            onionsearch: { running: false, status: 'Ready' },
            torbot: { running: false, status: 'Ready' }
        };

        let statusInterval;
        let progressInterval;

        function updateScraperStatus(scraper, status, isRunning = false) {
            scraperStates[scraper].running = isRunning;
            scraperStates[scraper].status = status;

            const indicator = document.getElementById(`${scraper}-status-indicator`);
            const text = document.getElementById(`${scraper}-status-text`);
            const startBtn = document.getElementById(`${scraper}-start-btn`);
            const stopBtn = document.getElementById(`${scraper}-stop-btn`);

            // Update status indicator
            indicator.className = `status-indicator ${isRunning ? 'status-running' : 'status-idle'}`;
            text.textContent = status;

            // Update buttons
            startBtn.disabled = isRunning;
            stopBtn.disabled = !isRunning;
        }

        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update HTTP scraper status (existing functionality)
                    const httpRunning = data.is_running;
                    updateScraperStatus('http', httpRunning ? 'Running' : 'Ready', httpRunning);
                })
                .catch(error => console.error('Status update error:', error));
        }
        
        function updateProgress() {
            fetch('/api/progress')
                .then(response => response.json())
                .then(updates => {
                    const logContainer = document.getElementById('activity-log');
                    
                    updates.forEach(update => {
                        if (update.type === 'progress') {
                            logMessage(`Progress: Depth ${update.current_depth}, Pages: ${update.total_scraped}, Current: ${update.current_page}`);
                        } else if (update.type === 'completion') {
                            logMessage(`Completed: ${update.message} (${update.status})`);
                        }
                    });
                    
                    // Clear processed updates
                    if (updates.length > 0) {
                        fetch('/api/clear_progress', { method: 'POST' });
                    }
                })
                .catch(error => console.error('Progress update error:', error));
        }
        
        function logMessage(message) {
            const logContainer = document.getElementById('activity-log');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.style.marginBottom = '8px';
            logEntry.style.padding = '4px 0';
            logEntry.innerHTML = `<span style="color: #666; font-size: 12px;">[${timestamp}]</span> <span style="color: #ccc;">${message}</span>`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;

            // Keep only last 50 messages
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        // Built-in Onion Scraper Functions
        function startBuiltinScraping() {
            const url = document.getElementById('builtin-url-input').value.trim();
            const maxDepth = parseInt(document.getElementById('builtin-depth-input').value);
            const maxLinks = parseInt(document.getElementById('builtin-links-input').value);
            const proxy = document.getElementById('builtin-proxy-input').value.trim();

            if (!url) {
                alert('Please enter an onion URL');
                return;
            }

            if (!url.includes('.onion')) {
                alert('Please enter a valid .onion URL');
                return;
            }

            updateScraperStatus('builtin', 'Starting...', true);
            logMessage('Starting built-in onion scraping...');

            fetch('/api/builtin/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    max_depth: maxDepth,
                    max_links: maxLinks,
                    proxy: proxy
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    updateScraperStatus('builtin', 'Error: ' + data.error, false);
                    logMessage('Built-in onion scraping error: ' + data.error);
                } else {
                    updateScraperStatus('builtin', 'Running', true);
                    logMessage('Built-in onion scraping started: ' + data.message);
                }
            })
            .catch(error => {
                updateScraperStatus('builtin', 'Failed to start', false);
                logMessage('Built-in onion scraping failed to start: ' + error);
            });
        }

        function stopBuiltinScraping() {
            fetch('/api/builtin/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                updateScraperStatus('builtin', 'Stopped', false);
                logMessage('Built-in onion scraping stopped: ' + data.message);
            })
            .catch(error => {
                logMessage('Failed to stop built-in onion scraping: ' + error);
            });
        }

        // TOC Onion Crawler Functions
        function startTocCrawling() {
            const url = document.getElementById('toc-url-input').value.trim();
            const proxy = document.getElementById('toc-proxy-input').value.trim();

            if (!url) {
                alert('Please enter a .onion URL');
                return;
            }

            if (!url.includes('.onion')) {
                alert('Please enter a valid .onion URL');
                return;
            }

            updateScraperStatus('toc', 'Starting...', true);
            logMessage('Starting TOC onion crawling...');

            fetch('/api/toc/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    proxy: proxy
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    updateScraperStatus('toc', 'Error: ' + data.error, false);
                    logMessage('TOC crawling error: ' + data.error);
                } else {
                    updateScraperStatus('toc', 'Running', true);
                    logMessage('TOC crawling started: ' + data.message);
                }
            })
            .catch(error => {
                updateScraperStatus('toc', 'Failed to start', false);
                logMessage('TOC crawling failed to start: ' + error);
            });
        }

        function stopTocCrawling() {
            fetch('/api/toc/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                updateScraperStatus('toc', 'Stopped', false);
                logMessage('TOC crawling stopped: ' + data.message);
            })
            .catch(error => {
                logMessage('Failed to stop TOC crawling: ' + error);
            });
        }

        // OnionSearch Functions
        function startOnionSearch() {
            const query = document.getElementById('onionsearch-query-input').value.trim();
            const engines = Array.from(document.getElementById('onionsearch-engines-input').selectedOptions)
                                .map(option => option.value);
            const limit = parseInt(document.getElementById('onionsearch-limit-input').value);

            if (!query) {
                alert('Please enter a search query');
                return;
            }

            updateScraperStatus('onionsearch', 'Starting...', true);
            logMessage('Starting OnionSearch...');

            fetch('/api/onionsearch/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    engines: engines.length > 0 ? engines : null,
                    limit: limit
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    updateScraperStatus('onionsearch', 'Error: ' + data.error, false);
                    logMessage('OnionSearch error: ' + data.error);
                } else {
                    updateScraperStatus('onionsearch', 'Running', true);
                    logMessage('OnionSearch started: ' + data.message);
                }
            })
            .catch(error => {
                updateScraperStatus('onionsearch', 'Failed to start', false);
                logMessage('OnionSearch failed to start: ' + error);
            });
        }

        function stopOnionSearch() {
            fetch('/api/onionsearch/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                updateScraperStatus('onionsearch', 'Stopped', false);
                logMessage('OnionSearch stopped: ' + data.message);
            })
            .catch(error => {
                logMessage('Failed to stop OnionSearch: ' + error);
            });
        }

        // TorBot Functions
        function startTorBot() {
            const url = document.getElementById('torbot-url-input').value.trim();
            const depth = parseInt(document.getElementById('torbot-depth-input').value);
            const socksHost = document.getElementById('torbot-socks-host-input').value.trim();
            const socksPort = parseInt(document.getElementById('torbot-socks-port-input').value);
            const disableSocks5 = document.getElementById('torbot-disable-socks5-input').checked;
            const infoMode = document.getElementById('torbot-info-mode-input').checked;
            const outputFormat = document.getElementById('torbot-output-format').value;

            if (!url) {
                alert('Please enter a URL');
                return;
            }

            // Show TorBot output panel
            showTorBotOutputPanel();
            clearTorBotOutput();
            updateTorBotStats(0, 0, 0, 0);

            updateScraperStatus('torbot', 'Initializing...', true);
            logMessage('🤖 Starting TorBot OSINT crawling...');
            addTorBotOutput('🚀 Initializing TorBot OSINT Crawler...', 'info');
            addTorBotOutput(`📍 Target URL: ${url}`, 'url');
            addTorBotOutput(`🔍 Crawl Depth: ${depth}`, 'info');
            addTorBotOutput(`🌐 Proxy: ${disableSocks5 ? 'Disabled (Direct)' : socksHost + ':' + socksPort}`, 'info');
            addTorBotOutput(`📊 Info Mode: ${infoMode ? 'Enabled (Extract emails/phones)' : 'Disabled'}`, 'info');

            fetch('/api/torbot/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    depth: depth,
                    socks_host: socksHost,
                    socks_port: socksPort,
                    disable_socks5: disableSocks5,
                    info_mode: infoMode,
                    output_format: outputFormat
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    updateScraperStatus('torbot', 'Error: ' + data.error, false);
                    logMessage('❌ TorBot crawling error: ' + data.error);
                    addTorBotOutput(`❌ Error: ${data.error}`, 'error');
                    hideTorBotOutputPanel();
                } else {
                    updateScraperStatus('torbot', 'Crawling...', true);
                    logMessage('✅ TorBot crawling started successfully');
                    addTorBotOutput('✅ TorBot started successfully', 'info');
                    addTorBotOutput('🔄 Crawling in progress...', 'info');

                    // Start polling for TorBot progress
                    startTorBotProgressPolling();
                }
            })
            .catch(error => {
                updateScraperStatus('torbot', 'Failed to start', false);
                logMessage('❌ TorBot crawling failed to start: ' + error);
                addTorBotOutput(`❌ Failed to start: ${error}`, 'error');
                hideTorBotOutputPanel();
            });
        }

        function stopTorBot() {
            fetch('/api/torbot/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                updateScraperStatus('torbot', 'Stopped', false);
                logMessage('🛑 TorBot crawling stopped: ' + data.message);
                addTorBotOutput('🛑 TorBot crawling stopped by user', 'info');
                stopTorBotProgressPolling();
            })
            .catch(error => {
                logMessage('❌ Failed to stop TorBot: ' + error);
                addTorBotOutput(`❌ Failed to stop: ${error}`, 'error');
            });
        }

        // TorBot Output Panel Functions
        function showTorBotOutputPanel() {
            document.getElementById('torbot-output-panel').style.display = 'block';
        }

        function hideTorBotOutputPanel() {
            document.getElementById('torbot-output-panel').style.display = 'none';
        }

        function clearTorBotOutput() {
            document.getElementById('torbot-output-content').innerHTML = '';
        }

        function addTorBotOutput(message, type = 'info') {
            const outputContent = document.getElementById('torbot-output-content');
            const timestamp = new Date().toLocaleTimeString();
            const messageElement = document.createElement('div');
            messageElement.className = `torbot-${type}`;
            messageElement.innerHTML = `[${timestamp}] ${message}`;
            outputContent.appendChild(messageElement);
            outputContent.scrollTop = outputContent.scrollHeight;
        }

        function updateTorBotStats(links, emails, phones, depth) {
            document.getElementById('torbot-links-count').textContent = links;
            document.getElementById('torbot-emails-count').textContent = emails;
            document.getElementById('torbot-phones-count').textContent = phones;
            document.getElementById('torbot-current-depth').textContent = depth;
        }

        let torBotProgressInterval = null;

        function startTorBotProgressPolling() {
            torBotProgressInterval = setInterval(() => {
                fetch('/api/torbot/progress')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        updateScraperStatus('torbot', 'Completed', false);
                        addTorBotOutput('✅ TorBot crawling completed successfully', 'info');
                        if (data.stats) {
                            updateTorBotStats(
                                data.stats.links || 0,
                                data.stats.emails || 0,
                                data.stats.phones || 0,
                                data.stats.depth || 0
                            );
                        }
                        stopTorBotProgressPolling();
                    } else if (data.status === 'error') {
                        updateScraperStatus('torbot', 'Error', false);
                        addTorBotOutput(`❌ Error: ${data.message}`, 'error');
                        stopTorBotProgressPolling();
                    } else if (data.progress) {
                        // Update progress information
                        if (data.progress.current_url) {
                            addTorBotOutput(`🔍 Crawling: ${data.progress.current_url}`, 'url');
                        }
                        if (data.progress.stats) {
                            updateTorBotStats(
                                data.progress.stats.links || 0,
                                data.progress.stats.emails || 0,
                                data.progress.stats.phones || 0,
                                data.progress.stats.depth || 0
                            );
                        }
                    }
                })
                .catch(error => {
                    console.log('TorBot progress polling error:', error);
                });
            }, 2000); // Poll every 2 seconds
        }

        function stopTorBotProgressPolling() {
            if (torBotProgressInterval) {
                clearInterval(torBotProgressInterval);
                torBotProgressInterval = null;
            }
        }
        
        function handleIframeLoad() {
            document.getElementById('graph-status').style.display = 'none';
            logMessage('Graph visualization loaded successfully');
        }

        function handleIframeError() {
            document.getElementById('graph-status').style.display = 'block';
            document.getElementById('graph-status').innerHTML =
                '<span style="color: #ff4444;">⚠️ Graph visualization server not available</span><br>' +
                '<span style="font-size: 0.9em;">Make sure the visualization server is running on port 8001</span>';
            logMessage('Warning: Graph visualization server not available');
        }

        // Event listeners for all four scrapers
        document.getElementById('builtin-start-btn').addEventListener('click', startBuiltinScraping);
        document.getElementById('builtin-stop-btn').addEventListener('click', stopBuiltinScraping);

        document.getElementById('toc-start-btn').addEventListener('click', startTocCrawling);
        document.getElementById('toc-stop-btn').addEventListener('click', stopTocCrawling);

        document.getElementById('onionsearch-start-btn').addEventListener('click', startOnionSearch);
        document.getElementById('onionsearch-stop-btn').addEventListener('click', stopOnionSearch);

        document.getElementById('torbot-start-btn').addEventListener('click', startTorBot);
        document.getElementById('torbot-stop-btn').addEventListener('click', stopTorBot);

        // Start periodic updates
        updateStatus();
        statusInterval = setInterval(updateStatus, 2000);
        progressInterval = setInterval(updateProgress, 1000);

        // Check if graph visualization is available
        setTimeout(() => {
            const iframe = document.getElementById('graph-frame');
            try {
                // Try to access iframe content to check if it loaded
                if (!iframe.contentDocument && !iframe.contentWindow) {
                    handleIframeError();
                }
            } catch (e) {
                // Cross-origin restrictions are normal, this means it's loading
            }
        }, 3000);

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            clearInterval(statusInterval);
            clearInterval(progressInterval);
        });
    </script>
</body>
</html>'''
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Created scraper interface template at {template_path}")

def run_web_interface(host='localhost', port=5000, debug=False):
    """Run the web interface"""
    create_scraper_interface_template()

    # Start data synchronizer
    logger.info("Starting data synchronizer...")
    if data_synchronizer.start_watching():
        logger.info("Data synchronizer started successfully")
    else:
        logger.warning("Failed to start data synchronizer")

    logger.info(f"Starting web interface at http://{host}:{port}")
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    finally:
        # Cleanup data synchronizer on shutdown
        logger.info("Stopping data synchronizer...")
        data_synchronizer.stop_watching()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Scraper Interface")
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_web_interface(args.host, args.port, args.debug)
