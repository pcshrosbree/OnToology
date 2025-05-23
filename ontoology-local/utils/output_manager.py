"""
Output management utilities for generating the final documentation structure.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, Template


class OutputManager:
    """Manages the output directory and generates the final documentation."""
    
    def __init__(self, output_dir: str):
        """
        Initialize the output manager.
        
        Args:
            output_dir: Directory where all outputs will be generated
        """
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / 'assets'
        
    def setup_output_directory(self):
        """Create and setup the output directory structure."""
        # Create main output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create assets directory
        self.assets_dir.mkdir(exist_ok=True)
        
        # Copy static assets
        self._copy_static_assets()
        
    def _copy_static_assets(self):
        """Copy CSS, JS, and other static assets to the output directory."""
        # Create CSS directory and add basic styles
        css_dir = self.assets_dir / 'css'
        css_dir.mkdir(exist_ok=True)
        
        # Generate basic CSS
        css_content = self._generate_base_css()
        with open(css_dir / 'style.css', 'w') as f:
            f.write(css_content)
        
        # Create JS directory
        js_dir = self.assets_dir / 'js'
        js_dir.mkdir(exist_ok=True)
        
        # Generate basic JavaScript
        js_content = self._generate_base_js()
        with open(js_dir / 'script.js', 'w') as f:
            f.write(js_content)
    
    def _generate_base_css(self) -> str:
        """Generate basic CSS for the documentation."""
        return """
/* OnToology Local Documentation Styles */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f8f9fa;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 2.5rem;
}

.header p {
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
}

.ontology-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.ontology-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.ontology-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.ontology-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #2c3e50;
}

.ontology-description {
    color: #666;
    margin-bottom: 1rem;
    font-size: 0.95rem;
}

.ontology-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.stat-badge {
    background: #e9ecef;
    padding: 0.25rem 0.5rem;
    border-radius: 15px;
    font-size: 0.8rem;
    color: #495057;
}

