#!/usr/bin/env python3
"""
Data synchronization utility for Live Graph System
Ensures data.json is available in the frontend directory for the visualization
"""

import os
import shutil
import time
import threading
import json
from pathlib import Path
import logging

# Try to import watchdog, fallback to polling if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️  Watchdog not available, using polling mode for data synchronization")

logger = logging.getLogger(__name__)

class DataSyncHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    """File system event handler for data.json synchronization"""
    
    def __init__(self, source_path, target_path):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.last_sync = 0
        self.sync_delay = 1  # Minimum seconds between syncs
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        if Path(event.src_path).name == "data.json":
            self.sync_data_file()
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        if Path(event.src_path).name == "data.json":
            self.sync_data_file()
    
    def sync_data_file(self):
        """Synchronize data.json from source to target"""
        current_time = time.time()
        
        # Prevent too frequent syncing
        if current_time - self.last_sync < self.sync_delay:
            return
            
        try:
            if self.source_path.exists():
                # Ensure target directory exists
                self.target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(self.source_path, self.target_path)
                self.last_sync = current_time
                
                logger.info(f"Data synchronized: {self.source_path} -> {self.target_path}")
                print(f"📊 Data synchronized: data.json updated in frontend")
            else:
                logger.warning(f"Source data file not found: {self.source_path}")
                
        except Exception as e:
            logger.error(f"Failed to sync data file: {e}")
            print(f"❌ Failed to sync data file: {e}")

