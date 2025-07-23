// Web-based Live Data Generator Control System
class WebDataGenerator {
  constructor() {
    this.isRunning = false;
    this.cycleCount = 0;
    this.maxCycles = 5;
    this.delayBetweenCycles = 3000; // 3 seconds
    this.currentTimeout = null;
    
    // Content pools for realistic data generation
    this.contentPools = {
      technology: {
        categories: ['Blockchain Technology', 'Internet of Things', 'Robotics', 'Virtual Reality', 'Augmented Reality', 'Machine Learning', 'Edge Computing'],
        subcategories: ['Smart Contracts', 'Sensor Networks', 'Autonomous Systems', 'Immersive Experiences', 'Mixed Reality', 'Deep Learning', 'Distributed Computing'],
        items: ['Cryptocurrency Wallets', 'Environmental Monitoring', 'Drone Navigation', 'VR Gaming', 'AR Shopping', 'Neural Networks', 'Microservices']
      },
      science: {
        categories: ['Astronomy', 'Neuroscience', 'Environmental Science', 'Materials Science', 'Biotechnology', 'Quantum Physics', 'Marine Biology'],
        subcategories: ['Exoplanet Research', 'Brain Imaging', 'Climate Modeling', 'Nanotechnology', 'Gene Therapy', 'Quantum Computing', 'Ocean Ecosystems'],
        items: ['Telescope Arrays', 'fMRI Scanning', 'Carbon Footprint', 'Graphene Applications', 'CRISPR Technology', 'Quantum Algorithms', 'Coral Reefs']
      },
      arts: {
        categories: ['Digital Media', 'Contemporary Art', 'Film Production', 'Interactive Design', 'Sound Art', 'Performance Art', 'Street Art'],
        subcategories: ['Motion Graphics', 'Installation Art', 'Documentary Film', 'User Experience', 'Ambient Music', 'Live Performance', 'Murals'],
        items: ['3D Animation', 'Light Sculptures', 'Cinematography', 'Interface Design', 'Soundscapes', 'Theater', 'Graffiti']
      },
      business: {
        categories: ['E-commerce', 'Supply Chain', 'Data Analytics', 'Customer Relations', 'Sustainability', 'Digital Transformation', 'Innovation Management'],
        subcategories: ['Online Marketplaces', 'Logistics Management', 'Business Intelligence', 'CRM Systems', 'Green Technology', 'Cloud Migration', 'R&D Strategy'],
        items: ['Payment Processing', 'Inventory Tracking', 'Predictive Analytics', 'Customer Support', 'Renewable Energy', 'API Integration', 'Patent Portfolio']
      }
    };

    this.initializeUI();
  }

  // Initialize the control UI
  initializeUI() {
    this.createControlPanel();
    this.updateStatus();
  }

  // Create control panel HTML
  createControlPanel() {
    const controlPanel = document.createElement('div');
    controlPanel.id = 'generator-control-panel';
    controlPanel.innerHTML = `
      <div style="position: fixed; top: 20px; right: 20px; background: white; padding: 20px; border: 2px solid #333; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); z-index: 1000; font-family: Arial, sans-serif;">
        <h3 style="margin: 0 0 15px 0; color: #333;">Live Data Generator</h3>
        
        <div style="margin-bottom: 15px;">
          <div><strong>Status:</strong> <span id="generator-status">Stopped</span></div>
          <div><strong>Cycle:</strong> <span id="cycle-count">0</span>/<span id="max-cycles">5</span></div>
          <div><strong>Delay:</strong> <span id="cycle-delay">3</span>s</div>
        </div>
        
        <div style="margin-bottom: 15px;">
          <label for="cycles-input" style="display: block; margin-bottom: 5px;">Max Cycles:</label>
          <input type="number" id="cycles-input" value="5" min="1" max="20" style="width: 60px; padding: 4px;">
          
          <label for="delay-input" style="display: block; margin-top: 10px; margin-bottom: 5px;">Delay (seconds):</label>
          <input type="number" id="delay-input" value="3" min="1" max="10" style="width: 60px; padding: 4px;">
        </div>
        
        <div>
          <button id="start-btn" style="background: #4CAF50; color: white; border: none; padding: 8px 16px; margin-right: 8px; border-radius: 4px; cursor: pointer;">Start</button>
          <button id="stop-btn" style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;" disabled>Stop</button>
        </div>
        
        <div id="generation-log" style="margin-top: 15px; max-height: 200px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 12px; font-family: monospace;">
          <div>Ready to start generation...</div>
        </div>
      </div>
    `;
    
    document.body.appendChild(controlPanel);
    
    // Add event listeners
    document.getElementById('start-btn').addEventListener('click', () => this.start());
    document.getElementById('stop-btn').addEventListener('click', () => this.stop());
    document.getElementById('cycles-input').addEventListener('change', (e) => {
      this.maxCycles = parseInt(e.target.value);
      this.updateStatus();
    });
    document.getElementById('delay-input').addEventListener('change', (e) => {
      this.delayBetweenCycles = parseInt(e.target.value) * 1000;
      this.updateStatus();
    });
  }

