#!/usr/bin/env python3
"""
End-to-end tests for graph visualization functionality
Tests D3.js integration, data rendering, and interactive features
"""

import pytest
import unittest
import json
import tempfile
import time
import subprocess
import requests
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend" / "core"))

from data_sync import DataSynchronizer


class TestGraphVisualization(unittest.TestCase):
    """Test graph visualization end-to-end functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.data_file = self.temp_dir / "data.json"
        self.frontend_data_file = self.temp_dir / "frontend" / "data" / "data.json"
        self.frontend_data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Visualization server setup
        self.viz_server_port = 8001
        self.viz_server_process = None
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.viz_server_process:
            self.viz_server_process.terminate()
            self.viz_server_process.wait()
            
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def create_test_visualization_data(self):
        """Create comprehensive test data for visualization"""
        return {
            "name": "Live Graph System Test Data",
            "type": "root",
            "description": "Comprehensive test data for graph visualization",
            "children": [
                {
                    "name": "Web Scraping Results",
                    "type": "category",
                    "description": "Results from HTTP/HTTPS scraping",
                    "children": [
                        {
                            "name": "Example.com",
                            "type": "subcategory",
                            "description": "URL: http://example.com",
                            "url": "http://example.com",
                            "children": [
                                {
                                    "name": "About Page",
                                    "type": "item",
                                    "description": "URL: http://example.com/about",
                                    "url": "http://example.com/about",
                                    "children": []
                                },
                                {
                                    "name": "Contact Page",
                                    "type": "item",
                                    "description": "URL: http://example.com/contact",
                                    "url": "http://example.com/contact",
                                    "children": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Onion Search Results",
                    "type": "category",
                    "description": "Results from OnionSearch engines",
                    "children": [
                        {
                            "name": "Ahmia",
                            "type": "subcategory",
                            "description": "URL: onion://ahmia",
                            "url": "onion://ahmia",
                            "children": [
                                {
                                    "name": "Privacy Tools",
                                    "type": "item",
                                    "description": "URL: http://privacy.onion",
                                    "url": "http://privacy.onion",
                                    "children": []
                                },
                                {
                                    "name": "Secure Email",
                                    "type": "item",
                                    "description": "URL: http://email.onion",
                                    "url": "http://email.onion",
                                    "children": []
                                }
                            ]
                        },
                        {
                            "name": "DarkSearch",
                            "type": "subcategory",
                            "description": "URL: onion://darksearch",
                            "url": "onion://darksearch",
                            "children": [
                                {
                                    "name": "Anonymous Chat",
                                    "type": "item",
                                    "description": "URL: http://chat.onion",
                                    "url": "http://chat.onion",
                                    "children": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "TOC Crawl Results",
                    "type": "category",
                    "description": "Results from TOC onion crawler",
                    "children": [
                        {
                            "name": "Hidden Services",
                            "type": "subcategory",
                            "description": "URL: http://services.onion",
                            "url": "http://services.onion",
                            "children": [
                                {
                                    "name": "VPN Service",
                                    "type": "item",
                                    "description": "URL: http://services.onion/vpn",
                                    "url": "http://services.onion/vpn",
                                    "children": []
                                },
                                {
                                    "name": "File Sharing",
                                    "type": "item",
                                    "description": "URL: http://services.onion/files",
                                    "url": "http://services.onion/files",
                                    "children": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
    def start_visualization_server(self):
        """Start the visualization server for testing"""
        # Create a simple HTML file for testing
        frontend_dir = self.temp_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        # Copy or create the visualization files
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Live Graph Visualization - Test</title>
            <style>
                body { margin: 0; padding: 20px; background: white; color: black; }
                #graph-container { width: 100%; height: 600px; border: 1px solid black; }
                .node circle { fill: #fff; stroke: steelblue; stroke-width: 1.5px; }
                .node text { font: 12px sans-serif; }
                .link { fill: none; stroke: #ccc; stroke-width: 1.5px; }
            </style>
            <script src="https://d3js.org/d3.v3.min.js"></script>
        </head>
        <body>
            <h1>Live Graph Visualization</h1>
            <div id="graph-container"></div>
            
            <script>
                // Basic D3.js visualization setup
                var margin = [20, 60, 20, 60],
                    width = 800 - margin[1] - margin[3],
                    height = 600 - margin[0] - margin[2],
                    i = 0,
                    duration = 750,
                    root;

                var tree = d3.layout.tree()
                    .size([height, width]);

                var diagonal = d3.svg.diagonal()
                    .projection(function(d) { return [d.y, d.x]; });

                var svg = d3.select("#graph-container").append("svg:svg")
                    .attr("width", width + margin[1] + margin[3])
                    .attr("height", height + margin[0] + margin[2])
                    .append("svg:g")
                    .attr("transform", "translate(" + margin[3] + "," + margin[0] + ")");

                // Load and display data
                function loadData() {
                    d3.json("data/data.json", function(error, flare) {
                        if (error) {
                            console.error("Error loading data:", error);
                            return;
                        }
                        
                        root = flare;
                        root.x0 = height / 2;
                        root.y0 = 0;

                        function collapse(d) {
                            if (d.children) {
                                d._children = d.children;
                                d._children.forEach(collapse);
                                d.children = null;
                            }
                        }

                        root.children.forEach(collapse);
                        update(root);
                    });
                }

                function update(source) {
                    var nodes = tree.nodes(root).reverse(),
                        links = tree.links(nodes);

                    nodes.forEach(function(d) { d.y = d.depth * 180; });

                    var node = svg.selectAll("g.node")
                        .data(nodes, function(d) { return d.id || (d.id = ++i); });

                    var nodeEnter = node.enter().append("svg:g")
                        .attr("class", "node")
                        .attr("transform", function(d) { 
                            return "translate(" + source.y0 + "," + source.x0 + ")"; 
                        })
                        .on("click", function(d) { toggle(d); update(d); });

                    nodeEnter.append("svg:circle")
                        .attr("r", 1e-6)
                        .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

                    nodeEnter.append("svg:text")
                        .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
                        .attr("dy", ".35em")
                        .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
                        .text(function(d) { return d.name; })
                        .style("fill-opacity", 1e-6);

                    var nodeUpdate = node.transition()
                        .duration(duration)
                        .attr("transform", function(d) { 
                            return "translate(" + d.y + "," + d.x + ")"; 
                        });

                    nodeUpdate.select("circle")
                        .attr("r", 4.5)
                        .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

                    nodeUpdate.select("text")
                        .style("fill-opacity", 1);

                    var link = svg.selectAll("path.link")
                        .data(links, function(d) { return d.target.id; });

                    link.enter().insert("svg:path", "g")
                        .attr("class", "link")
                        .attr("d", function(d) {
                            var o = {x: source.x0, y: source.y0};
                            return diagonal({source: o, target: o});
                        })
                        .transition()
                        .duration(duration)
                        .attr("d", diagonal);

                    link.transition()
                        .duration(duration)
                        .attr("d", diagonal);
                }

                function toggle(d) {
                    if (d.children) {
                        d._children = d.children;
                        d.children = null;
                    } else {
                        d.children = d._children;
                        d._children = null;
                    }
                }

                // Auto-refresh data every 5 seconds
                function autoRefresh() {
                    loadData();
                    setTimeout(autoRefresh, 5000);
                }

                // Initialize
                loadData();
                autoRefresh();
                
                // Expose functions for testing
                window.testFunctions = {
                    loadData: loadData,
                    update: update,
                    toggle: toggle
                };
            </script>
        </body>
        </html>
        """
        
        with open(frontend_dir / "index.html", 'w') as f:
            f.write(html_content)
            
        # Start HTTP server for visualization
        try:
            self.viz_server_process = subprocess.Popen([
                sys.executable, '-m', 'http.server', str(self.viz_server_port)
            ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(2)  # Wait for server to start
            
            # Test if server is running
            test_url = f"http://localhost:{self.viz_server_port}/index.html"
            response = requests.get(test_url, timeout=5)
            
            if response.status_code == 200:
                return test_url
            else:
                raise Exception("Visualization server not responding")
                
        except Exception as e:
            if self.viz_server_process:
                self.viz_server_process.terminate()
            raise e
            
    def test_data_synchronization_for_visualization(self):
        """Test data synchronization between backend and visualization"""
        # Create test data
        test_data = self.create_test_visualization_data()
        
        # Save to main data file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
            
        # Set up synchronizer
        synchronizer = DataSynchronizer(self.temp_dir)
        
        # Test initial sync
        sync_result = synchronizer.sync_to_frontend()
        self.assertTrue(sync_result)
        
        # Verify frontend data file exists
        self.assertTrue(self.frontend_data_file.exists())
        
        # Verify data integrity
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            frontend_data = json.load(f)
            
        self.assertEqual(frontend_data, test_data)
        
        # Test data update and re-sync
        test_data['name'] = 'Updated Test Data'
        test_data['children'].append({
            "name": "New Category",
            "type": "category",
            "description": "Newly added category",
            "children": []
        })
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
            
        # Check if sync is needed
        sync_needed = synchronizer.check_sync_needed()
        self.assertTrue(sync_needed)
        
        # Perform sync
        sync_result = synchronizer.sync_to_frontend()
        self.assertTrue(sync_result)
        
        # Verify updated data
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            updated_frontend_data = json.load(f)
            
        self.assertEqual(updated_frontend_data['name'], 'Updated Test Data')
        self.assertEqual(len(updated_frontend_data['children']), 4)
        
    def test_visualization_data_structure_validation(self):
        """Test that data structure is valid for D3.js visualization"""
        test_data = self.create_test_visualization_data()
        
        def validate_d3_structure(node, path="root"):
            """Validate data structure for D3.js compatibility"""
            # Required fields for D3.js tree layout
            required_fields = ["name"]
            for field in required_fields:
                self.assertIn(field, node, f"Missing required field '{field}' at {path}")
                
            # Name should be a string
            self.assertIsInstance(node["name"], str, f"Name should be string at {path}")
            
            # Children should be a list if present
            if "children" in node:
                self.assertIsInstance(node["children"], list, f"Children should be list at {path}")
                
                # Recursively validate children
                for i, child in enumerate(node["children"]):
                    validate_d3_structure(child, f"{path}.children[{i}]")
                    
            # Additional fields should be valid
            if "type" in node:
                valid_types = ["root", "category", "subcategory", "item"]
                self.assertIn(node["type"], valid_types, f"Invalid type at {path}")
                
        validate_d3_structure(test_data)
        
    def test_visualization_server_accessibility(self):
        """Test that visualization server is accessible and functional"""
        # Create and save test data
        test_data = self.create_test_visualization_data()
        
        # Set up frontend data directory
        frontend_data_dir = self.temp_dir / "frontend" / "data"
        frontend_data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(frontend_data_dir / "data.json", 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
            
        # Start visualization server
        viz_url = self.start_visualization_server()
        
        # Test server accessibility
        response = requests.get(viz_url, timeout=10)
        self.assertEqual(response.status_code, 200)
        
        # Verify HTML content
        html_content = response.text
        self.assertIn("Live Graph Visualization", html_content)
        self.assertIn("graph-container", html_content)
        self.assertIn("d3.js", html_content.lower())
        
        # Test data file accessibility
        data_url = f"http://localhost:{self.viz_server_port}/data/data.json"
        data_response = requests.get(data_url, timeout=5)
        self.assertEqual(data_response.status_code, 200)
        
        # Verify data content
        loaded_data = data_response.json()
        self.assertEqual(loaded_data, test_data)
        
    def test_real_time_data_updates(self):
        """Test real-time data updates in visualization"""
        # Create initial data
        initial_data = {
            "name": "Initial Data",
            "type": "root",
            "description": "Initial test data",
            "children": [
                {
                    "name": "Category 1",
                    "type": "category",
                    "description": "First category",
                    "children": []
                }
            ]
        }
        
        # Set up data files
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)
            
        synchronizer = DataSynchronizer(self.temp_dir)
        synchronizer.sync_to_frontend()
        
        # Simulate data update
        updated_data = {
            "name": "Updated Data",
            "type": "root",
            "description": "Updated test data",
            "children": [
                {
                    "name": "Category 1",
                    "type": "category",
                    "description": "First category",
                    "children": [
                        {
                            "name": "New Item",
                            "type": "item",
                            "description": "Newly added item",
                            "children": []
                        }
                    ]
                },
                {
                    "name": "Category 2",
                    "type": "category",
                    "description": "Second category",
                    "children": []
                }
            ]
        }
        
        # Update main data file
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2)
            
        # Test automatic sync detection
        sync_needed = synchronizer.check_sync_needed()
        self.assertTrue(sync_needed)
        
        # Perform sync
        sync_result = synchronizer.sync_to_frontend()
        self.assertTrue(sync_result)
        
        # Verify updated data in frontend
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            frontend_data = json.load(f)
            
        self.assertEqual(frontend_data['name'], 'Updated Data')
        self.assertEqual(len(frontend_data['children']), 2)
        self.assertEqual(len(frontend_data['children'][0]['children']), 1)
        
    def test_large_dataset_visualization(self):
        """Test visualization with large datasets"""
        # Create a large dataset
        large_data = {
            "name": "Large Dataset Test",
            "type": "root",
            "description": "Large dataset for performance testing",
            "children": []
        }
        
        # Generate multiple categories with many items
        for cat_i in range(10):  # 10 categories
            category = {
                "name": f"Category {cat_i + 1}",
                "type": "category",
                "description": f"Category {cat_i + 1} description",
                "children": []
            }
            
            for item_i in range(20):  # 20 items per category
                item = {
                    "name": f"Item {cat_i + 1}.{item_i + 1}",
                    "type": "item",
                    "description": f"Item {cat_i + 1}.{item_i + 1} description",
                    "children": []
                }
                category["children"].append(item)
                
            large_data["children"].append(category)
            
        # Test data size
        total_nodes = 1 + 10 + (10 * 20)  # root + categories + items = 211 nodes
        self.assertEqual(self._count_nodes(large_data), total_nodes)
        
        # Test serialization performance
        start_time = time.time()
        json_str = json.dumps(large_data)
        serialization_time = time.time() - start_time
        
        # Should serialize quickly (under 1 second)
        self.assertLess(serialization_time, 1.0)
        
        # Test file I/O performance
        start_time = time.time()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(large_data, f, indent=2)
        write_time = time.time() - start_time
        
        # Should write quickly (under 2 seconds)
        self.assertLess(write_time, 2.0)
        
        # Test synchronization performance
        synchronizer = DataSynchronizer(self.temp_dir)
        start_time = time.time()
        sync_result = synchronizer.sync_to_frontend()
        sync_time = time.time() - start_time
        
        self.assertTrue(sync_result)
        # Should sync quickly (under 3 seconds)
        self.assertLess(sync_time, 3.0)
        
    def _count_nodes(self, node):
        """Recursively count nodes in data structure"""
        count = 1  # Count current node
        if "children" in node:
            for child in node["children"]:
                count += self._count_nodes(child)
        return count
        
    def test_visualization_error_handling(self):
        """Test error handling in visualization system"""
        # Test with invalid JSON
        invalid_json = "{ invalid json content"
        with open(self.data_file, 'w') as f:
            f.write(invalid_json)
            
        synchronizer = DataSynchronizer(self.temp_dir)
        sync_result = synchronizer.sync_to_frontend()
        
        # Should fail gracefully
        self.assertFalse(sync_result)
        
        # Test with missing data file
        if self.data_file.exists():
            self.data_file.unlink()
            
        sync_result = synchronizer.sync_to_frontend()
        self.assertFalse(sync_result)
        
        # Test with empty data
        empty_data = {}
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f)
            
        sync_result = synchronizer.sync_to_frontend()
        self.assertTrue(sync_result)  # Should sync empty data successfully
        
        # Verify empty data was synced
        with open(self.frontend_data_file, 'r', encoding='utf-8') as f:
            synced_data = json.load(f)
            
        self.assertEqual(synced_data, empty_data)


if __name__ == '__main__':
    unittest.main()
