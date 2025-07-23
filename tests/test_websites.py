#!/usr/bin/env python3
"""
Test Website Validation Script
Validates the test website collection and demonstrates web scraper functionality
"""

import os
import sys
import subprocess
import time
import requests
from urllib.parse import urljoin, urlparse
import json

def start_test_server(port=8002):
    """Start a local HTTP server for test websites"""
    test_dir = os.path.join(os.path.dirname(__file__), 'test-websites')
    
    if not os.path.exists(test_dir):
        print(f"❌ Test websites directory not found: {test_dir}")
        return None
    
    print(f"🚀 Starting test server on port {port}...")
    try:
        # Start Python HTTP server in test-websites directory
        process = subprocess.Popen([
            sys.executable, '-m', 'http.server', str(port)
        ], cwd=test_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(2)
        
        # Test if server is running
        test_url = f"http://localhost:{port}/index.html"
        response = requests.get(test_url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Test server running at http://localhost:{port}")
            return process
        else:
            print(f"❌ Server not responding properly")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start test server: {e}")
        return None

def validate_test_websites(base_url="http://localhost:8002"):
    """Validate that test websites are accessible and have proper link structure"""
    
    test_sites = [
        ("TechNews Central", "/index.html"),
        ("Corporate Site", "/corporate-site/index.html"),
        ("Blog Site", "/blog-site/index.html"),
        ("Documentation Site", "/documentation-site/index.html"),
        ("News Site", "/news-site/index.html"),
        ("Portfolio Site", "/portfolio-site/index.html"),
    ]
    
    print("\n🔍 Validating test websites...")
    
    results = {}
    
    for site_name, path in test_sites:
        url = base_url + path
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Count links in the page
                content = response.text.lower()
                link_count = content.count('<a href=')
                internal_links = content.count('href="index.html') + content.count('href="./') + content.count('href="../')
                external_links = content.count('href="../') - content.count('href="../test-websites/')
                
                results[site_name] = {
                    'status': 'OK',
                    'total_links': link_count,
                    'internal_links': internal_links,
                    'url': url
                }
                print(f"✅ {site_name}: {link_count} total links")
            else:
                results[site_name] = {
                    'status': f'HTTP {response.status_code}',
                    'url': url
                }
                print(f"❌ {site_name}: HTTP {response.status_code}")
                
        except Exception as e:
            results[site_name] = {
                'status': f'Error: {str(e)}',
                'url': url
            }
            print(f"❌ {site_name}: {str(e)}")
    
    return results

def test_web_scraper(base_url="http://localhost:8002"):
    """Test the web scraper with test websites"""
    
    print("\n🕷️ Testing web scraper with test websites...")
    
    # Test URLs
    test_urls = [
        f"{base_url}/index.html",
        f"{base_url}/corporate-site/index.html",
        f"{base_url}/blog-site/index.html"
    ]
    
    scraper_script = os.path.join(os.path.dirname(__file__), 'scraper_cli.py')
    
    if not os.path.exists(scraper_script):
        print("❌ Web scraper script not found")
        return False
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📊 Test {i}: Scraping {url}")
        try:
            # Run scraper with limited depth for testing
            result = subprocess.run([
                sys.executable, scraper_script,
                '--url', url,
                '--depth', '2',
                '--output', f'test_scrape_{i}.json'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ Scraping completed successfully")
                
                # Check if output file was created
                output_file = f'test_scrape_{i}.json'
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        if 'children' in data:
                            node_count = count_nodes(data)
                            print(f"📈 Generated {node_count} nodes in graph structure")
                        else:
                            print("⚠️ Unexpected data structure in output")
                    
                    # Clean up test file
                    os.remove(output_file)
                else:
                    print("⚠️ Output file not created")
            else:
                print(f"❌ Scraping failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Scraping timed out")
        except Exception as e:
            print(f"❌ Scraping error: {e}")
    
    return True

def count_nodes(data):
    """Recursively count nodes in the scraped data structure"""
    count = 1  # Count current node
    if 'children' in data and data['children']:
        for child in data['children']:
            count += count_nodes(child)
    return count

def generate_test_report(validation_results):
    """Generate a comprehensive test report"""
    
    print("\n📋 TEST REPORT")
    print("=" * 50)
    
    total_sites = len(validation_results)
    successful_sites = sum(1 for result in validation_results.values() if result['status'] == 'OK')
    total_links = sum(result.get('total_links', 0) for result in validation_results.values() if result['status'] == 'OK')
    
    print(f"Total Test Sites: {total_sites}")
    print(f"Successfully Loaded: {successful_sites}")
    print(f"Total Links Found: {total_links}")
    print(f"Success Rate: {(successful_sites/total_sites)*100:.1f}%")
    
    print("\nSite Details:")
    for site_name, result in validation_results.items():
        status = result['status']
        if status == 'OK':
            links = result.get('total_links', 0)
            print(f"  ✅ {site_name}: {links} links")
        else:
            print(f"  ❌ {site_name}: {status}")
    
    print("\nRecommended Test Commands:")
    print("  # Basic scraping test:")
    print("  python scraper_cli.py --url http://localhost:8002/index.html --depth 3")
    print("\n  # Deep hierarchical test:")
    print("  python scraper_cli.py --url http://localhost:8002/corporate-site/index.html --depth 4")
    print("\n  # Web interface test:")
    print("  python scraper_web_interface.py")
    print("  # Then use: http://localhost:8002/index.html")
    
    print("\n" + "=" * 50)

def main():
    """Main test function"""
    print("🧪 Test Website Collection Validator")
    print("=" * 40)
    
    # Start test server
    server_process = start_test_server()
    
    if not server_process:
        print("❌ Cannot start test server. Exiting.")
        return 1
    
    try:
        # Validate websites
        validation_results = validate_test_websites()
        
        # Test web scraper (optional)
        if '--skip-scraper' not in sys.argv:
            test_web_scraper()
        
        # Generate report
        generate_test_report(validation_results)
        
        print(f"\n🎉 Test validation complete!")
        print(f"🌐 Test websites available at: http://localhost:8002")
        print(f"📚 See test-websites/README.md for detailed usage instructions")
        
        if '--keep-server' in sys.argv:
            print("\n⏳ Keeping server running (use Ctrl+C to stop)...")
            try:
                server_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return 1
    
    finally:
        # Clean up server
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("🔌 Test server stopped")

if __name__ == "__main__":
    exit(main())
