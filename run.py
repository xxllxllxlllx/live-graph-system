#!/usr/bin/env python3
"""
🧅 Live Graph System - Onion Scraper Launcher
Advanced onion site scraping with Tor integration and graph visualization
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent

def run_web_interface():
    """Launch the complete onion scraper web interface with visualization"""
    import threading
    import time

    print("🧅 Starting Live Graph System - Onion Scraper Interface...")
    print("📊 Starting graph visualization server...")
    print("🕷️  Starting onion scraper web interface...")
    print()
    print("📍 Onion Scraper Interface: http://localhost:5000")
    print("📍 Graph Visualization: http://localhost:8001")
    print("🧅 Features: Built-in Onion Scraper, TOC, OnionSearch, TorBot")
    print("🔒 Tor Integration: Automatic proxy detection and fallback")
    print("⏹️  Press Ctrl+C to stop both services")
    print()

    # Start the visualization server in a separate thread
    def start_visualization():
        frontend_dir = get_project_root() / "frontend"
        os.chdir(frontend_dir)
        try:
            subprocess.run([sys.executable, "-m", "http.server", "8001"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    viz_thread = threading.Thread(target=start_visualization, daemon=True)
    viz_thread.start()

    # Give the visualization server time to start
    time.sleep(2)
    print("✅ Graph visualization server started on port 8001")

    # Start the web scraper interface
    interfaces_dir = get_project_root() / "backend" / "interfaces"
    os.chdir(interfaces_dir)

    try:
        subprocess.run([sys.executable, "scraper_web_interface.py"])
    except KeyboardInterrupt:
        print("\n✅ Web interface stopped")
        print("✅ Graph visualization server stopped")

def run_cli():
    """Launch the onion scraper CLI interface"""
    interfaces_dir = get_project_root() / "backend" / "interfaces"
    os.chdir(interfaces_dir)

    print("🧅 Starting Onion Scraper CLI Interface...")
    print("🔒 Features: Built-in scraper, TOC, OnionSearch, TorBot")
    print("💡 Type 'help' for available commands")
    subprocess.run([sys.executable, "scraper_cli.py", "--interactive"])

def run_builtin_scraper(url):
    """Run built-in onion scraper directly"""
    interfaces_dir = get_project_root() / "backend" / "interfaces"
    os.chdir(interfaces_dir)

    print("🧅 Starting Built-in Onion Scraper...")
    print(f"📍 Target URL: {url}")
    print("🔒 Using built-in Tor integration")

    subprocess.run([sys.executable, "scraper_cli.py", "--builtin", url])

def run_toc_crawler(url):
    """Run TOC onion crawler directly"""
    print("🧅 Starting TOC Onion Crawler...")
    print(f"📍 Target URL: {url}")

    # Check if Go is available
    try:
        subprocess.run(["go", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ERROR: Go programming language not found")
        print("Please install Go 1.19+ from https://golang.org/dl/")
        return False

    # Check if TOR proxy is running
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        if result == 0:
            print("✅ TOR proxy detected on 127.0.0.1:9050")
        else:
            print("⚠️  WARNING: TOR proxy not detected on 127.0.0.1:9050")
    except:
        print("⚠️  WARNING: Could not check TOR proxy status")

    # Run TOC crawler
    toc_dir = get_project_root() / "onions" / "toc-main"
    if not toc_dir.exists():
        print(f"❌ ERROR: TOC directory not found at {toc_dir}")
        return False

    os.chdir(toc_dir)
    data_file = get_project_root() / "data" / "data.json"

    try:
        print(f"🚀 Running: go run main.go -url {url} -output {data_file}")
        subprocess.run(["go", "run", "main.go", "-url", url, "-output", str(data_file)], check=True)
        print("✅ TOC crawling completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ TOC crawler failed: {e}")
        return False

def run_onionsearch(query):
    """Run OnionSearch engine directly"""
    print("🔍 Starting OnionSearch Engine...")
    print(f"📍 Search Query: {query}")

    # Check required packages
    try:
        import requests, bs4, socks, tqdm
        print("✅ Required packages available")
    except ImportError as e:
        print(f"❌ ERROR: Required package missing: {e}")
        print("Please install: pip install requests beautifulsoup4 PySocks tqdm")
        return False

    # Run OnionSearch
    onionsearch_dir = get_project_root() / "onions" / "OnionSearch-master"
    if not onionsearch_dir.exists():
        print(f"❌ ERROR: OnionSearch directory not found at {onionsearch_dir}")
        return False

    os.chdir(onionsearch_dir)
    csv_file = "onionsearch_results.csv"

    try:
        print(f"🚀 Running: python -m onionsearch.core {query} --output {csv_file} --limit 5")
        subprocess.run([sys.executable, "-m", "onionsearch.core", query, "--output", csv_file, "--limit", "5"], check=True)

        # Convert to JSON
        if Path(csv_file).exists():
            print("🔄 Converting results to unified JSON format...")
            data_file = get_project_root() / "data" / "data.json"
            converter_script = get_project_root() / "backend" / "core" / "onion_data_converters.py"

            subprocess.run([
                sys.executable, str(converter_script),
                "--convert-csv", csv_file,
                "--output", str(data_file),
                "--search-term", query
            ], check=True)

            Path(csv_file).unlink()  # Clean up CSV file
            print("✅ OnionSearch completed successfully")
            return True
        else:
            print("⚠️  WARNING: No results file generated")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ OnionSearch failed: {e}")
        return False

def run_torbot(url, depth=2):
    """Run TorBot OSINT crawler directly"""
    print("🤖 Starting TorBot OSINT Crawler...")
    print(f"📍 Target URL: {url}")
    print(f"🔍 Crawl Depth: {depth}")

    # Check required packages
    try:
        import httpx, treelib, tabulate, toml
        print("✅ Required packages available")
    except ImportError as e:
        print(f"❌ ERROR: Required package missing: {e}")
        print("Please install: pip install httpx[socks] treelib tabulate toml validators")
        return False

    # Run TorBot
    torbot_dir = get_project_root() / "onions" / "TorBot-dev"
    if not torbot_dir.exists():
        print(f"❌ ERROR: TorBot directory not found at {torbot_dir}")
        return False

    os.chdir(torbot_dir)

    try:
        print(f"🚀 Running: python main.py -u {url} --depth {depth} --save json --quiet")
        subprocess.run([sys.executable, "main.py", "-u", url, "--depth", str(depth), "--save", "json", "--quiet"], check=True)

        # Find and convert the generated JSON file
        json_files = list(Path(".").glob("*.json"))
        if json_files:
            json_file = max(json_files, key=lambda f: f.stat().st_mtime)  # Most recent
            print("🔄 Converting results to unified JSON format...")

            data_file = get_project_root() / "data" / "data.json"
            converter_script = get_project_root() / "backend" / "core" / "onion_data_converters.py"

            subprocess.run([
                sys.executable, str(converter_script),
                "--convert-torbot", str(json_file),
                "--output", str(data_file),
                "--starting-url", url
            ], check=True)

            json_file.unlink()  # Clean up temp file
            print("✅ TorBot OSINT crawling completed successfully")
            return True
        else:
            print("⚠️  WARNING: No JSON output file found")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ TorBot failed: {e}")
        return False

def check_dependencies():
    """Check all system dependencies"""
    print("🔍 Checking System Dependencies...")
    print("=" * 50)

    # Check Python
    print(f"✅ Python: {sys.version.split()[0]}")

    # Check Go
    try:
        result = subprocess.run(["go", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Go: {result.stdout.strip()}")
        else:
            print("❌ Go: Not found")
    except FileNotFoundError:
        print("❌ Go: Not found - required for TOC crawler")

    # Check TOR proxy
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        if result == 0:
            print("✅ TOR proxy: Running on 127.0.0.1:9050")
        else:
            print("❌ TOR proxy: Not running on 127.0.0.1:9050")
    except:
        print("❌ TOR proxy: Connection check failed")

    # Check Python packages
    packages = {
        "OnionSearch": ["requests", "bs4", "socks", "tqdm"],
        "TorBot": ["httpx", "treelib", "tabulate", "toml", "validators"]
    }

    for scraper, pkg_list in packages.items():
        print(f"\n{scraper} packages:")
        for pkg in pkg_list:
            try:
                __import__(pkg)
                print(f"  ✅ {pkg}")
            except ImportError:
                print(f"  ❌ {pkg}")

def setup_system():
    """Run the setup script"""
    interfaces_dir = get_project_root() / "backend" / "interfaces"
    os.chdir(interfaces_dir)

    print("🔧 Setting up Live Graph System...")
    subprocess.run([sys.executable, "setup_scraper.py"])

def main():
    parser = argparse.ArgumentParser(
        description="🧅 Live Graph System - Onion Scraper Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --setup                    # Setup the system (first time)
  python run.py --web                      # Complete onion scraper web interface
  python run.py --cli                      # Command-line interface

Onion Scraper Direct Usage:
  python run.py --builtin "http://example.onion"       # Built-in Onion Scraper (Primary)
  python run.py --toc "http://example.onion"           # TOC Onion Crawler
  python run.py --onionsearch "privacy tools"          # OnionSearch Engine
  python run.py --torbot "http://example.onion"        # TorBot OSINT Crawler
  python run.py --check-deps                           # Check all dependencies
        """
    )

    parser.add_argument("--setup", action="store_true",
                       help="Setup the system (install dependencies)")
    parser.add_argument("--web", action="store_true",
                       help="Launch complete onion scraper web interface")
    parser.add_argument("--cli", action="store_true",
                       help="Launch onion scraper CLI interface")

    # Onion scraper arguments
    parser.add_argument("--builtin", type=str, metavar="URL",
                       help="Run built-in onion scraper on specified .onion URL (Primary)")
    parser.add_argument("--toc", type=str, metavar="URL",
                       help="Run TOC onion crawler on specified .onion URL")
    parser.add_argument("--onionsearch", type=str, metavar="QUERY",
                       help="Run OnionSearch engine with specified search query")
    parser.add_argument("--torbot", type=str, metavar="URL",
                       help="Run TorBot OSINT crawler on specified .onion URL")
    parser.add_argument("--depth", type=int, default=2, metavar="N",
                       help="Crawl depth for TorBot (default: 2)")
    parser.add_argument("--check-deps", action="store_true",
                       help="Check all system dependencies")

    args = parser.parse_args()

    if args.setup:
        setup_system()
    elif args.web:
        run_web_interface()
    elif args.cli:
        run_cli()
    elif args.builtin:
        run_builtin_scraper(args.builtin)
    elif args.toc:
        success = run_toc_crawler(args.toc)
        sys.exit(0 if success else 1)
    elif args.onionsearch:
        success = run_onionsearch(args.onionsearch)
        sys.exit(0 if success else 1)
    elif args.torbot:
        success = run_torbot(args.torbot, args.depth)
        sys.exit(0 if success else 1)
    elif args.check_deps:
        check_dependencies()
    else:
        print("🧅 Live Graph System - Onion Scraper Launcher")
        print("=" * 50)
        print("Choose an option:")
        print("1. Setup system (first time)")
        print("2. Complete onion scraper web interface")
        print("3. Onion scraper CLI interface")
        print("4. Built-in Onion Scraper (direct)")
        print("5. TOC Onion Crawler (direct)")
        print("6. OnionSearch Engine (direct)")
        print("7. TorBot OSINT Crawler (direct)")
        print("8. Check dependencies")
        print("9. Exit")

        while True:
            choice = input("\nEnter choice (1-9): ").strip()

            if choice == "1":
                setup_system()
                break
            elif choice == "2":
                run_web_interface()
                break
            elif choice == "3":
                run_cli()
                break
            elif choice == "4":
                url = input("Enter .onion URL: ").strip()
                if url:
                    run_builtin_scraper(url)
                else:
                    print("❌ .onion URL required")
                break
            elif choice == "5":
                url = input("Enter .onion URL: ").strip()
                if url:
                    run_toc_crawler(url)
                else:
                    print("❌ .onion URL required")
                break
            elif choice == "6":
                query = input("Enter search query: ").strip()
                if query:
                    run_onionsearch(query)
                else:
                    print("❌ Search query required")
                break
            elif choice == "7":
                url = input("Enter .onion URL: ").strip()
                if url:
                    depth_input = input("Enter crawl depth (default 2): ").strip()
                    depth = int(depth_input) if depth_input.isdigit() else 2
                    run_torbot(url, depth)
                else:
                    print("❌ .onion URL required")
                break
            elif choice == "8":
                check_dependencies()
                break
            elif choice == "9":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")

if __name__ == "__main__":
    main()
