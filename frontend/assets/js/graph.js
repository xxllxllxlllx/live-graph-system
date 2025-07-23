/**
 * Live Graph Visualization System
 *
 * Built with D3.js v3 by Mike Bostock (https://d3js.org/)
 * Inspired by OSINT Framework tree visualization (https://github.com/lockfale/OSINT-Framework)
 *
 * Features:
 * - Interactive hierarchical tree visualization
 * - Real-time data updates from web scraper
 * - Smooth animations and transitions
 * - Responsive design for multiple screen sizes
 */

// Graph dimensions and settings - responsive
var margin = [20, 60, 20, 60],
    width = Math.max(800, window.innerWidth - margin[1] - margin[3]),
    height = Math.max(600, window.innerHeight - margin[0] - margin[2]),
    i = 0,
    duration = 750,
    root;

// Create the tree layout
var tree = d3.layout.tree()
    .size([height, width]);

// Create the diagonal projection for links
var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

// Create the SVG container with proper zoom setup
var svgContainer = d3.select("#graph-container").append("svg:svg")
    .attr("width", width + margin[1] + margin[3])
    .attr("height", height + margin[0] + margin[2]);

var svg = svgContainer.append("svg:g")
    .attr("transform", "translate(" + margin[3] + "," + margin[0] + ")");

// Global variables for live data system
window.root = null;
window.update = update;
let lastDataHash = null;

// Function to collapse nodes
function collapse(d) {
  if (d.children) {
    d._children = d.children;
    d._children.forEach(collapse);
    d.children = null;
  }
}

// Initialize the graph with data
function initializeGraph(json) {
  root = json;
  window.root = root; // Make root globally accessible
  root.x0 = height / 2;
  root.y0 = 0;

  // Initially collapse all children except the first level
  if (root.children) {
    root.children.forEach(function(d) {
      if (d.children) {
        d.children.forEach(collapse);
      }
    });
  }

  update(root);
}

// Load data with error handling and hash checking
function loadData() {
  d3.json("data/data.json", function(error, json) {
    if (error) {
      console.error("Error loading data:", error);
      console.log("Attempting to load from alternative path...");
      // Fallback to try the original path
      d3.json("../data/data.json", function(error2, json2) {
        if (error2) {
          console.error("Error loading data from fallback path:", error2);
          showErrorMessage("Failed to load data.json. Please ensure the data file exists.");
          return;
        }
        processLoadedData(json2);
      });
      return;
    }
    processLoadedData(json);
  });
}

function processLoadedData(json) {

    // Calculate simple hash of the data to detect changes
    const dataString = JSON.stringify(json);
    const currentHash = dataString.length + dataString.charCodeAt(0) + dataString.charCodeAt(dataString.length - 1);

    // Only update if data has changed
    if (currentHash !== lastDataHash) {
      lastDataHash = currentHash;
      console.log("Data updated, refreshing graph...");

      if (!root) {
        // First load
        initializeGraph(json);
      } else {
        // Update existing graph
        root = json;
        window.root = root;
        root.x0 = height / 2;
        root.y0 = 0;
        update(root);
      }
    }
}

// Show error message to user
function showErrorMessage(message) {
  console.error(message);
  // Create error display in the graph area
  d3.select("#graph").selectAll("*").remove();
  d3.select("#graph")
    .append("div")
    .style("text-align", "center")
    .style("padding", "50px")
    .style("color", "#ff4444")
    .style("font-size", "18px")
    .html("⚠️ " + message + "<br><br>Please check the console for more details.");
}

// Start real-time data polling
function startDataPolling() {
  // Initial load
  loadData();

  // Poll for changes every 1 second
  setInterval(loadData, 1000);
}

// Start the system
startDataPolling();