  // Update status display
  updateStatus() {
    document.getElementById('generator-status').textContent = this.isRunning ? 'Running' : 'Stopped';
    document.getElementById('cycle-count').textContent = this.cycleCount;
    document.getElementById('max-cycles').textContent = this.maxCycles;
    document.getElementById('cycle-delay').textContent = this.delayBetweenCycles / 1000;
    
    document.getElementById('start-btn').disabled = this.isRunning;
    document.getElementById('stop-btn').disabled = !this.isRunning;
  }

  // Log messages to the control panel
  log(message) {
    const logDiv = document.getElementById('generation-log');
    if (logDiv) {
      const timestamp = new Date().toLocaleTimeString();
      const logEntry = document.createElement('div');
      logEntry.textContent = `[${timestamp}] ${message}`;
      logDiv.appendChild(logEntry);
      logDiv.scrollTop = logDiv.scrollHeight;
    }

    // Send message to parent controller if in iframe
    if (window.parent !== window) {
      window.parent.postMessage({
        type: 'generationUpdate',
        cycleCount: this.cycleCount,
        message: message
      }, '*');
    }

    console.log(message);
  }

  // Generate random content based on theme and node type
  generateRandomContent(theme, nodeType) {
    const pool = this.contentPools[theme];
    if (!pool) return { name: 'Unknown', description: 'Generated content' };

    let name, description;
    
    switch (nodeType) {
      case 'category':
        name = pool.categories[Math.floor(Math.random() * pool.categories.length)];
        description = `${name} category with various specialized areas`;
        break;
      case 'subcategory':
        name = pool.subcategories[Math.floor(Math.random() * pool.subcategories.length)];
        description = `Specialized area focusing on ${name.toLowerCase()}`;
        break;
      case 'item':
        name = pool.items[Math.floor(Math.random() * pool.items.length)];
        description = `Specific implementation of ${name.toLowerCase()}`;
        break;
      default:
        name = 'Generated Node';
        description = 'Dynamically generated content';
    }

    return { name, description };
  }

  // Find all possible locations where new nodes can be added
  findAddableLocations(node, theme = null, path = []) {
    const locations = [];
    
    // Determine theme from branch name if not provided
    if (!theme && node.name) {
      if (node.name.includes('Technology')) theme = 'technology';
      else if (node.name.includes('Science')) theme = 'science';
      else if (node.name.includes('Arts')) theme = 'arts';
      else if (node.name.includes('Business')) theme = 'business';
    }

    // Add current node as a potential location if it can have children
    if (node.type !== 'item') {
      locations.push({
        node: node,
        path: [...path],
        theme: theme,
        canAddType: this.getNextNodeType(node.type)
      });
    }

    // Recursively check children
    if (node.children) {
      node.children.forEach((child, index) => {
        const childLocations = this.findAddableLocations(child, theme, [...path, index]);
        locations.push(...childLocations);
      });
    }

    return locations;
  }

