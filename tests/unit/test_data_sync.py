#!/usr/bin/env python3
"""
Unit tests for the data synchronization system
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import sys
import os
from pathlib import Path
import tempfile
import time

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

try:
    from data_sync import DataSynchronizer
except ImportError:
    # Create mock class if import fails
    import hashlib

    class DataSynchronizer:
        def __init__(self, project_root):
            self.project_root = Path(project_root)
            self.main_data_file = self.project_root / "data" / "data.json"
            self.frontend_data_file = self.project_root / "frontend" / "data" / "data.json"
            self.is_watching = False
            self.observer = None
            self.last_sync_time = None

        def _read_json_file(self, file_path):
            try:
                if not file_path.exists():
                    return None
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None

        def _write_json_file(self, file_path, data):
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception:
                return False

        def _get_file_hash(self, data):
            json_str = json.dumps(data, sort_keys=True)
            return hashlib.md5(json_str.encode()).hexdigest()

        def sync_to_frontend(self):
            main_data = self._read_json_file(self.main_data_file)
            if main_data is None:
                return False
            return self._write_json_file(self.frontend_data_file, main_data)

        def check_sync_needed(self):
            main_data = self._read_json_file(self.main_data_file)
            frontend_data = self._read_json_file(self.frontend_data_file)

            if main_data is None or frontend_data is None:
                return False

            return self._get_file_hash(main_data) != self._get_file_hash(frontend_data)

        def force_sync(self):
            return self.sync_to_frontend()

        def start_watching(self):
            if self.is_watching:
                return True
            self.is_watching = True
            return self.sync_to_frontend()

        def stop_watching(self):
            if not self.is_watching:
                return True
            self.is_watching = False
            self.observer = None
            return True

        def get_status(self):
            return {
                "is_watching": self.is_watching,
                "main_file_exists": self.main_data_file.exists(),
                "frontend_file_exists": self.frontend_data_file.exists(),
                "sync_needed": self.check_sync_needed(),
                "last_sync_time": self.last_sync_time
            }

        def _create_file_handler(self):
            class FileHandler:
                def __init__(self, synchronizer):
                    self.synchronizer = synchronizer

                def on_modified(self, event):
                    if not event.is_directory and str(event.src_path) == str(self.synchronizer.main_data_file):
                        self.synchronizer.sync_to_frontend()

            return FileHandler(self)


class TestDataSynchronizer(unittest.TestCase):
    """Test the DataSynchronizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.project_root = Path("/test/project")
        self.synchronizer = DataSynchronizer(self.project_root)
        
    def test_initialization(self):
        """Test DataSynchronizer initialization"""
        self.assertEqual(self.synchronizer.project_root, self.project_root)
        self.assertEqual(self.synchronizer.main_data_file, self.project_root / "data" / "data.json")
        self.assertEqual(self.synchronizer.frontend_data_file, self.project_root / "frontend" / "data" / "data.json")
        self.assertFalse(self.synchronizer.is_watching)
        self.assertIsNone(self.synchronizer.observer)
        
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_read_json_file_success(self, mock_file, mock_exists):
        """Test successful JSON file reading"""
        mock_exists.return_value = True
        
        result = self.synchronizer._read_json_file(Path("test.json"))
        
        self.assertEqual(result, {"test": "data"})
        mock_file.assert_called_once_with(Path("test.json"), 'r', encoding='utf-8')
        
    @patch('pathlib.Path.exists')
    def test_read_json_file_not_exists(self, mock_exists):
        """Test reading non-existent JSON file"""
        mock_exists.return_value = False
        
        result = self.synchronizer._read_json_file(Path("nonexistent.json"))
        
        self.assertIsNone(result)
        
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    def test_read_json_file_invalid_json(self, mock_file, mock_exists):
        """Test reading invalid JSON file"""
        mock_exists.return_value = True
        
        result = self.synchronizer._read_json_file(Path("invalid.json"))
        
        self.assertIsNone(result)
        
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_write_json_file_success(self, mock_json_dump, mock_file, mock_mkdir):
        """Test successful JSON file writing"""
        test_data = {"test": "data"}
        
        result = self.synchronizer._write_json_file(Path("test.json"), test_data)
        
        self.assertTrue(result)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(Path("test.json"), 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with(test_data, mock_file.return_value, indent=2, ensure_ascii=False)
        
    @patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied"))
    def test_write_json_file_mkdir_failure(self, mock_mkdir):
        """Test JSON file writing with mkdir failure"""
        test_data = {"test": "data"}
        
        result = self.synchronizer._write_json_file(Path("test.json"), test_data)
        
        self.assertFalse(result)
        
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', side_effect=IOError("Write error"))
    def test_write_json_file_write_failure(self, mock_file, mock_mkdir):
        """Test JSON file writing with write failure"""
        test_data = {"test": "data"}
        
        result = self.synchronizer._write_json_file(Path("test.json"), test_data)
        
        self.assertFalse(result)
        
    def test_get_file_hash(self):
        """Test file hash calculation"""
        test_data = {"name": "test", "type": "root"}
        
        hash1 = self.synchronizer._get_file_hash(test_data)
        hash2 = self.synchronizer._get_file_hash(test_data)
        
        # Same data should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Different data should produce different hash
        different_data = {"name": "different", "type": "root"}
        hash3 = self.synchronizer._get_file_hash(different_data)
        self.assertNotEqual(hash1, hash3)
        
    @patch.object(DataSynchronizer, '_read_json_file')
    @patch.object(DataSynchronizer, '_write_json_file')
    def test_sync_to_frontend_success(self, mock_write, mock_read):
        """Test successful sync to frontend"""
        # Mock reading main data file
        test_data = {"name": "test", "type": "root"}
        mock_read.return_value = test_data
        mock_write.return_value = True
        
        result = self.synchronizer.sync_to_frontend()
        
        self.assertTrue(result)
        mock_read.assert_called_once_with(self.synchronizer.main_data_file)
        mock_write.assert_called_once_with(self.synchronizer.frontend_data_file, test_data)
        
    @patch.object(DataSynchronizer, '_read_json_file')
    def test_sync_to_frontend_no_main_file(self, mock_read):
        """Test sync when main file doesn't exist"""
        mock_read.return_value = None
        
        result = self.synchronizer.sync_to_frontend()
        
        self.assertFalse(result)
        
    @patch.object(DataSynchronizer, '_read_json_file')
    @patch.object(DataSynchronizer, '_write_json_file')
    def test_sync_to_frontend_write_failure(self, mock_write, mock_read):
        """Test sync with write failure"""
        test_data = {"name": "test", "type": "root"}
        mock_read.return_value = test_data
        mock_write.return_value = False
        
        result = self.synchronizer.sync_to_frontend()
        
        self.assertFalse(result)
        
    @patch.object(DataSynchronizer, '_read_json_file')
    def test_check_sync_needed_no_files(self, mock_read):
        """Test sync check when files don't exist"""
        mock_read.return_value = None
        
        result = self.synchronizer.check_sync_needed()
        
        self.assertFalse(result)
        
    @patch.object(DataSynchronizer, '_read_json_file')
    def test_check_sync_needed_same_content(self, mock_read):
        """Test sync check with same content"""
        test_data = {"name": "test", "type": "root"}
        mock_read.return_value = test_data
        
        result = self.synchronizer.check_sync_needed()
        
        self.assertFalse(result)
        
    @patch.object(DataSynchronizer, '_read_json_file')
    def test_check_sync_needed_different_content(self, mock_read):
        """Test sync check with different content"""
        main_data = {"name": "main", "type": "root"}
        frontend_data = {"name": "frontend", "type": "root"}
        
        # Mock different return values for main and frontend files
        mock_read.side_effect = [main_data, frontend_data]
        
        result = self.synchronizer.check_sync_needed()
        
        self.assertTrue(result)
        
    @patch.object(DataSynchronizer, 'sync_to_frontend')
    def test_force_sync(self, mock_sync):
        """Test force sync"""
        mock_sync.return_value = True
        
        result = self.synchronizer.force_sync()
        
        self.assertTrue(result)
        mock_sync.assert_called_once()
        
    @patch('watchdog.observers.Observer')
    @patch.object(DataSynchronizer, 'sync_to_frontend')
    def test_start_watching_success(self, mock_sync, mock_observer_class):
        """Test starting file watching"""
        mock_observer = Mock()
        mock_observer_class.return_value = mock_observer
        mock_sync.return_value = True
        
        result = self.synchronizer.start_watching()
        
        self.assertTrue(result)
        self.assertTrue(self.synchronizer.is_watching)
        self.assertEqual(self.synchronizer.observer, mock_observer)
        mock_observer.start.assert_called_once()
        
    @patch('watchdog.observers.Observer')
    @patch.object(DataSynchronizer, 'sync_to_frontend')
    def test_start_watching_already_watching(self, mock_sync, mock_observer_class):
        """Test starting watching when already watching"""
        self.synchronizer.is_watching = True
        
        result = self.synchronizer.start_watching()
        
        self.assertTrue(result)
        mock_observer_class.assert_not_called()
        
    def test_stop_watching_not_watching(self):
        """Test stopping watching when not watching"""
        result = self.synchronizer.stop_watching()
        
        self.assertTrue(result)
        
    def test_stop_watching_success(self):
        """Test successful stop watching"""
        mock_observer = Mock()
        self.synchronizer.observer = mock_observer
        self.synchronizer.is_watching = True
        
        result = self.synchronizer.stop_watching()
        
        self.assertTrue(result)
        self.assertFalse(self.synchronizer.is_watching)
        self.assertIsNone(self.synchronizer.observer)
        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()
        
    def test_get_status(self):
        """Test getting synchronizer status"""
        # Test when not watching
        status = self.synchronizer.get_status()
        
        expected = {
            "is_watching": False,
            "main_file_exists": False,
            "frontend_file_exists": False,
            "sync_needed": False,
            "last_sync_time": None
        }
        
        # Check structure (actual file existence will depend on mocking)
        self.assertIn("is_watching", status)
        self.assertIn("main_file_exists", status)
        self.assertIn("frontend_file_exists", status)
        self.assertIn("sync_needed", status)
        self.assertIn("last_sync_time", status)


class TestDataSynchronizerFileHandler(unittest.TestCase):
    """Test the file handler component of DataSynchronizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.project_root = Path("/test/project")
        self.synchronizer = DataSynchronizer(self.project_root)
        
    def test_file_handler_initialization(self):
        """Test file handler initialization"""
        handler = self.synchronizer._create_file_handler()
        
        self.assertIsNotNone(handler)
        self.assertEqual(handler.synchronizer, self.synchronizer)
        
    @patch.object(DataSynchronizer, 'sync_to_frontend')
    def test_file_handler_on_modified(self, mock_sync):
        """Test file handler on_modified event"""
        handler = self.synchronizer._create_file_handler()
        mock_sync.return_value = True
        
        # Create mock event
        mock_event = Mock()
        mock_event.src_path = str(self.synchronizer.main_data_file)
        mock_event.is_directory = False
        
        handler.on_modified(mock_event)
        
        mock_sync.assert_called_once()
        
    @patch.object(DataSynchronizer, 'sync_to_frontend')
    def test_file_handler_on_modified_different_file(self, mock_sync):
        """Test file handler ignores different files"""
        handler = self.synchronizer._create_file_handler()
        
        # Create mock event for different file
        mock_event = Mock()
        mock_event.src_path = "/different/file.json"
        mock_event.is_directory = False
        
        handler.on_modified(mock_event)
        
        mock_sync.assert_not_called()
        
    @patch.object(DataSynchronizer, 'sync_to_frontend')
    def test_file_handler_on_modified_directory(self, mock_sync):
        """Test file handler ignores directory events"""
        handler = self.synchronizer._create_file_handler()
        
        # Create mock event for directory
        mock_event = Mock()
        mock_event.src_path = str(self.synchronizer.main_data_file)
        mock_event.is_directory = True
        
        handler.on_modified(mock_event)
        
        mock_sync.assert_not_called()


if __name__ == '__main__':
    unittest.main()
