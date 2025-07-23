#!/bin/bash
# Live Graph System Launcher for Unix/Linux/Mac
# Enhanced shell script with onion scraper support

echo ""
echo "========================================"
echo "  Live Graph System Launcher"
echo "========================================"
echo ""

# Determine Python command
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python 3.7+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check for special onion scraper arguments
case "$1" in
    --help|-h)
        show_help
        ;;
    --toc)
        run_toc "$2"
        ;;
    --onionsearch)
        run_onionsearch "$2"
        ;;
    --torbot)
        run_torbot "$2" "$3"
        ;;
    --check-deps)
        check_dependencies
        ;;
    *)
        # Default: Run the Python launcher
        $PYTHON_CMD run.py "$@"
        ;;
esac

function show_help() {
    echo ""
    echo "========================================"
    echo "  Live Graph System - Usage Guide"
    echo "========================================"
    echo ""
    echo "Standard Usage:"
    echo "  ./run.sh                    Start interactive launcher"
    echo "  ./run.sh --web              Start web interface directly"
    echo ""
    echo "Onion Scraper Direct Usage:"
    echo "  ./run.sh --toc \"URL\"        TOC Onion Crawler"
    echo "  ./run.sh --onionsearch \"QUERY\"  OnionSearch Engine"
    echo "  ./run.sh --torbot \"URL\"     TorBot OSINT Crawler"
    echo "  ./run.sh --check-deps       Check all dependencies"
    echo ""
    echo "Examples:"
    echo "  ./run.sh --toc \"http://example.onion\""
    echo "  ./run.sh --onionsearch \"privacy tools\""
    echo "  ./run.sh --torbot \"https://example.com\""
    echo "  ./run.sh --torbot \"http://example.onion\" 3"
    echo ""
    echo "Requirements:"
    echo "  TOC Crawler:    Go 1.19+, TOR proxy (127.0.0.1:9050)"
    echo "  OnionSearch:    Python packages (requests, bs4, PySocks, tqdm)"
    echo "  TorBot:         Python packages (httpx, treelib, tabulate, toml)"
    echo ""
    echo "For detailed setup: ./run.sh --check-deps"
    echo ""
}

function run_toc() {
    echo ""
    echo "========================================"
    echo "  TOC Onion Crawler (Direct Mode)"
    echo "========================================"
    echo ""

    # Check if Go is available
    if ! command -v go &> /dev/null; then
        echo "ERROR: Go programming language is not installed or not in PATH"
        echo "Please install Go 1.19+ from https://golang.org/dl/"
        exit 1
    fi

    # Check if TOR is running
    echo "Checking TOR proxy connection..."
    if nc -z 127.0.0.1 9050 2>/dev/null; then
        echo "✅ TOR proxy is running on 127.0.0.1:9050"
    else
        echo "⚠️  WARNING: TOR proxy not detected on 127.0.0.1:9050"
        echo "Please start TOR daemon before using onion crawler"
        echo "On Ubuntu/Debian: sudo systemctl start tor"
        echo "On macOS: brew services start tor"
    fi

    if [ -z "$1" ]; then
        echo "ERROR: Please provide a .onion URL"
        echo "Usage: ./run.sh --toc \"http://example.onion\""
        echo "Example: ./run.sh --toc \"http://facebookcorewwwi.onion\""
        echo ""
        exit 1
    fi

    echo ""
    echo "Starting TOC Onion Crawler..."
    echo "Target URL: $1"
    echo ""

    if [ ! -d "onions/toc-main" ]; then
        echo "ERROR: TOC directory not found at onions/toc-main"
        echo "Please ensure the toc-main directory exists"
        exit 1
    fi

    cd onions/toc-main
    echo "Running: go run main.go -url \"$1\" -output ../../data/data.json"

    if ! go run main.go -url "$1" -output ../../data/data.json; then
        echo "ERROR: TOC crawler failed to execute"
        echo "Check that Go is installed and TOR proxy is running"
        cd ../..
        exit 1
    fi

    echo "✅ TOC crawling completed successfully"
    cd ../..
}

