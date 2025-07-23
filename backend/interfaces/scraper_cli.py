#!/usr/bin/env python3
"""
Command Line Interface for Onion Scraper
Provides command-line control for the onion scraping system with Tor integration
"""

import argparse
import sys
import time
import signal
from urllib.parse import urlparse
import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from onion_data_converters import OnionScraperRunner
from scraper_integration import ScraperController
import logging

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OnionScraperCLI:
    """Command line interface for the onion scraper system"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.onion_runner = OnionScraperRunner(self.project_root)
        self.controller = ScraperController()  # Keep for compatibility
        self.running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n\nReceived interrupt signal. Stopping onion scraper...")
        try:
            self.onion_runner.onion_scraper.stop_scraping()
        except:
            pass
        self.controller.stop_scraping()
        self.running = False
        sys.exit(0)
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted (preferably .onion)"""
        try:
            result = urlparse(url)
            is_valid = all([result.scheme, result.netloc])
            # Prefer onion URLs but allow others for compatibility
            return is_valid
        except Exception:
            return False
    
    def print_status(self):
        """Print current scraping status"""
        status = self.controller.get_status()
        print("\n" + "="*50)
        print("🧅 ONION SCRAPER STATUS")
        print("="*50)
        print(f"Running: {'Yes' if status['is_running'] else 'No'}")

        # Show onion scraper tools status
        tools_status = self.onion_runner.tools_available
        print(f"\n🛠️ Available Tools:")
        print(f"  Built-in Onion Scraper: ✅ Always Available")
        print(f"  TOC Crawler: {'✅ Available' if tools_status.get('toc', False) else '❌ Not Available'}")
        print(f"  OnionSearch: {'✅ Available' if tools_status.get('onionsearch', False) else '❌ Not Available'}")
        print(f"  TorBot: {'✅ Available' if tools_status.get('torbot', False) else '❌ Not Available'}")
        print(f"  Tor Proxy: {'✅ Running' if tools_status.get('tor_proxy', False) else '❌ Not Running'}")
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
                    if url.endswith('.onion') or '.onion' in url:
                        if self.controller.get_status()['is_running']:
                            print("Another scraping process is already running. Stop it first.")
                        else:
                            print(f"Starting onion scraping of: {url}")
                            self.run_builtin_scraper(url)
                    else:
                        print("Please provide a valid .onion URL for onion scraping.")

                elif command.startswith('builtin '):
                    url = command[8:].strip()
                    self.run_builtin_scraper(url)

                elif command.startswith('toc '):
                    url = command[4:].strip()
                    self.run_toc_crawler(url)

                elif command.startswith('onionsearch '):
                    query = command[12:].strip()
                    self.run_onionsearch(query)

                elif command.startswith('torbot '):
                    url = command[7:].strip()
                    self.run_torbot(url)
                
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
🧅 Onion Scraper CLI - Command Line Interface

Available Commands:
  scrape <url>     - Start onion scraping for the specified .onion URL
  builtin <url>    - Use built-in onion scraper
  toc <url>        - Use TOC onion crawler
  onionsearch <q>  - Use OnionSearch with query
  torbot <url>     - Use TorBot crawler
  status           - Show current scraping status
  stop             - Stop the current scraping process
  help             - Show this help message
  quit/exit        - Exit the program

