# Test Websites Collection for Web Scraper

This directory contains a comprehensive collection of interconnected test websites designed to thoroughly test the hierarchical web scraper system. These sites provide a controlled environment for testing various scraping scenarios without relying on external websites.

## 🌐 Website Collection Overview

### 1. **TechNews Central** (`index.html`)
- **Theme**: Technology news and reviews website
- **Structure**: Homepage with navigation to reviews, news, tutorials, industry coverage
- **Links**: 25+ internal links, 8+ external links to other test sites
- **Features**: Article listings, sidebar navigation, category pages, related content links

### 2. **InnovateTech Solutions** (`corporate-site/`)
- **Theme**: Corporate technology consulting company
- **Structure**: Professional business website with services, solutions, team info
- **Links**: 30+ internal links, 10+ external links to other test sites
- **Features**: Service descriptions, industry solutions, team profiles, case studies

### 3. **TechThoughts Blog** (`blog-site/`)
- **Theme**: Personal technology blog with programming insights
- **Structure**: Blog-style layout with posts, categories, tags, archives
- **Links**: 20+ internal links, 12+ external links to other test sites
- **Features**: Blog posts, tag cloud, category navigation, author profiles

### 4. **DevDocs Hub** (`documentation-site/`)
- **Theme**: Developer documentation and API reference site
- **Structure**: Documentation-style layout with sidebar navigation
- **Links**: 35+ internal links, 8+ external links to other test sites
- **Features**: API documentation, code examples, tutorials, reference guides

### 5. **Global News Today** (`news-site/`)
- **Theme**: General news website with multiple categories
- **Structure**: News portal with breaking news, categories, live updates
- **Links**: 40+ internal links, 15+ external links to other test sites
- **Features**: Breaking news banner, category sections, trending stories, live updates

### 6. **Alex Chen Portfolio** (`portfolio-site/`)
- **Theme**: Personal portfolio website for a full-stack developer
- **Structure**: Portfolio layout with projects, skills, experience, contact
- **Links**: 25+ internal links, 10+ external links to other test sites
- **Features**: Project showcases, skill categories, professional experience, testimonials

## 🔗 Link Structure & Interconnections

### Internal Link Patterns
- **Homepage to Category**: Each site has 5-8 main category pages
- **Category to Detail**: Each category contains 3-6 detailed sub-pages
- **Cross-References**: Related content links within same site
- **Hierarchical Depth**: Up to 4 levels deep for comprehensive testing

### External Link Patterns
- **Cross-Site Navigation**: Each site links to 3-5 other test sites
- **Contextual Links**: Related content links between different sites
- **Circular References**: Sites link back to each other creating network effect
- **Thematic Connections**: Technology-related sites link to each other appropriately

## 📊 Testing Scenarios Covered

### 1. **Hierarchical Crawling**
- Multiple depth levels (1-4 levels deep)
- Parent-child page relationships
- Category and subcategory structures
- Breadcrumb navigation testing

### 2. **Link Type Variety**
- Standard HTML anchor links (`<a href="">`)
- Relative URLs (`./page.html`, `../other-site/page.html`)
- Absolute localhost URLs for cross-site testing
- Navigation menus and sidebar links
- Footer links and sitemaps

### 3. **Content Categorization**
- Different website themes and purposes
- Varied content structures and layouts
- Multiple navigation patterns
- Different HTML structures and CSS frameworks

### 4. **Edge Cases**
- Circular link references
- Deep nested directory structures
- Cross-site linking patterns
- Mixed internal/external link scenarios

## 🚀 Usage Instructions

### Starting the Test Environment

1. **Start Local Web Server**:
   ```bash
   cd live-graph-system/test-websites
   python -m http.server 8002
   ```

2. **Access Test Sites**:
   - Main Tech News: `http://localhost:8002/index.html`
   - Corporate Site: `http://localhost:8002/corporate-site/index.html`
   - Blog Site: `http://localhost:8002/blog-site/index.html`
   - Documentation: `http://localhost:8002/documentation-site/index.html`
   - News Site: `http://localhost:8002/news-site/index.html`
   - Portfolio: `http://localhost:8002/portfolio-site/index.html`

### Testing with Web Scraper

1. **Basic Scraping Test**:
   ```bash
   python scraper_cli.py --url http://localhost:8002/index.html --depth 3
   ```

2. **Deep Hierarchical Test**:
   ```bash
   python scraper_cli.py --url http://localhost:8002/corporate-site/index.html --depth 4
   ```

3. **Cross-Site Network Test**:
   ```bash
   python scraper_cli.py --url http://localhost:8002/index.html --depth 2 --follow-external
   ```

4. **Web Interface Testing**:
   - Start web scraper interface: `python scraper_web_interface.py`
   - Use test URLs in the web interface for controlled testing

## 📈 Expected Scraping Results

### Link Count Expectations
- **Total Unique Pages**: ~150+ pages across all sites
- **Internal Links per Site**: 15-40 links depending on site complexity
- **External Cross-Site Links**: 8-15 links per site
- **Maximum Depth**: 4 levels for comprehensive hierarchical testing

### Graph Visualization Results
- **Node Count**: 50-150 nodes depending on depth and scope
- **Hierarchical Structure**: Clear parent-child relationships
- **Cross-Site Connections**: Visible network connections between different sites
- **Category Clustering**: Related pages should cluster together

## 🛠 Customization Options

### Adding New Test Pages
1. Create new HTML files following the existing structure patterns
2. Add appropriate internal and external links
3. Update navigation menus in related pages
4. Test with web scraper to verify link discovery

### Modifying Link Structures
1. Edit existing HTML files to add/remove links
2. Ensure bidirectional linking where appropriate
3. Maintain realistic website navigation patterns
4. Test changes with scraper to verify functionality

### Creating New Test Sites
1. Create new directory for the site theme
2. Build interconnected pages with 15-25 links each
3. Add cross-references to existing test sites
4. Update this README with new site information

## 🎯 Testing Objectives

This test website collection is designed to validate:

- ✅ **Hierarchical Crawling**: Multi-level page discovery and mapping
- ✅ **Link Following**: Proper extraction and following of various link types
- ✅ **Cross-Site Navigation**: Handling of external links between test sites
- ✅ **Data Structure Generation**: Creation of proper JSON data for D3.js visualization
- ✅ **Error Handling**: Graceful handling of broken links and edge cases
- ✅ **Performance**: Efficient crawling of interconnected site networks
- ✅ **Visualization**: Generation of meaningful graph structures for display

## 📝 Notes

- All links use relative or localhost URLs for local testing
- Sites are designed to be realistic while remaining simple to maintain
- Content is generic but follows real-world website patterns
- HTML structure is clean and follows web standards
- CSS styling is minimal but functional for realistic appearance

---

**Ready to test!** Start your local web server and begin scraping these interconnected test websites to validate your web scraper's hierarchical crawling capabilities.
