"""
Documentation processor - generates HTML documentation for ontologies.
"""

from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Template
import logging


class DocumentationProcessor:
    """Generates comprehensive HTML documentation for ontologies."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the documentation processor.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.languages = config.get('languages', ['en'])
        
    def process(self, ontology_data: Dict[str, Any], base_name: str, 
                output_dir: str) -> Dict[str, Any]:
        """
        Generate HTML documentation for an ontology.
        
        Args:
            ontology_data: Parsed ontology data
            base_name: Base filename for outputs
            output_dir: Output directory path
            
        Returns:
            Dictionary with output file information
        """
        try:
            output_file = f"{base_name}_documentation.html"
            output_path = Path(output_dir) / output_file
            
            # Generate HTML content
            html_content = self._generate_html(ontology_data)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Generated documentation: {output_file}")
            
            return {
                'file': output_file,
                'path': str(output_path),
                'statistics': ontology_data.get('statistics', {})
            }
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _generate_html(self, ontology_data: Dict[str, Any]) -> str:
        """Generate the complete HTML documentation."""
        
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Ontology Documentation</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .toc {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        .toc li {
            margin: 0.5rem 0;
        }
        .toc a {
            color: #007bff;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        .metadata-grid {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 0.5rem 1rem;
            margin-bottom: 1rem;
        }
        .metadata-label {
            font-weight: 600;
            color: #495057;
        }
        .namespace-table {
            font-family: monospace;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="doc-header">
        <h1>{{ title }}</h1>
        {% if description %}
        <p class="lead">{{ description }}</p>
        {% endif %}
        
        <div class="metadata-grid">
            {% if ontology_uri %}
            <span class="metadata-label">Ontology URI:</span>
            <span><a href="{{ ontology_uri }}" class="uri-link">{{ ontology_uri }}</a></span>
            {% endif %}
            
            {% if version %}
            <span class="metadata-label">Version:</span>
            <span>{{ version }}</span>
            {% endif %}
            
            {% if authors %}
            <span class="metadata-label">Authors:</span>
            <span>{{ authors | join(', ') }}</span>
            {% endif %}
            
            {% if license %}
            <span class="metadata-label">License:</span>
            <span><a href="{{ license }}" class="uri-link">{{ license }}</a></span>
            {% endif %}
        </div>
        
        {% if statistics %}
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-number">{{ statistics.classes }}</span>
                <span class="stat-label">Classes</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ statistics.object_properties }}</span>
                <span class="stat-label">Object Properties</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ statistics.datatype_properties }}</span>
                <span class="stat-label">Datatype Properties</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{{ statistics.individuals }}</span>
                <span class="stat-label">Individuals</span>
            </div>
        </div>
        {% endif %}
    </div>
    
    <div class="doc-content">
        <div class="toc">
            <h2>Table of Contents</h2>
            <ul>
                {% if classes %}
                <li><a href="#classes">Classes ({{ classes|length }})</a></li>
                {% endif %}
                {% if properties.object_properties %}
                <li><a href="#object-properties">Object Properties ({{ properties.object_properties|length }})</a></li>
                {% endif %}
                {% if properties.datatype_properties %}
                <li><a href="#datatype-properties">Datatype Properties ({{ properties.datatype_properties|length }})</a></li>
                {% endif %}
                {% if properties.annotation_properties %}
                <li><a href="#annotation-properties">Annotation Properties ({{ properties.annotation_properties|length }})</a></li>
                {% endif %}
                {% if individuals %}
                <li><a href="#individuals">Individuals ({{ individuals|length }})</a></li>
                {% endif %}
                {% if namespaces %}
                <li><a href="#namespaces">Namespaces</a></li>
                {% endif %}
            </ul>
        </div>
        
        {% if classes %}
        <div class="section" id="classes">
            <h2>Classes</h2>
            <table class="entity-table">
                <thead>
                    <tr>
                        <th>Class</th>
                        <th>Label</th>
                        <th>Description</th>
                        <th>Superclasses</th>
                    </tr>
                </thead>
                <tbody>
                    {% for class in classes %}
                    <tr>
                        <td><a href="{{ class.uri }}" class="uri-link">{{ class.uri.split('#')[-1] or class.uri.split('/')[-1] }}</a></td>
                        <td>{{ class.label }}</td>
                        <td>{{ class.comment }}</td>
                        <td>
                            {% for super in class.superclasses %}
                            <a href="{{ super }}" class="uri-link">{{ super.split('#')[-1] or super.split('/')[-1] }}</a>{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if properties.object_properties %}
        <div class="section" id="object-properties">
            <h2>Object Properties</h2>
            <table class="entity-table">
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Label</th>
                        <th>Description</th>
                        <th>Domain</th>
                        <th>Range</th>
                    </tr>
                </thead>
                <tbody>
                    {% for prop in properties.object_properties %}
                    <tr>
                        <td><a href="{{ prop.uri }}" class="uri-link">{{ prop.uri.split('#')[-1] or prop.uri.split('/')[-1] }}</a></td>
                        <td>{{ prop.label }}</td>
                        <td>{{ prop.comment }}</td>
                        <td>
                            {% for domain in prop.domain %}
                            <a href="{{ domain }}" class="uri-link">{{ domain.split('#')[-1] or domain.split('/')[-1] }}</a>{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </td>
                        <td>
                            {% for range in prop.range %}
                            <a href="{{ range }}" class="uri-link">{{ range.split('#')[-1] or range.split('/')[-1] }}</a>{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if properties.datatype_properties %}
        <div class="section" id="datatype-properties">
            <h2>Datatype Properties</h2>
            <table class="entity-table">
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Label</th>
                        <th>Description</th>
                        <th>Domain</th>
                        <th>Range</th>
                    </tr>
                </thead>
                <tbody>
                    {% for prop in properties.datatype_properties %}
                    <tr>
                        <td><a href="{{ prop.uri }}" class="uri-link">{{ prop.uri.split('#')[-1] or prop.uri.split('/')[-1] }}</a></td>
                        <td>{{ prop.label }}</td>
                        <td>{{ prop.comment }}</td>
                        <td>
                            {% for domain in prop.domain %}
                            <a href="{{ domain }}" class="uri-link">{{ domain.split('#')[-1] or domain.split('/')[-1] }}</a>{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </td>
                        <td>
                            {% for range in prop.range %}
                            <a href="{{ range }}" class="uri-link">{{ range.split('#')[-1] or range.split('/')[-1] }}</a>{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if properties.annotation_properties %}
        <div class="section" id="annotation-properties">
            <h2>Annotation Properties</h2>
            <table class="entity-table">
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Label</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {% for prop in properties.annotation_properties %}
                    <tr>
                        <td><a href="{{ prop.uri }}" class="uri-link">{{ prop.uri.split('#')[-1] or prop.uri.split('/')[-1] }}</a></td>
                        <td>{{ prop.label }}</td>
                        <td>{{ prop.comment }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if individuals %}
        <div class="section" id="individuals">
            <h2>Individuals</h2>
            <table class="entity-table">
                <thead>
                    <tr>
                        <th>Individual</th>
                        <th>Label</th>
                        <th>Description</th>
                        <th>Types</th>
                    </tr>
                </thead>
                <tbody>
                    {% for individual in individuals %}
                    <tr>
                        <td><a href="{{ individual.uri }}" class="uri-link">{{ individual.uri.split('#')[-1] or individual.uri.split('/')[-1] }}</a></td>
                        <td>{{ individual.label }}</td>
                        <td>{{ individual.comment }}</td>
                        <td>
                            {% for type in individual.types %}
                            <a href="{{ type }}" class="uri-link">{{ type.split('#')[-1] or type.split('/')[-1] }}</a>{% if not loop.last %}, {% endif %}
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if namespaces %}
        <div class="section" id="namespaces">
            <h2>Namespaces</h2>
            <table class="entity-table namespace-table">
                <thead>
                    <tr>
                        <th>Prefix</th>
                        <th>Namespace URI</th>
                    </tr>
                </thead>
                <tbody>
                    {% for prefix, namespace in namespaces.items() %}
                    <tr>
                        <td>{{ prefix }}</td>
                        <td><a href="{{ namespace }}" class="uri-link">{{ namespace }}</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if imports %}
        <div class="section" id="imports">
            <h2>Imported Ontologies</h2>
            <ul>
                {% for import in imports %}
                <li><a href="{{ import }}" class="uri-link">{{ import }}</a></li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    
    <div class="footer">
        <p>Generated by OnToology Local</p>
        <p><a href="index.html">← Back to Index</a></p>
    </div>
    
    <script src="assets/js/script.js"></script>
</body>
</html>
"""
        
        template = Template(template_content)
        return template.render(**ontology_data)
