@echo off
REM 🧅 Live Graph System - Onion Scraper Launcher for Windows
REM Enhanced batch file with comprehensive onion scraper support

echo.
echo ========================================
echo   🧅 Live Graph System - Onion Scraper
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    echo.
    pause
    exit /b 1
)

REM Check for special onion scraper arguments
if "%1"=="--help" goto show_help
if "%1"=="-h" goto show_help
if "%1"=="--builtin" goto run_builtin
if "%1"=="--toc" goto run_toc
if "%1"=="--onionsearch" goto run_onionsearch
if "%1"=="--torbot" goto run_torbot
if "%1"=="--check-deps" goto check_dependencies

REM Default: Run the Python launcher
python run.py %*
goto end

:show_help
echo.
echo ========================================
echo   🧅 Live Graph System - Usage Guide
echo ========================================
echo.
echo Standard Usage:
echo   run.bat                    Start interactive launcher
echo   run.bat --web              Start onion scraper web interface
echo.
echo Onion Scraper Direct Usage:
echo   run.bat --builtin "URL"    Built-in Onion Scraper (Primary)
echo   run.bat --toc "URL"        TOC Onion Crawler
echo   run.bat --onionsearch "QUERY"  OnionSearch Engine
echo   run.bat --torbot "URL"     TorBot OSINT Crawler
echo   run.bat --check-deps       Check all dependencies
echo.
echo Examples:
echo   run.bat --builtin "http://duckduckgogg42ts72.onion"
echo   run.bat --toc "http://example.onion"
echo   run.bat --onionsearch "privacy tools"
echo   run.bat --torbot "http://example.onion"
echo.
echo Requirements:
echo   Built-in:       Python 3.7+, automatic Tor integration
echo   TOC Crawler:    Go 1.19+, TOR proxy (127.0.0.1:9050)
echo   OnionSearch:    Python packages (requests, bs4, PySocks, tqdm)
echo   TorBot:         Python packages (httpx, treelib, tabulate, toml)
echo.
echo For detailed setup: run.bat --check-deps
echo.
pause
goto end

:run_builtin
echo.
echo ========================================
echo   Built-in Onion Scraper (Direct Mode)
echo ========================================
echo.

if "%2"=="" (
    echo ERROR: Please provide a .onion URL
    echo Usage: run.bat --builtin "http://example.onion"
    echo Example: run.bat --builtin "http://duckduckgogg42ts72.onion"
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Built-in Onion Scraper...
echo Target URL: %2
echo Using built-in Tor integration with automatic fallback
echo.

python run.py --builtin %2
if errorlevel 1 (
    echo ERROR: Built-in onion scraper failed
    pause
    exit /b 1
)

echo ✅ Built-in onion scraping completed successfully
goto end

:run_toc
echo.
echo ========================================
echo   TOC Onion Crawler (Direct Mode)
echo ========================================
echo.

REM Check if Go is available
go version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Go programming language is not installed or not in PATH
    echo Please install Go 1.19+ from https://golang.org/dl/
    echo.
    pause
    exit /b 1
)

REM Check if TOR is running
echo Checking TOR proxy connection...
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', 9050); $client.Close(); Write-Host 'TOR proxy is running on 127.0.0.1:9050' } catch { Write-Host 'WARNING: TOR proxy not detected on 127.0.0.1:9050'; Write-Host 'Please start TOR daemon before using onion crawler' }"

if "%2"=="" (
    echo ERROR: Please provide a .onion URL
    echo Usage: run.bat --toc "http://example.onion"
    echo Example: run.bat --toc "http://facebookcorewwwi.onion"
    echo.
    pause
    exit /b 1
)

echo.
echo Starting TOC Onion Crawler...
echo Target URL: %2
echo.

cd onions\toc-main
if errorlevel 1 (
    echo ERROR: TOC directory not found at onions\toc-main
    echo Please ensure the toc-main directory exists
    pause
    exit /b 1
)

echo Running: go run main.go -url %2 -output ..\..\data\data.json
go run main.go -url %2 -output ..\..\data\data.json
if errorlevel 1 (
    echo ERROR: TOC crawler failed to execute
    echo Check that Go is installed and TOR proxy is running
    cd ..\..
    pause
    exit /b 1
)

echo ✅ TOC crawling completed successfully
cd ..\..
goto end

:run_onionsearch
echo.
echo ========================================
echo   OnionSearch Engine (Direct Mode)
echo ========================================
echo.

REM Check if required Python packages are available
python -c "import requests, bs4, socks, tqdm" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required Python packages not found
    echo Please install: pip install requests beautifulsoup4 PySocks tqdm
    echo.
    pause
    exit /b 1
)

if "%2"=="" (
    echo ERROR: Please provide a search query
    echo Usage: run.bat --onionsearch "search terms"
    echo Example: run.bat --onionsearch "privacy tools"
    echo Example: run.bat --onionsearch "secure messaging"
    echo.
    pause
    exit /b 1
)

echo.
echo Starting OnionSearch Engine...
echo Search Query: %2
echo.