  // Determine what type of node can be added to a parent
  getNextNodeType(parentType) {
    switch (parentType) {
      case 'root': return 'category';
      case 'category': return 'subcategory';
      case 'subcategory': return 'item';
      default: return null;
    }
  }

  // Add new nodes to random locations in the current data
  addRandomNodes(data) {
    const locations = this.findAddableLocations(data);
    const validLocations = locations.filter(loc => loc.canAddType !== null);
    
    if (validLocations.length === 0) {
      this.log('No valid locations to add nodes');
      return false;
    }

    // Add 1-3 new nodes randomly
    const nodesToAdd = Math.floor(Math.random() * 3) + 1;
    let nodesAdded = 0;

    for (let i = 0; i < nodesToAdd && validLocations.length > 0; i++) {
      const randomIndex = Math.floor(Math.random() * validLocations.length);
      const location = validLocations[randomIndex];
      
      // Generate new node content
      const content = this.generateRandomContent(location.theme, location.canAddType);
      const newNode = {
        name: content.name,
        type: location.canAddType,
        description: content.description
      };

      // Add children array if not an item
      if (location.canAddType !== 'item') {
        newNode.children = [];
      }

      // Add the new node to the selected location
      if (!location.node.children) {
        location.node.children = [];
      }
      location.node.children.push(newNode);
      
      nodesAdded++;
      this.log(`Added ${location.canAddType}: ${content.name} to ${location.node.name}`);
      
      // Remove this location to avoid duplicates
      validLocations.splice(randomIndex, 1);
    }

    return nodesAdded > 0;
  }

  // Run a single generation cycle
  async runCycle() {
    this.log(`--- Cycle ${this.cycleCount + 1}/${this.maxCycles} ---`);
    
    // Get current data from the global root variable (set by graph.js)
    if (!window.root) {
      this.log('Error: No graph data available');
      return false;
    }

    const success = this.addRandomNodes(window.root);
    if (success) {
      this.cycleCount++;
      // Trigger graph update
      if (window.update && typeof window.update === 'function') {
        window.update(window.root);
        this.log('Graph updated with new nodes');
      }
      return true;
    }
    
    return false;
  }

  // Start the live generation process
  async start() {
    if (this.isRunning) {
      this.log('Generator is already running');
      return;
    }

    this.log('Starting live data generation...');
    this.isRunning = true;
    this.cycleCount = 0;
    this.updateStatus();

    const runNextCycle = async () => {
      if (!this.isRunning || this.cycleCount >= this.maxCycles) {
        this.stop();
        return;
      }

      await this.runCycle();
      
      if (this.isRunning && this.cycleCount < this.maxCycles) {
        this.log(`Waiting ${this.delayBetweenCycles/1000} seconds before next cycle...`);
        this.currentTimeout = setTimeout(runNextCycle, this.delayBetweenCycles);
      } else {
        this.stop();
      }
    };

    runNextCycle();
  }

  // Stop the generation process
  stop() {
    if (this.currentTimeout) {
      clearTimeout(this.currentTimeout);
      this.currentTimeout = null;
    }

    this.log(`Live data generation completed! Total cycles: ${this.cycleCount}`);
    this.isRunning = false;
    this.updateStatus();

    // Notify parent controller if in iframe
    if (window.parent !== window) {
      window.parent.postMessage({
        type: 'generationComplete',
        cycleCount: this.cycleCount
      }, '*');
    }
  }
}

// Initialize the generator when the page loads
let webGenerator;
document.addEventListener('DOMContentLoaded', () => {
  webGenerator = new WebDataGenerator();

  // Listen for messages from parent controller
  window.addEventListener('message', (event) => {
    if (event.data.action === 'startGeneration') {
      webGenerator.maxCycles = event.data.maxCycles || 5;
      webGenerator.delayBetweenCycles = event.data.delay || 3000;
      webGenerator.generationMode = event.data.mode || 'random';
      webGenerator.start();
    } else if (event.data.action === 'stopGeneration') {
      webGenerator.stop();
    }
  });
});
