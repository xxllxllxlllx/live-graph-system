#!/usr/bin/env python3
"""
Test script for Tor integration with Live Graph System
Demonstrates how to use the onion scrapers with Tor proxy
"""

import sys
import logging
from pathlib import Path

# Add backend paths
sys.path.append(str(Path(__file__).parent / "backend" / "core"))

from onion_data_converters import OnionScraperRunner, TorProxy

def main():
    """Test Tor integration and onion scraping"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🧅 Live Graph System - Tor Integration Test")
    print("=" * 50)
    
    # Initialize components
    project_root = Path(__file__).parent
    runner = OnionScraperRunner(project_root)
    
    print("\n1. Testing Tor Connection")
    print("-" * 30)
    
    # Test Tor proxy
    tor_proxy = TorProxy()
    
    if not tor_proxy.check_tor_running():
        print("❌ Tor is not running!")
        print("💡 To use this feature:")
        print("   1. Download and install Tor Browser from: https://www.torproject.org/")
        print("   2. Start Tor Browser (this starts the Tor proxy on 127.0.0.1:9050)")
        print("   3. Or install Tor service and start it")
        print("   4. Install SOCKS support: pip install requests[socks]")
        print("   5. Make sure Tor proxy is running on 127.0.0.1:9050")
        print("\n🔧 Troubleshooting:")
        print("   - Check if Tor Browser is fully loaded (not just starting)")
        print("   - Verify no firewall is blocking port 9050")
        print("   - Try restarting Tor Browser")
        return False
    
    print("✅ Tor proxy is running on 127.0.0.1:9050")

    # Test proxy with regular site first
    print("🌐 Testing Tor proxy with regular website...")
    if tor_proxy.test_connection():
        print("✅ Tor proxy is working correctly")
    else:
        print("❌ Tor proxy test failed - check your Tor Browser setup")
        print("💡 Make sure Tor Browser is fully loaded and connected")

    print("\n2. Testing Popular Onion Sites")
    print("-" * 30)
    
    # Test popular onion sites
    results = runner.test_tor_connection()
    
    for site_name, result in results.items():
        status = result['status']
        if status == 'accessible':
            print(f"✅ {site_name}: Accessible")
        elif status.startswith('http_'):
            print(f"⚠️ {site_name}: {status}")
        else:
            print(f"❌ {site_name}: Failed")
    
    print("\n3. Demonstrating Onion Scraping")
    print("-" * 30)
    
    # Test scraping a popular onion site
    print("🦆 Scraping DuckDuckGo onion site...")
    result_file = runner.scrape_popular_onion_site('duckduckgo')
    
    if result_file:
        print(f"✅ Successfully scraped and saved to: {result_file}")
    else:
        print("❌ Failed to scrape onion site")
    
    print("\n4. Testing Ahmia Search Engine")
    print("-" * 30)
    
    # Test Ahmia search
    print("🔍 Searching via Ahmia onion search engine...")
    search_result = runner.run_onionsearch("privacy tools")
    
    if search_result:
        print(f"✅ Search completed, results saved to: {search_result}")
    else:
        print("❌ Search failed")
    
    print("\n5. Testing TOC Crawler")
    print("-" * 30)
    
    # Test TOC crawler
    print("🕷️ Running TOC crawler on DuckDuckGo onion...")
    toc_result = runner.run_toc_main(runner.popular_onion_sites['duckduckgo'])
    
    if toc_result:
        print(f"✅ TOC crawl completed, results saved to: {toc_result}")
    else:
        print("❌ TOC crawl failed")
    
    print("\n" + "=" * 50)
    print("🎉 Tor integration test completed!")
    print("\n📋 How Tor Proxying Works:")
    print("1. Tor creates a SOCKS5 proxy on 127.0.0.1:9050")
    print("2. Our scrapers connect through this proxy")
    print("3. Traffic is routed through 3 Tor nodes (Entry → Middle → Exit)")
    print("4. For .onion sites, traffic stays within Tor network")
    print("5. Provides anonymity and access to hidden services")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