function run_onionsearch() {
    echo ""
    echo "========================================"
    echo "  OnionSearch Engine (Direct Mode)"
    echo "========================================"
    echo ""

    # Check if required Python packages are available
    if ! $PYTHON_CMD -c "import requests, bs4, socks, tqdm" 2>/dev/null; then
        echo "ERROR: Required Python packages not found"
        echo "Please install: pip install requests beautifulsoup4 PySocks tqdm"
        exit 1
    fi

    echo ""
    echo "Starting OnionSearch Engine..."
    echo "Usage: Provide search query as argument"
    echo ""

    if [ -z "$1" ]; then
        echo "ERROR: Please provide a search query"
        echo "Example: ./run.sh --onionsearch \"privacy tools\""
        exit 1
    fi

    if [ ! -d "onions/OnionSearch-master" ]; then
        echo "ERROR: OnionSearch directory not found"
        exit 1
    fi

    cd onions/OnionSearch-master
    $PYTHON_CMD -m onionsearch.core "$1" --output onionsearch_results.csv --limit 5

    if [ -f "onionsearch_results.csv" ]; then
        echo ""
        echo "Converting results to JSON format..."
        $PYTHON_CMD ../../backend/core/onion_data_converters.py --convert-csv onionsearch_results.csv --output ../../data/onionsearch_data.json
        rm onionsearch_results.csv
    fi
    cd ../..
}

function run_torbot() {
    echo ""
    echo "========================================"
    echo "  TorBot OSINT Crawler (Direct Mode)"
    echo "========================================"
    echo ""

    # Check if required Python packages are available
    if ! $PYTHON_CMD -c "import httpx, bs4, treelib, tabulate, toml" 2>/dev/null; then
        echo "ERROR: Required Python packages not found"
        echo "Please install: pip install httpx[socks] beautifulsoup4 treelib tabulate toml validators"
        exit 1
    fi

    echo ""
    echo "Starting TorBot OSINT Crawler..."
    echo "Usage: Provide target URL as argument"
    echo ""

    if [ -z "$1" ]; then
        echo "ERROR: Please provide a target URL"
        echo "Example: ./run.sh --torbot \"https://example.com\""
        echo "Example: ./run.sh --torbot \"http://example.onion\""
        exit 1
    fi

    if [ ! -d "onions/TorBot-dev" ]; then
        echo "ERROR: TorBot directory not found"
        exit 1
    fi

    # Set depth parameter (default 2)
    DEPTH=${2:-2}

    echo "Running TorBot with URL: $1 and depth: $DEPTH"

    cd onions/TorBot-dev
    $PYTHON_CMD main.py -u "$1" --depth "$DEPTH" --save json --quiet

    # Find and convert the generated JSON file
    if ls *.json 1> /dev/null 2>&1; then
        echo ""
        echo "Converting results to unified format..."
        for json_file in *.json; do
            $PYTHON_CMD ../../backend/core/onion_data_converters.py --convert-torbot "$json_file" --output ../../data/torbot_data.json --starting-url "$1"
            rm "$json_file"
            break  # Only process the first JSON file
        done
    else
        echo "No JSON output file found from TorBot"
    fi
    cd ../..
}

function check_dependencies() {
    echo ""
    echo "========================================"
    echo "  Dependency Check"
    echo "========================================"
    echo ""

    echo "Checking Python..."
    if command -v python3 &> /dev/null; then
        echo "✅ Python3 available: $(python3 --version)"
    elif command -v python &> /dev/null; then
        echo "✅ Python available: $(python --version)"
    else
        echo "❌ Python not found"
    fi

    echo ""
    echo "Checking Go..."
    if command -v go &> /dev/null; then
        echo "✅ Go available: $(go version)"
    else
        echo "❌ Go not found - required for TOC crawler"
    fi

    echo ""
    echo "Checking TOR proxy..."
    if nc -z 127.0.0.1 9050 2>/dev/null; then
        echo "✅ TOR proxy running on 127.0.0.1:9050"
    else
        echo "❌ TOR proxy not running on 127.0.0.1:9050"
    fi

    echo ""
    echo "Checking Python packages for OnionSearch..."
    $PYTHON_CMD -c "import requests; print('✅ requests')" 2>/dev/null || echo "❌ requests"
    $PYTHON_CMD -c "import bs4; print('✅ beautifulsoup4')" 2>/dev/null || echo "❌ beautifulsoup4"
    $PYTHON_CMD -c "import socks; print('✅ PySocks')" 2>/dev/null || echo "❌ PySocks"
    $PYTHON_CMD -c "import tqdm; print('✅ tqdm')" 2>/dev/null || echo "❌ tqdm"

    echo ""
    echo "Checking Python packages for TorBot..."
    $PYTHON_CMD -c "import httpx; print('✅ httpx')" 2>/dev/null || echo "❌ httpx"
    $PYTHON_CMD -c "import treelib; print('✅ treelib')" 2>/dev/null || echo "❌ treelib"
    $PYTHON_CMD -c "import tabulate; print('✅ tabulate')" 2>/dev/null || echo "❌ tabulate"
    $PYTHON_CMD -c "import toml; print('✅ toml')" 2>/dev/null || echo "❌ toml"
    $PYTHON_CMD -c "import validators; print('✅ validators')" 2>/dev/null || echo "❌ validators"

    echo ""
    echo "Dependency check complete."
}