Examples:
  scrape http://duckduckgogg42ts72.onion
  builtin http://example.onion
  toc http://example.onion
  onionsearch "search query"
  status
  stop
        """
        print(help_text)

    def run_builtin_scraper(self, url: str):
        """Run the built-in onion scraper"""
        if not url.endswith('.onion') and '.onion' not in url:
            print(f"Error: Please provide a valid .onion URL: {url}")
            return 1

        print(f"🧅 Starting built-in onion scraper for: {url}")
        try:
            result = self.onion_runner.crawl_onion_site(url, save_to_file=True)
            if result:
                print(f"✅ Built-in onion scraping completed successfully!")
                print(f"📄 Data saved to: {result}")
                return 0
            else:
                print("❌ Built-in onion scraping failed")
                return 1
        except Exception as e:
            print(f"❌ Error during built-in onion scraping: {e}")
            return 1

    def run_toc_crawler(self, url: str):
        """Run TOC onion crawler"""
        if not url.endswith('.onion') and '.onion' not in url:
            print(f"Error: Please provide a valid .onion URL: {url}")
            return 1

        print(f"🧅 Starting TOC crawler for: {url}")
        try:
            result = self.onion_runner.run_toc_crawler(url)
            if result:
                print(f"✅ TOC crawling completed successfully!")
                return 0
            else:
                print("❌ TOC crawling failed")
                return 1
        except Exception as e:
            print(f"❌ Error during TOC crawling: {e}")
            return 1

    def run_onionsearch(self, query: str):
        """Run OnionSearch crawler"""
        print(f"🧅 Starting OnionSearch for query: {query}")
        try:
            result = self.onion_runner.run_onionsearch(query)
            if result:
                print(f"✅ OnionSearch completed successfully!")
                return 0
            else:
                print("❌ OnionSearch failed")
                return 1
        except Exception as e:
            print(f"❌ Error during OnionSearch: {e}")
            return 1

    def run_torbot(self, url: str):
        """Run TorBot crawler"""
        if not url.endswith('.onion') and '.onion' not in url:
            print(f"Error: Please provide a valid .onion URL: {url}")
            return 1

        print(f"🧅 Starting TorBot for: {url}")
        try:
            result = self.onion_runner.run_torbot(url)
            if result:
                print(f"✅ TorBot completed successfully!")
                return 0
            else:
                print("❌ TorBot failed")
                return 1
        except Exception as e:
            print(f"❌ Error during TorBot: {e}")
            return 1

    def run_single_scrape(self, url: str, max_depth: int, max_links: int,
                         progressive: bool, wait: bool):
        """Run a single scraping operation"""
        if not self.validate_url(url):
            print(f"Error: Invalid URL format: {url}")
            return 1

        # Check if it's an onion URL and use appropriate scraper
        if url.endswith('.onion') or '.onion' in url:
            print(f"🧅 Starting onion scraping of: {url}")
            return self.run_builtin_scraper(url)
        else:
            print(f"❌ This CLI now focuses on onion scraping. Please provide a .onion URL.")
            print(f"For regular web scraping, use the web interface at http://localhost:5000")
            return 1
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
        description="🧅 Onion Scraper CLI - Tor-enabled onion site scraping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive
  %(prog)s --url http://duckduckgogg42ts72.onion --depth 2 --links 3
  %(prog)s --builtin http://example.onion
  %(prog)s --toc http://example.onion
  %(prog)s --onionsearch "search query"
        """
    )
    
    parser.add_argument(
        '--url', '-u',
        help='Onion URL to start scraping from'
    )

    parser.add_argument(
        '--builtin',
        help='Use built-in onion scraper for the specified .onion URL'
    )

    parser.add_argument(
        '--toc',
        help='Use TOC crawler for the specified .onion URL'
    )

    parser.add_argument(
        '--onionsearch',
        help='Use OnionSearch with the specified search query'
    )

    parser.add_argument(
        '--torbot',
        help='Use TorBot for the specified .onion URL'
    )

    parser.add_argument(
        '--depth', '-d',
        type=int,
        default=2,
        help='Maximum depth to scrape (default: 2 for onion sites)'
    )

    parser.add_argument(
        '--links', '-l',
        type=int,
        default=3,
        help='Maximum links to extract per page (default: 3 for onion sites)'
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
    cli = OnionScraperCLI()

    try:
        if args.interactive:
            # Run in interactive mode
            cli.run_interactive_mode()
        elif args.builtin:
            # Use built-in onion scraper
            return cli.run_builtin_scraper(args.builtin)
        elif args.toc:
            # Use TOC crawler
            return cli.run_toc_crawler(args.toc)
        elif args.onionsearch:
            # Use OnionSearch
            return cli.run_onionsearch(args.onionsearch)
        elif args.torbot:
            # Use TorBot
            return cli.run_torbot(args.torbot)
        elif args.url:
            # Run single scraping operation with built-in scraper
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