cd onions\OnionSearch-master
if errorlevel 1 (
    echo ERROR: OnionSearch directory not found at onions\OnionSearch-master
    echo Please ensure the OnionSearch-master directory exists
    pause
    exit /b 1
)

echo Running: python -m onionsearch.core %2 --output onionsearch_results.csv --limit 5
python -m onionsearch.core %2 --output onionsearch_results.csv --limit 5
if errorlevel 1 (
    echo ERROR: OnionSearch failed to execute
    echo Check that required Python packages are installed
    cd ..\..
    pause
    exit /b 1
)

if exist onionsearch_results.csv (
    echo.
    echo Converting results to unified JSON format...
    python ..\..\backend\core\onion_data_converters.py --convert-csv onionsearch_results.csv --output ..\..\data\data.json --search-term %2
    if errorlevel 1 (
        echo ERROR: Failed to convert results to JSON
        cd ..\..
        pause
        exit /b 1
    )
    del onionsearch_results.csv
    echo ✅ OnionSearch completed successfully
) else (
    echo WARNING: No results file generated
)
cd ..\..
goto end

:run_torbot
echo.
echo ========================================
echo   TorBot OSINT Crawler (Direct Mode)
echo ========================================
echo.

REM Check if required Python packages are available
python -c "import httpx, beautifulsoup4, treelib, tabulate" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required Python packages not found
    echo Please install: pip install httpx[socks] beautifulsoup4 treelib tabulate toml
    echo.
    pause
    exit /b 1
)

if "%2"=="" (
    echo ERROR: Please provide a target URL
    echo Usage: run.bat --torbot "URL" [depth]
    echo Example: run.bat --torbot "https://example.com"
    echo Example: run.bat --torbot "http://example.onion" 3
    echo.
    pause
    exit /b 1
)

REM Set depth parameter (default 2)
set DEPTH=2
if not "%3"=="" set DEPTH=%3

echo.
echo Starting TorBot OSINT Crawler...
echo Target URL: %2
echo Crawl Depth: %DEPTH%
echo.

cd onions\TorBot-dev
if errorlevel 1 (
    echo ERROR: TorBot directory not found at onions\TorBot-dev
    echo Please ensure the TorBot-dev directory exists
    pause
    exit /b 1
)

echo Running: python main.py -u %2 --depth %DEPTH% --save json --quiet
python main.py -u %2 --depth %DEPTH% --save json --quiet
if errorlevel 1 (
    echo ERROR: TorBot failed to execute
    echo Check that required Python packages are installed
    cd ..\..
    pause
    exit /b 1
)

REM Find and convert the most recent JSON file
set FOUND_JSON=0
for %%f in (*.json) do (
    echo.
    echo Converting results to unified format...
    python ..\..\backend\core\onion_data_converters.py --convert-torbot "%%f" --output ..\..\data\data.json --starting-url %2
    if errorlevel 1 (
        echo ERROR: Failed to convert TorBot results
        del "%%f"
        cd ..\..
        pause
        exit /b 1
    )
    del "%%f"
    set FOUND_JSON=1
    goto torbot_conversion_done
)

:torbot_conversion_done
if %FOUND_JSON%==1 (
    echo ✅ TorBot OSINT crawling completed successfully
) else (
    echo WARNING: No JSON output file found from TorBot
)
cd ..\..
goto end

:check_dependencies
echo.
echo ========================================
echo   Dependency Check
echo ========================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found
) else (
    echo ✅ Python available
)

echo.
echo Checking Go...
go version >nul 2>&1
if errorlevel 1 (
    echo ❌ Go not found - required for TOC crawler
) else (
    echo ✅ Go available
    go version
)

echo.
echo Checking TOR proxy...
powershell -Command "try { $client = New-Object System.Net.Sockets.TcpClient; $client.Connect('127.0.0.1', 9050); $client.Close(); Write-Host '✅ TOR proxy running on 127.0.0.1:9050' } catch { Write-Host '❌ TOR proxy not running on 127.0.0.1:9050' }"

echo.
echo Checking Python packages for OnionSearch...
python -c "import requests; print('✅ requests')" 2>nul || echo ❌ requests
python -c "import bs4; print('✅ beautifulsoup4')" 2>nul || echo ❌ beautifulsoup4
python -c "import socks; print('✅ PySocks')" 2>nul || echo ❌ PySocks
python -c "import tqdm; print('✅ tqdm')" 2>nul || echo ❌ tqdm

echo.
echo Checking Python packages for TorBot...
python -c "import httpx; print('✅ httpx')" 2>nul || echo ❌ httpx
python -c "import treelib; print('✅ treelib')" 2>nul || echo ❌ treelib
python -c "import tabulate; print('✅ tabulate')" 2>nul || echo ❌ tabulate
python -c "import toml; print('✅ toml')" 2>nul || echo ❌ toml
python -c "import validators; print('✅ validators')" 2>nul || echo ❌ validators

echo.
echo Dependency check complete.
pause
goto end

:end
REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)
