const fs = require('fs');
const path = require('path');

class LiveDataGenerator {
  constructor() {
    this.dataPath = path.join(__dirname, 'data.json');
    this.isRunning = false;
    this.cycleCount = 0;
    this.maxCycles = 5;
    this.delayBetweenCycles = 3000; // 3 seconds
    
    // Predefined data pools for realistic content generation
    this.contentPools = {
      technology: {
        categories: ['Blockchain Technology', 'Internet of Things', 'Robotics', 'Virtual Reality', 'Augmented Reality'],
        subcategories: ['Smart Contracts', 'Sensor Networks', 'Autonomous Systems', 'Immersive Experiences', 'Mixed Reality'],
        items: ['Cryptocurrency Wallets', 'Environmental Monitoring', 'Drone Navigation', 'VR Gaming', 'AR Shopping']
      },
      science: {
        categories: ['Astronomy', 'Neuroscience', 'Environmental Science', 'Materials Science', 'Biotechnology'],
        subcategories: ['Exoplanet Research', 'Brain Imaging', 'Climate Modeling', 'Nanotechnology', 'Gene Therapy'],
        items: ['Telescope Arrays', 'fMRI Scanning', 'Carbon Footprint', 'Graphene Applications', 'CRISPR Technology']
      },
      arts: {
        categories: ['Digital Media', 'Contemporary Art', 'Film Production', 'Interactive Design', 'Sound Art'],
        subcategories: ['Motion Graphics', 'Installation Art', 'Documentary Film', 'User Experience', 'Ambient Music'],
        items: ['3D Animation', 'Light Sculptures', 'Cinematography', 'Interface Design', 'Soundscapes']
      },
      business: {
        categories: ['E-commerce', 'Supply Chain', 'Data Analytics', 'Customer Relations', 'Sustainability'],
        subcategories: ['Online Marketplaces', 'Logistics Management', 'Business Intelligence', 'CRM Systems', 'Green Technology'],
        items: ['Payment Processing', 'Inventory Tracking', 'Predictive Analytics', 'Customer Support', 'Renewable Energy']
      }
    };
  }

  // Load current data from JSON file
  loadData() {
    try {
      const data = fs.readFileSync(this.dataPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('Error loading data:', error);
      return null;
    }
  }

  // Save data to JSON file
  saveData(data) {
    try {
      fs.writeFileSync(this.dataPath, JSON.stringify(data, null, 2));
      console.log('Data saved successfully');
      return true;
    } catch (error) {
      console.error('Error saving data:', error);
      return false;
    }
  }

  // Generate random content based on node type and theme
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

  // Add new nodes to random locations
  addRandomNodes(data) {
    const locations = this.findAddableLocations(data);
    const validLocations = locations.filter(loc => loc.canAddType !== null);
    
    if (validLocations.length === 0) {
      console.log('No valid locations to add nodes');
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
      console.log(`Added new ${location.canAddType}: ${content.name} to ${location.node.name}`);
      
      // Remove this location to avoid duplicates
      validLocations.splice(randomIndex, 1);
    }

    return nodesAdded > 0;
  }

  // Run a single generation cycle
  async runCycle() {
    console.log(`\n--- Cycle ${this.cycleCount + 1}/${this.maxCycles} ---`);
    
    const data = this.loadData();
    if (!data) {
      console.error('Failed to load data');
      return false;
    }

    const success = this.addRandomNodes(data);
    if (success) {
      this.saveData(data);
      this.cycleCount++;
      return true;
    }
    
    return false;
  }

  // Start the live generation process
  async start() {
    if (this.isRunning) {
      console.log('Generator is already running');
      return;
    }

    console.log('Starting live data generation...');
    this.isRunning = true;
    this.cycleCount = 0;

    while (this.isRunning && this.cycleCount < this.maxCycles) {
      await this.runCycle();
      
      if (this.cycleCount < this.maxCycles) {
        console.log(`Waiting ${this.delayBetweenCycles/1000} seconds before next cycle...`);
        await new Promise(resolve => setTimeout(resolve, this.delayBetweenCycles));
      }
    }

    this.stop();
  }

  // Stop the generation process
  stop() {
    console.log('\nLive data generation completed!');
    console.log(`Total cycles completed: ${this.cycleCount}`);
    this.isRunning = false;
  }

  // Get current status
  getStatus() {
    return {
      isRunning: this.isRunning,
      cycleCount: this.cycleCount,
      maxCycles: this.maxCycles,
      delayBetweenCycles: this.delayBetweenCycles
    };
  }
}

// Export for use as module or run directly
if (require.main === module) {
  const generator = new LiveDataGenerator();
  
  // Handle command line arguments
  const args = process.argv.slice(2);
  if (args.includes('--start')) {
    generator.start();
  } else {
    console.log('Live Data Generator');
    console.log('Usage: node data-generator.js --start');
    console.log('Or use as a module: const generator = new LiveDataGenerator();');
  }
}

module.exports = LiveDataGenerator;
