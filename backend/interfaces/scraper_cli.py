#!/usr/bin/env python3
"""
Command Line Interface for Web Scraper
Provides command-line control for the web scraping system
"""

import argparse
import sys
import time
import signal
from urllib.parse import urlparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from scraper_integration import ScraperController
import logging

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScraperCLI:
    """Command line interface for the web scraper"""
    
    def __init__(self):
        self.controller = ScraperController()
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n\nReceived interrupt signal. Stopping scraper...")
        self.controller.stop_scraping()
        self.running = False
        sys.exit(0)
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def print_status(self):
        """Print current scraping status"""
        status = self.controller.get_status()
        print("\n" + "="*50)
        print("SCRAPER STATUS")
        print("="*50)
        print(f"Running: {'Yes' if status['is_running'] else 'No'}")
        print(f"Current URL: {status.get('current_url', 'None')}")
        print(f"Data File: {status.get('data_file', 'data.json')}")
        
        if status['is_running']:
            print(f"Current Depth: {status.get('current_depth', 0)}")
            print(f"Pages Scraped: {status.get('total_scraped', 0)}")
            print(f"URLs Visited: {status.get('visited_urls_count', 0)}")
        print("="*50)
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        print("Web Scraper Interactive Mode")
        print("Commands: scrape <url>, status, stop, quit")
        print("Type 'help' for more information")
        
        while self.running:
            try:
                command = input("\nscraper> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    if self.controller.get_status()['is_running']:
                        print("Stopping current scraping...")
                        self.controller.stop_scraping()
                    break
                
                elif command == 'help':
                    self.print_help()
                
                elif command == 'status':
                    self.print_status()
                
                elif command == 'stop':
                    if self.controller.get_status()['is_running']:
                        print("Stopping scraping...")
                        self.controller.stop_scraping()
                    else:
                        print("No scraping process is currently running.")
                
                elif command.startswith('scrape '):
                    url = command[7:].strip()
                    if self.validate_url(url):
                        if self.controller.get_status()['is_running']:
                            print("Another scraping process is already running. Stop it first.")
                        else:
                            print(f"Starting scraping of: {url}")
                            self.controller.start_scraping(url, max_depth=3, max_links=5)
                    else:
                        print("Invalid URL format. Please provide a valid HTTP/HTTPS URL.")
                
                elif command == '':
                    continue
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit or Ctrl+C again to force quit.")
            except EOFError:
                break
        
        print("Goodbye!")
    
    def print_help(self):
        """Print help information"""
        help_text = """
Available Commands:
  scrape <url>     - Start scraping the specified URL
  status           - Show current scraping status
  stop             - Stop the current scraping process
  help             - Show this help message
  quit/exit        - Exit the program

Examples:
  scrape https://example.com
  scrape https://news.ycombinator.com
  status
  stop
        """
        print(help_text)
    
    def run_single_scrape(self, url: str, max_depth: int, max_links: int, 
                         progressive: bool, wait: bool):
        """Run a single scraping operation"""
        if not self.validate_url(url):
            print(f"Error: Invalid URL format: {url}")
            return 1
        
        print(f"Starting scraping of: {url}")
        print(f"Max depth: {max_depth}, Max links per page: {max_links}")
        print(f"Progressive mode: {'On' if progressive else 'Off'}")
        
        self.controller.start_scraping(url, max_depth, max_links, progressive)
        
        if wait:
            print("Scraping in progress... Press Ctrl+C to stop")
            try:
                while self.controller.get_status()['is_running'] and self.running:
                    time.sleep(1)
                    # Print periodic status updates
                    status = self.controller.get_status()
                    if status.get('total_scraped', 0) > 0:
                        print(f"\rProgress: Depth {status.get('current_depth', 0)}, "
                              f"Pages: {status.get('total_scraped', 0)}", end='', flush=True)
                
                print("\nScraping completed!")
                self.print_status()
                
            except KeyboardInterrupt:
                print("\nStopping scraper...")
                self.controller.stop_scraping()
                return 1
        else:
            print("Scraping started in background. Use 'status' command to check progress.")
        
        return 0

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Web Scraper for Live Graph Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive
  %(prog)s --url https://example.com --depth 3 --links 5
  %(prog)s --url https://news.ycombinator.com --depth 2 --progressive
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        help='URL to start scraping from'
    )
    
    parser.add_argument(
        '--depth', '-d',
        type=int,
        default=3,
        help='Maximum depth to scrape (default: 3)'
    )
    
    parser.add_argument(
        '--links', '-l',
        type=int,
        default=5,
        help='Maximum links to extract per page (default: 5)'
    )
    
    parser.add_argument(
        '--progressive', '-p',
        action='store_true',
        help='Enable progressive scraping with real-time updates'
    )
    
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='Start scraping in background without waiting'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create CLI instance
    cli = ScraperCLI()
    
    try:
        if args.interactive:
            # Run in interactive mode
            cli.run_interactive_mode()
        elif args.url:
            # Run single scraping operation
            return cli.run_single_scrape(
                args.url,
                args.depth,
                args.links,
                args.progressive,
                not args.no_wait
            )
        else:
            # No URL provided, show help
            parser.print_help()
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
