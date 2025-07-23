"""
Core scraping functionality
Contains the main web scraper and integration components
"""

from .web_scraper import WebScraper
from .scraper_integration import LiveScraperIntegration, ScraperController

__all__ = ['WebScraper', 'LiveScraperIntegration', 'ScraperController']