// Main update function with enhanced animations
function update(source) {
  // Compute the new tree layout
  var nodes = tree.nodes(root).reverse();

  // Normalize for fixed-depth - adjustable spacing
  var depthSpacing = 180; // Pixels between depth levels (was 200)
  nodes.forEach(function(d) { d.y = d.depth * depthSpacing; });

  // Update the nodes
  var node = svg.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter any new nodes at the parent's previous position with enhanced animation
  var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) {
        // Use source position for smooth entrance
        var sourceX = source ? source.x0 : height / 2;
        var sourceY = source ? source.y0 : 0;
        return "translate(" + sourceY + "," + sourceX + ")";
      })
      .style("opacity", 0) // Start invisible for fade-in effect
      .on("click", function(d) { toggle(d); update(d); });

  // Add circles for nodes - matching original OSINT Framework style
  nodeEnter.append("svg:circle")
      .attr("r", 1e-6)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; })
      .style("stroke", "steelblue")
      .style("stroke-width", "1.5px");

  // Add text labels - matching original OSINT Framework style
  nodeEnter.append("svg:text")
      .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .text(function(d) { return d.name; })
      .style("fill", "rgb(0, 0, 0)")
      .style("font-size", "12px")
      .style("fill-opacity", 1e-6);

  // Add tooltips
  nodeEnter.append("svg:title")
    .text(function(d) {
      return d.description || d.name;
    });

  // Transition nodes to their new position with enhanced animations
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
      .style("opacity", 1); // Fade in new nodes

  nodeUpdate.select("circle")
      .attr("r", 6)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

  nodeUpdate.select("text")
      .style("fill-opacity", 1);

  // Transition exiting nodes to the parent's new position
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();

  nodeExit.select("circle")
      .attr("r", 1e-6);

  nodeExit.select("text")
      .style("fill-opacity", 1e-6);

  // Update the links
  var link = svg.selectAll("path.link")
      .data(tree.links(nodes), function(d) { return d.target.id; });

  // Enter any new links at the parent's previous position
  link.enter().insert("svg:path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
    .transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition links to their new position
  link.transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition exiting nodes to the parent's new position
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

  // Stash the old positions for transition
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });

  // Enhance node interactions after update
  enhanceNodeInteraction();
}

// Toggle children on click
function toggle(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
}

// Handle window resize for responsiveness
function handleResize() {
  var newWidth = Math.max(800, window.innerWidth - margin[1] - margin[3]);
  var newHeight = Math.max(600, window.innerHeight - margin[0] - margin[2]);

  if (newWidth !== width || newHeight !== height) {
    width = newWidth;
    height = newHeight;

    tree.size([height, width]);

    svg.select("svg")
      .attr("width", width + margin[1] + margin[3])
      .attr("height", height + margin[0] + margin[2]);

    if (root) {
      update(root);
    }
  }
}

// Add resize event listener
window.addEventListener('resize', handleResize);

// Enhanced iframe interaction support
function resetView() {
  if (root) {
    // Reset all nodes to collapsed state except root
    function collapseAll(d) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
        d._children.forEach(collapseAll);
      }
    }

    if (root.children) {
      root.children.forEach(collapseAll);
    }

    // Reset zoom and pan
    svg.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity);

    // Update the visualization
    update(root);
  }
}

// Message handling for iframe communication
window.addEventListener('message', function(event) {
  if (event.data && event.data.action) {
    switch (event.data.action) {
      case 'reset':
        resetView();
        break;
      case 'refresh':
        loadData();
        break;
    }
  }
});

// Enhanced zoom and pan behavior
var zoom = d3.behavior.zoom()
  .scaleExtent([0.1, 3])
  .on("zoom", function() {
    svg.attr("transform",
      "translate(" + d3.event.translate + ")" +
      " scale(" + d3.event.scale + ")" +
      " translate(" + margin[3] + "," + margin[0] + ")");
  });

// Apply zoom behavior to the outer SVG container
svgContainer.call(zoom);

// Add visual feedback for better interaction
svgContainer.style("cursor", "grab");

// Improve node interaction with proper hover behavior
function enhanceNodeInteraction() {
  svg.selectAll("g.node")
    .style("cursor", "pointer")
    .on("mouseover", function(d) {
      d3.select(this).select("circle")
        .transition()
        .duration(200)
        .attr("r", function(d) {
          // Expand on hover: default 6 -> 7.5, collapsed nodes 6 -> 7
          return d._children ? 7 : 7.5;
        })
        .style("stroke-width", "2.5px");
    })
    .on("mouseout", function(d) {
      d3.select(this).select("circle")
        .transition()
        .duration(200)
        .attr("r", 6) // Return to default size for all nodes
        .style("stroke-width", "1.5px");
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
  switch(event.key) {
    case 'r':
    case 'R':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault();
        loadData();
      }
      break;
    case 'Escape':
      resetView();
      break;
  }
});

// Add touch support for mobile devices
if ('ontouchstart' in window) {
  svgContainer.style("cursor", "default");
}
