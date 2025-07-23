#!/usr/bin/env python3
"""
Web Scraper Integration for Live Graph System
Integrates web scraping with the existing D3.js visualization system
"""

import json
import time
import threading
from typing import Dict, Optional, Callable
from .web_scraper import WebScraper, ScrapingConfig
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LiveScraperIntegration:
    """Integration layer between web scraper and live graph system"""
    
    def __init__(self, data_file_path: str = "../../data/data.json"):
        self.data_file_path = Path(data_file_path)
        self.scraper = None
        self.scraping_thread = None
        self.is_running = False
        self.current_url = None
        self.progress_callback = None
        self.completion_callback = None
        
    def set_progress_callback(self, callback: Callable[[Dict], None]):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_completion_callback(self, callback: Callable[[Dict], None]):
        """Set callback for completion notification"""
        self.completion_callback = callback
    
    def transform_scraped_data(self, scraped_data: Dict) -> Dict:
        """Transform scraped data to match the existing graph format"""
        if not scraped_data:
            return self.create_empty_graph()
        
        def transform_node(node: Dict, depth: int = 0) -> Dict:
            """Recursively transform nodes to match expected format"""
            # Map scraper node types to graph node types
            type_mapping = {
                "root": "root",
                "level1": "category", 
                "level2": "subcategory",
                "level3": "item",
                "level4": "item",
                "level5": "item",
                "level6": "item",
                "level7": "item",
                "level8": "item",
                "level9": "item",
                "level10": "item"
            }
            
            transformed = {
                "name": node.get("name", "Unknown Page"),
                "type": type_mapping.get(node.get("type", "item"), "item"),
                "description": node.get("description", "No description available")
            }
            
            # Add URL if present (for reference)
            if "url" in node:
                transformed["url"] = node["url"]
            
            # Transform children (always include children array for consistency)
            children = node.get("children", [])
            transformed["children"] = [
                transform_node(child, depth + 1)
                for child in children
            ]
            
            return transformed
        
        return transform_node(scraped_data)
    
    def create_empty_graph(self) -> Dict:
        """Create an empty graph structure"""
        return {
            "name": "No Data Available",
            "type": "root",
            "description": "No scraping data available",
            "children": []
        }
    
    def save_data(self, data: Dict) -> bool:
        """Save data to the JSON file used by the graph system"""
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {self.data_file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def load_existing_data(self) -> Dict:
        """Load existing data from the JSON file"""
        try:
            if self.data_file_path.exists():
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load existing data: {e}")
        
        return self.create_empty_graph()
    
    def scrape_and_update(self, url: str, config: ScrapingConfig = None):
        """Scrape website and update the graph data"""
        def scraping_worker():
            try:
                logger.info(f"Starting web scraping for: {url}")
                
                # Create scraper with config
                self.scraper = WebScraper(config or ScrapingConfig())
                
                # Start scraping
                scraped_data = self.scraper.start_scraping(url)
                
                if scraped_data:
                    # Transform data to match graph format
                    transformed_data = self.transform_scraped_data(scraped_data)
                    
                    # Save to data file
                    if self.save_data(transformed_data):
                        logger.info("Scraping completed successfully")
                        if self.completion_callback:
                            self.completion_callback({
                                "status": "success",
                                "message": "Scraping completed successfully",
                                "total_pages": self.scraper.total_scraped,
                                "max_depth": self.scraper.current_depth
                            })
                    else:
                        logger.error("Failed to save scraped data")
                        if self.completion_callback:
                            self.completion_callback({
                                "status": "error",
                                "message": "Failed to save scraped data"
                            })
                else:
                    logger.error("No data was scraped")
                    if self.completion_callback:
                        self.completion_callback({
                            "status": "error",
                            "message": "No data was scraped"
                        })
                        
            except Exception as e:
                logger.error(f"Scraping error: {e}")
                if self.completion_callback:
                    self.completion_callback({
                        "status": "error",
                        "message": f"Scraping error: {str(e)}"
                    })
            finally:
                self.is_running = False
                self.scraper = None
        
        # Start scraping in a separate thread
        self.is_running = True
        self.current_url = url
        self.scraping_thread = threading.Thread(target=scraping_worker)
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def start_progressive_scraping(self, url: str, config: ScrapingConfig = None):
        """Start progressive scraping with real-time updates"""
        def progressive_worker():
            try:
                logger.info(f"Starting progressive web scraping for: {url}")
                
                # Create scraper with config
                self.scraper = WebScraper(config or ScrapingConfig())
                
                # Override the scraper's recursive method to provide updates
                original_scrape = self.scraper.scrape_recursive
                
                def progressive_scrape(url, depth=0):
                    result = original_scrape(url, depth)
                    
                    # Send progress update
                    if self.progress_callback and result:
                        status = self.scraper.get_status()
                        self.progress_callback({
                            "type": "progress",
                            "current_depth": depth,
                            "total_scraped": status["total_scraped"],
                            "current_page": result.get("name", "Unknown"),
                            "current_url": url
                        })
                        
                        # Save intermediate results for real-time visualization
                        if depth == 0:  # Save root updates
                            transformed = self.transform_scraped_data(result)
                            self.save_data(transformed)
                    
                    return result
                
                # Replace the method
                self.scraper.scrape_recursive = progressive_scrape
                
                # Start scraping
                scraped_data = self.scraper.start_scraping(url)
                
                if scraped_data:
                    # Final transformation and save
                    transformed_data = self.transform_scraped_data(scraped_data)
                    self.save_data(transformed_data)
                    
                    logger.info("Progressive scraping completed successfully")
                    if self.completion_callback:
                        self.completion_callback({
                            "status": "success",
                            "message": "Progressive scraping completed successfully",
                            "total_pages": self.scraper.total_scraped,
                            "max_depth": self.scraper.current_depth
                        })
                else:
                    logger.error("No data was scraped")
                    if self.completion_callback:
                        self.completion_callback({
                            "status": "error",
                            "message": "No data was scraped"
                        })
                        
            except Exception as e:
                logger.error(f"Progressive scraping error: {e}")
                if self.completion_callback:
                    self.completion_callback({
                        "status": "error",
                        "message": f"Progressive scraping error: {str(e)}"
                    })
            finally:
                self.is_running = False
                self.scraper = None
        
        # Start progressive scraping in a separate thread
        self.is_running = True
        self.current_url = url
        self.scraping_thread = threading.Thread(target=progressive_worker)
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def stop_scraping(self):
        """Stop the current scraping process"""
        if self.scraper:
            self.scraper.stop_scraping()
        
        self.is_running = False
        
        if self.scraping_thread and self.scraping_thread.is_alive():
            logger.info("Waiting for scraping thread to finish...")
            self.scraping_thread.join(timeout=5)
    
    def get_status(self) -> Dict:
        """Get current scraping status"""
        base_status = {
            "is_running": self.is_running,
            "current_url": self.current_url,
            "total_scraped": 0,
            "current_depth": 0
        }

        if self.scraper:
            base_status["total_scraped"] = getattr(self.scraper, 'total_scraped', 0)
            base_status["current_depth"] = getattr(self.scraper, 'current_depth', 0)

        return base_status
    
    def create_sample_config(self, max_depth: int = 3, max_links: int = 5) -> ScrapingConfig:
        """Create a sample configuration for testing"""
        return ScrapingConfig(
            max_depth=max_depth,
            max_links_per_page=max_links,
            request_delay=1.0,
            timeout=10,
            max_retries=2,
            respect_robots_txt=True,
            user_agent="LiveGraphScraper/1.0 (Educational Purpose)"
        )

class ScraperController:
    """High-level controller for the scraping system"""
    
    def __init__(self, data_file_path: str = "../../data/data.json"):
        self.integration = LiveScraperIntegration(data_file_path)
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """Setup default callbacks for logging"""
        def progress_callback(data):
            logger.info(f"Progress: Depth {data['current_depth']}, "
                       f"Pages: {data['total_scraped']}, "
                       f"Current: {data['current_page']}")
        
        def completion_callback(data):
            if data['status'] == 'success':
                logger.info(f"Scraping completed: {data['message']}")
            else:
                logger.error(f"Scraping failed: {data['message']}")
        
        self.integration.set_progress_callback(progress_callback)
        self.integration.set_completion_callback(completion_callback)
    
    def start_scraping(self, url: str, max_depth: int = 3, max_links: int = 5,
                      progressive: bool = True):
        """Start scraping with specified parameters"""
        try:
            # Check if already running
            if self.integration.is_running:
                return False

            config = self.integration.create_sample_config(max_depth, max_links)

            if progressive:
                self.integration.start_progressive_scraping(url, config)
            else:
                self.integration.scrape_and_update(url, config)

            return True
        except Exception as e:
            logger.error(f"Failed to start scraping: {e}")
            return False
    
    def stop_scraping(self):
        """Stop current scraping"""
        self.integration.stop_scraping()
    
    def get_status(self) -> Dict:
        """Get scraping status"""
        status = self.integration.get_status()
        # Ensure the status includes all expected fields
        return {
            "is_running": status.get("is_running", False),
            "current_url": status.get("current_url", None),
            "total_scraped": status.get("total_scraped", 0),
            "current_depth": status.get("current_depth", 0)
        }

if __name__ == "__main__":
    # Example usage
    controller = ScraperController()
    
    # Start scraping a website
    test_url = "https://example.com"
    controller.start_scraping(test_url, max_depth=2, max_links=3, progressive=True)
    
    # Wait for completion
    while controller.get_status()["is_running"]:
        time.sleep(1)
    
    print("Scraping completed!")