class DataSynchronizer:
    """Main data synchronization manager"""
    
    def __init__(self, project_root=None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        else:
            project_root = Path(project_root)
            
        self.project_root = project_root
        self.source_dir = project_root / "data"
        self.source_file = self.source_dir / "data.json"
        self.target_dir = project_root / "frontend" / "data"
        self.target_file = self.target_dir / "data.json"
        
        self.observer = None
        self.handler = None
        self.polling_thread = None
        self.polling_active = False
        self.last_sync_time = None
        self.is_watching = False
        self.main_data_file = self.source_file
        self.frontend_data_file = self.target_file
        self.observer = None

    def _read_json_file(self, file_path):
        """Read JSON data from a file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON file {file_path}: {e}")
            return None

    def _write_json_file(self, file_path, data):
        """Write JSON data to a file"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON file {file_path}: {e}")
            return False

    def setup_directories(self):
        """Ensure all necessary directories exist"""
        try:
            # Create source directory if it doesn't exist
            self.source_dir.mkdir(parents=True, exist_ok=True)
            
            # Create target directory if it doesn't exist
            self.target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create default data.json if it doesn't exist
            if not self.source_file.exists():
                self.create_default_data_file()
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup directories: {e}")
            return False
    
    def create_default_data_file(self):
        """Create a default data.json file"""
        default_data = {
            "name": "Live Graph System",
            "type": "root",
            "description": "No data available - start scraping to populate the graph",
            "url": "system://root",
            "children": [
                {
                    "name": "Getting Started",
                    "type": "category",
                    "description": "Use the web interface to start scraping",
                    "url": "system://help",
                    "children": [
                        {
                            "name": "HTTP/HTTPS Scraper",
                            "type": "item",
                            "description": "Scrape regular websites",
                            "url": "system://http-scraper",
                            "children": []
                        },
                        {
                            "name": "TOC Onion Crawler",
                            "type": "item",
                            "description": "Deep crawl .onion sites",
                            "url": "system://toc-crawler",
                            "children": []
                        },
                        {
                            "name": "OnionSearch Engine",
                            "type": "item",
                            "description": "Search multiple onion search engines",
                            "url": "system://onion-search",
                            "children": []
                        }
                    ]
                }
            ]
        }
        
        try:
            import json
            with open(self.source_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Created default data file: {self.source_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create default data file: {e}")
            return False
    
    def initial_sync(self):
        """Perform initial synchronization"""
        try:
            if self.source_file.exists():
                shutil.copy2(self.source_file, self.target_file)
                logger.info("Initial data synchronization completed")
                print("📊 Initial data synchronization completed")
                return True
            else:
                logger.warning("Source data file not found for initial sync")
                return False
        except Exception as e:
            logger.error(f"Initial sync failed: {e}")
            print(f"❌ Initial sync failed: {e}")
            return False
    
    def _polling_worker(self):
        """Polling worker for when watchdog is not available"""
        last_mtime = 0

        while self.polling_active:
            try:
                if self.source_file.exists():
                    current_mtime = self.source_file.stat().st_mtime
                    if current_mtime > last_mtime:
                        self.initial_sync()  # Reuse the sync logic
                        last_mtime = current_mtime

                time.sleep(2)  # Check every 2 seconds

            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(5)  # Wait longer on error

    def start_watching(self):
        """Start watching for data file changes"""
        try:
            if not self.setup_directories():
                return False

            # Perform initial sync
            self.initial_sync()

            if WATCHDOG_AVAILABLE:
                # Setup file watcher
                self.handler = DataSyncHandler(self.source_file, self.target_file)
                self.observer = Observer()
                self.observer.schedule(self.handler, str(self.source_dir), recursive=False)

                # Start watching
                self.observer.start()
                logger.info("Data file watcher started (watchdog mode)")
                print("👁️  Data file watcher started - data.json will be automatically synchronized")
            else:
                # Use polling mode
                self.polling_active = True
                self.polling_thread = threading.Thread(target=self._polling_worker, daemon=True)
                self.polling_thread.start()
                logger.info("Data file watcher started (polling mode)")
                print("👁️  Data file watcher started (polling mode) - data.json will be automatically synchronized")

            return True

        except Exception as e:
            logger.error(f"Failed to start data watcher: {e}")
            print(f"❌ Failed to start data watcher: {e}")
            return False
    
    def stop_watching(self):
        """Stop watching for data file changes"""
        try:
            if WATCHDOG_AVAILABLE and self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
                logger.info("Data file watcher stopped (watchdog mode)")
                print("🛑 Data file watcher stopped")
            elif self.polling_active:
                self.polling_active = False
                if self.polling_thread and self.polling_thread.is_alive():
                    self.polling_thread.join(timeout=5)
                logger.info("Data file watcher stopped (polling mode)")
                print("🛑 Data file watcher stopped")
        except Exception as e:
            logger.error(f"Error stopping data watcher: {e}")
    
    def force_sync(self):
        """Force synchronization of data file"""
        if self.handler:
            self.handler.sync_data_file()
        else:
            self.initial_sync()

    def clear_data_files(self):
        """Clear both data.json files (main and frontend copy)"""
        try:
            # Clear main data file
            if self.source_file.exists():
                self.source_file.unlink()
                logger.info(f"Cleared main data file: {self.source_file}")

            # Clear frontend data file
            if self.target_file.exists():
                self.target_file.unlink()
                logger.info(f"Cleared frontend data file: {self.target_file}")

            print("🗑️  Data files cleared - ready for new scraping session")
            return True

        except Exception as e:
            logger.error(f"Failed to clear data files: {e}")
            print(f"❌ Failed to clear data files: {e}")
            return False

    def sync_to_frontend(self):
        """Synchronize data from main file to frontend"""
        try:
            data = self._read_json_file(self.source_file)
            if data is None:
                return False

            success = self._write_json_file(self.target_file, data)
            if success:
                self.last_sync_time = time.time()
            return success
        except Exception as e:
            logger.error(f"Failed to sync to frontend: {e}")
            return False

    def get_status(self):
        """Get current synchronization status"""
        try:
            main_exists = self.source_file.exists()
            frontend_exists = self.target_file.exists()

            # Check if sync is needed
            sync_needed = False
            if main_exists and frontend_exists:
                try:
                    main_mtime = self.source_file.stat().st_mtime
                    frontend_mtime = self.target_file.stat().st_mtime
                    sync_needed = main_mtime > frontend_mtime
                except Exception:
                    sync_needed = True
            elif main_exists and not frontend_exists:
                sync_needed = True

            return {
                "is_watching": self.polling_active or (self.observer and self.observer.is_alive()),
                "main_file_exists": main_exists,
                "frontend_file_exists": frontend_exists,
                "sync_needed": sync_needed,
                "last_sync_time": self.last_sync_time
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {
                "is_watching": False,
                "main_file_exists": False,
                "frontend_file_exists": False,
                "sync_needed": False,
                "last_sync_time": None
            }

    def force_sync(self):
        """Force synchronization from main file to frontend"""
        try:
            return self.sync_to_frontend()
        except Exception as e:
            logger.error(f"Failed to force sync: {e}")
            return False

    def check_sync_needed(self):
        """Check if synchronization is needed"""
        try:
            main_data = self._read_json_file(self.source_file)
            frontend_data = self._read_json_file(self.target_file)

            if main_data is None and frontend_data is None:
                return False
            if main_data is None or frontend_data is None:
                return True

            # Compare data content
            return main_data != frontend_data
        except Exception as e:
            logger.error(f"Failed to check sync needed: {e}")
            return True

    def _get_file_hash(self, data):
        """Get hash of file data"""
        import hashlib
        try:
            data_str = json.dumps(data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to get file hash: {e}")
            return None

    def start_watching(self):
        """Start watching for file changes"""
        try:
            if self.is_watching:
                return True

            # Initial sync
            self.sync_to_frontend()

            # Start file watching
            from watchdog.observers import Observer
            self.observer = Observer()
            handler = self._create_file_handler()
            self.observer.schedule(handler, str(self.source_file.parent), recursive=False)
            self.observer.start()
            self.is_watching = True

            print("👁️  Data file watcher started - data.json will be automatically synchronized")
            return True
        except Exception as e:
            logger.error(f"Failed to start watching: {e}")
            return False

    def stop_watching(self):
        """Stop watching for file changes"""
        try:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            self.observer = None
            self.is_watching = False
            print("🛑 Data file watcher stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop watching: {e}")
            return None

    def _create_file_handler(self):
        """Create file change handler"""
        from watchdog.events import FileSystemEventHandler

        class DataFileHandler(FileSystemEventHandler):
            def __init__(self, synchronizer):
                self.synchronizer = synchronizer

            def on_modified(self, event):
                if event.is_directory:
                    return
                if Path(event.src_path) == self.synchronizer.source_file:
                    self.synchronizer.sync_to_frontend()

        return DataFileHandler(self)

def start_data_sync(project_root=None):
    """Start data synchronization service"""
    synchronizer = DataSynchronizer(project_root)
    return synchronizer.start_watching()

def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Graph System Data Synchronizer")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    synchronizer = DataSynchronizer(args.project_root)
    
    if synchronizer.start_watching():
        if args.daemon:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping data synchronizer...")
                synchronizer.stop_watching()
        else:
            print("✅ Data synchronizer started successfully")
            print("Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping data synchronizer...")
                synchronizer.stop_watching()
    else:
        print("❌ Failed to start data synchronizer")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