.output-links {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.output-link {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    font-size: 0.9rem;
    transition: background-color 0.2s;
}

.output-link:hover {
    background: #0056b3;
    color: white;
    text-decoration: none;
}

.output-link.documentation { background: #28a745; }
.output-link.evaluation { background: #ffc107; color: #212529; }
.output-link.diagrams { background: #17a2b8; }
.output-link.jsonld { background: #6f42c1; }
.output-link.validation { background: #dc3545; }

.summary-stats {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    text-align: center;
}

.stat-item {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
    color: #007bff;
    display: block;
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
}

.footer {
    text-align: center;
    padding: 2rem;
    color: #666;
    border-top: 1px solid #dee2e6;
    margin-top: 2rem;
}

/* Documentation page styles */
.doc-header {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.doc-content {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section {
    margin-bottom: 2rem;
}

.section h2 {
    color: #2c3e50;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.entity-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
}

.entity-table th,
.entity-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
}

.entity-table th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.entity-table tr:hover {
    background-color: #f8f9fa;
}

.uri-link {
    color: #007bff;
    text-decoration: none;
    font-family: monospace;
    font-size: 0.9rem;
}

.uri-link:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .ontology-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .output-links {
        flex-direction: column;
    }
}
"""
    
    def _generate_base_js(self) -> str:
        """Generate basic JavaScript for the documentation."""
        return """
// OnToology Local Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add copy functionality to URI links
    document.querySelectorAll('.uri-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (e.ctrlKey || e.metaKey) {
                e.preventDefault();
                navigator.clipboard.writeText(this.textContent).then(() => {
                    // Show temporary feedback
                    const original = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = original;
                    }, 1000);
                });
            }
        });
    });
    
    // Add search functionality if search box exists
    const searchBox = document.getElementById('search');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const cards = document.querySelectorAll('.ontology-card');
            
            cards.forEach(card => {
                const title = card.querySelector('.ontology-title').textContent.toLowerCase();
                const description = card.querySelector('.ontology-description').textContent.toLowerCase();
                
                if (title.includes(query) || description.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
});
"""
    
    def generate_index(self, results: List[Dict[str, Any]]):
        """Generate the main index.html file."""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OnToology Local Documentation</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="header">
        <h1>OnToology Local Documentation</h1>
        <p>Generated documentation for {{ results|length }} ontologies</p>
    </div>
    
    {% if results %}
    <div class="summary-stats">
        <h2>Summary Statistics</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-number">{{ results|length }}</span>
                <span class="stat-label">Ontologies</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ total_classes }}</span>
                <span class="stat-label">Total Classes</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ total_properties }}</span>
                <span class="stat-label">Total Properties</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ total_individuals }}</span>
                <span class="stat-label">Total Individuals</span>
            </div>
        </div>
    </div>
    
    <div class="ontology-grid">
        {% for result in results %}
        <div class="ontology-card">
            <div class="ontology-title">{{ result.title }}</div>
            {% if result.description %}
            <div class="ontology-description">{{ result.description }}</div>
            {% endif %}
            
            <div class="ontology-stats">
                {% if result.outputs.documentation and not result.outputs.documentation.error %}
                <span class="stat-badge">Documentation Available</span>
                {% endif %}
                {% if result.outputs.evaluation and not result.outputs.evaluation.error %}
                <span class="stat-badge">Evaluation Complete</span>
                {% endif %}
                {% if result.outputs.diagrams and not result.outputs.diagrams.error %}
                <span class="stat-badge">Diagrams Generated</span>
                {% endif %}
            </div>
            
            <div class="output-links">
                {% if result.outputs.documentation and not result.outputs.documentation.error %}
                <a href="{{ result.base_name }}_documentation.html" class="output-link documentation">Documentation</a>
                {% endif %}
                {% if result.outputs.evaluation and not result.outputs.evaluation.error %}
                <a href="{{ result.base_name }}_evaluation.html" class="output-link evaluation">Evaluation</a>
                {% endif %}
                {% if result.outputs.diagrams and not result.outputs.diagrams.error %}
                <a href="{{ result.base_name }}_diagram.png" class="output-link diagrams">Diagram</a>
                {% endif %}
                {% if result.outputs.jsonld and not result.outputs.jsonld.error %}
                <a href="{{ result.base_name }}_context.jsonld" class="output-link jsonld">JSON-LD</a>
                {% endif %}
                {% if result.outputs.validation and not result.outputs.validation.error %}
                <a href="{{ result.base_name }}_validation.html" class="output-link validation">Validation</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <div class="ontology-card">
        <div class="ontology-title">No ontologies processed</div>
        <div class="ontology-description">No ontology files were found or successfully processed.</div>
    </div>
    {% endif %}
    
    <div class="footer">
        <p>Generated by OnToology Local</p>
    </div>
    
    <script src="assets/js/script.js"></script>
</body>
</html>
"""
        
        # Calculate summary statistics
        total_classes = 0
        total_properties = 0
        total_individuals = 0
        
        for result in results:
            if 'outputs' in result and 'documentation' in result['outputs']:
                doc_output = result['outputs']['documentation']
                if isinstance(doc_output, dict) and 'statistics' in doc_output:
                    stats = doc_output['statistics']
                    total_classes += stats.get('classes', 0)
                    total_properties += (stats.get('object_properties', 0) + 
                                       stats.get('datatype_properties', 0) + 
                                       stats.get('annotation_properties', 0))
                    total_individuals += stats.get('individuals', 0)
        
        # Render template
        template = Template(template_content)
        html_content = template.render(
            results=results,
            total_classes=total_classes,
            total_properties=total_properties,
            total_individuals=total_individuals
        )
        
        # Write index file
        index_path = self.output_dir / 'index.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def get_output_path(self, filename: str) -> Path:
        """Get the full path for an output file."""
        return self.output_dir / filename
