"""
Validation processor - performs basic ontology validation checks.
"""

from typing import Dict, Any, List
from pathlib import Path
import logging
from jinja2 import Template
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, OWL


class ValidationProcessor:
    """Performs basic validation checks on ontologies."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the validation processor.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.check_consistency = config.get('check_consistency', True)
        self.check_completeness = config.get('check_completeness', True)
        
    def process(self, ontology_data: Dict[str, Any], base_name: str, 
                output_dir: str) -> Dict[str, Any]:
        """
        Generate validation report for an ontology.
        
        Args:
            ontology_data: Parsed ontology data
            base_name: Base filename for outputs
            output_dir: Output directory path
            
        Returns:
            Dictionary with output file information
        """
        try:
            output_file = f"{base_name}_validation.html"
            output_path = Path(output_dir) / output_file
            
            # Perform validation checks
            validation_results = self._validate_ontology(ontology_data)
            
            # Generate HTML report
            html_content = self._generate_html_report(
                ontology_data, validation_results
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Generated validation report: {output_file}")
            
            return {
                'file': output_file,
                'path': str(output_path),
                'validation': validation_results
            }
            
        except Exception as e:
            self.logger.error(f"Validation generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _validate_ontology(self, ontology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive validation of the ontology."""
        
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'summary': {
                'total_issues': 0,
                'errors': 0,
                'warnings': 0,
                'info': 0
            }
        }
        
        graph = ontology_data.get('graph')
        if not graph:
            results['errors'].append({
                'type': 'Parse Error',
                'message': 'Could not parse ontology graph',
                'severity': 'error'
            })
            return results
        
        # Basic syntax validation
        self._check_syntax(graph, results)
        
        # Metadata validation
        self._check_metadata(ontology_data, results)
        
        # Class validation
        self._check_classes(ontology_data, results)
        
        # Property validation
        self._check_properties(ontology_data, results)
        
        # Consistency checks
        if self.check_consistency:
            self._check_consistency_issues(ontology_data, results)
        
        # Completeness checks
        if self.check_completeness:
            self._check_completeness_issues(ontology_data, results)
        
        # Calculate summary
        results['summary']['errors'] = len(results['errors'])
        results['summary']['warnings'] = len(results['warnings'])
        results['summary']['info'] = len(results['info'])
        results['summary']['total_issues'] = (
            results['summary']['errors'] + 
            results['summary']['warnings'] + 
            results['summary']['info']
        )
        
        return results
    
    def _check_syntax(self, graph: Graph, results: Dict[str, Any]):
        """Check for basic syntax issues."""
        
        # Check for triples
        if len(graph) == 0:
            results['warnings'].append({
                'type': 'Empty Ontology',
                'message': 'The ontology contains no triples',
                'severity': 'warning'
            })
    
    def _check_metadata(self, ontology_data: Dict[str, Any], 
                       results: Dict[str, Any]):
        """Check ontology metadata completeness."""
        
        # Check for ontology declaration
        if not ontology_data.get('ontology_uri'):
            results['warnings'].append({
                'type': 'Missing Ontology Declaration',
                'message': 'No owl:Ontology declaration found',
                'severity': 'warning'
            })
        
        # Check for title
        if not ontology_data.get('title') or ontology_data.get('title') == ontology_data.get('file_path', '').split('/')[-1].split('.')[0]:
            results['info'].append({
                'type': 'Missing Title',
                'message': 'Consider adding a title (dc:title or rdfs:label)',
                'severity': 'info'
            })
        
        # Check for description
        if not ontology_data.get('description'):
            results['info'].append({
                'type': 'Missing Description',
                'message': 'Consider adding a description (dc:description or rdfs:comment)',
                'severity': 'info'
            })
        
        # Check for version
        if not ontology_data.get('version'):
            results['info'].append({
                'type': 'Missing Version',
                'message': 'Consider adding version information (owl:versionInfo)',
                'severity': 'info'
            })
        
        # Check for authors
        if not ontology_data.get('authors'):
            results['info'].append({
                'type': 'Missing Authors',
                'message': 'Consider adding author information (dc:creator)',
                'severity': 'info'
            })
    
    def _check_classes(self, ontology_data: Dict[str, Any], 
                      results: Dict[str, Any]):
        """Check class definitions."""
        
        classes = ontology_data.get('classes', [])
        
        if not classes:
            results['warnings'].append({
                'type': 'No Classes',
                'message': 'No OWL classes found in the ontology',
                'severity': 'warning'
            })
            return
        
        # Check for classes without labels
        unlabeled_classes = [cls for cls in classes if not cls.get('label') or cls['label'] == self._get_short_name(cls['uri'])]
        if unlabeled_classes:
            results['info'].append({
                'type': 'Classes Without Labels',
                'message': f'{len(unlabeled_classes)} classes lack rdfs:label annotations',
                'details': [cls['uri'] for cls in unlabeled_classes[:5]],
                'severity': 'info'
            })
        
        # Check for classes without comments
        uncommented_classes = [cls for cls in classes if not cls.get('comment')]
        if uncommented_classes:
            results['info'].append({
                'type': 'Classes Without Comments',
                'message': f'{len(uncommented_classes)} classes lack rdfs:comment annotations',
                'details': [cls['uri'] for cls in uncommented_classes[:5]],
                'severity': 'info'
            })
    
    def _check_properties(self, ontology_data: Dict[str, Any], 
                         results: Dict[str, Any]):
        """Check property definitions."""
        
        properties = ontology_data.get('properties', {})
        all_props = (properties.get('object_properties', []) + 
                    properties.get('datatype_properties', []) + 
                    properties.get('annotation_properties', []))
        
        if not all_props:
            results['warnings'].append({
                'type': 'No Properties',
                'message': 'No properties found in the ontology',
                'severity': 'warning'
            })
            return
        
        # Check object properties without domain/range
        obj_props = properties.get('object_properties', [])
        for prop in obj_props:
            if not prop.get('domain'):
                results['info'].append({
                    'type': 'Property Without Domain',
                    'message': f'Object property {self._get_short_name(prop["uri"])} has no domain',
                    'severity': 'info'
                })
            
            if not prop.get('range'):
                results['info'].append({
                    'type': 'Property Without Range',
                    'message': f'Object property {self._get_short_name(prop["uri"])} has no range',
                    'severity': 'info'
                })
        
        # Check datatype properties without domain/range
        data_props = properties.get('datatype_properties', [])
        for prop in data_props:
            if not prop.get('domain'):
                results['info'].append({
                    'type': 'Property Without Domain',
                    'message': f'Datatype property {self._get_short_name(prop["uri"])} has no domain',
                    'severity': 'info'
                })
            
            if not prop.get('range'):
                results['info'].append({
                    'type': 'Property Without Range',
                    'message': f'Datatype property {self._get_short_name(prop["uri"])} has no range',
                    'severity': 'info'
                })
    
    def _check_consistency_issues(self, ontology_data: Dict[str, Any], 
                                 results: Dict[str, Any]):
        """Check for potential consistency issues."""
        
        # Check for circular class hierarchies (simplified check)
        classes = ontology_data.get('classes', [])
        class_hierarchy = {}
        
        for cls in classes:
            class_hierarchy[cls['uri']] = cls.get('superclasses', [])
        
        # Simple cycle detection
        for cls_uri in class_hierarchy:
            visited = set()
            current = cls_uri
            
            while current and current in class_hierarchy:
                if current in visited:
                    results['errors'].append({
                        'type': 'Circular Class Hierarchy',
                        'message': f'Circular inheritance detected involving {self._get_short_name(cls_uri)}',
                        'severity': 'error'
                    })
                    break
                
                visited.add(current)
                superclasses = class_hierarchy[current]
                current = superclasses[0] if superclasses else None
    
    def _check_completeness_issues(self, ontology_data: Dict[str, Any], 
                                  results: Dict[str, Any]):
        """Check for completeness issues."""
        
        # Check if there are individuals but no classes
        individuals = ontology_data.get('individuals', [])
        classes = ontology_data.get('classes', [])
        
        if individuals and not classes:
            results['warnings'].append({
                'type': 'Individuals Without Classes',
                'message': 'Ontology has individuals but no class definitions',
                'severity': 'warning'
            })
        
        # Check for unused namespaces
        namespaces = ontology_data.get('namespaces', {})
        if len(namespaces) > 10:  # Arbitrary threshold
            results['info'].append({
                'type': 'Many Namespaces',
                'message': f'Ontology declares {len(namespaces)} namespaces - consider if all are needed',
                'severity': 'info'
            })
    
    def _generate_html_report(self, ontology_data: Dict[str, Any], 
                             validation: Dict[str, Any]) -> str:
        """Generate HTML validation report."""
        
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Validation Report</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .validation-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .summary-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .summary-card.errors { border-left: 4px solid #dc3545; }
        .summary-card.warnings { border-left: 4px solid #ffc107; }
        .summary-card.info { border-left: 4px solid #17a2b8; }
        .summary-card.total { border-left: 4px solid #6c757d; }
        
        .issue-item {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .issue-item.error { border-left: 4px solid #dc3545; }
        .issue-item.warning { border-left: 4px solid #ffc107; }
        .issue-item.info { border-left: 4px solid #17a2b8; }
        
        .issue-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .issue-message {
            color: #666;
            margin-bottom: 0.5rem;
        }
        
        .issue-details {
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9rem;
        }
        
        .success-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="doc-header">
        <h1>{{ title }} - Validation Report</h1>
        <p>Basic ontology validation and quality checks</p>
    </div>
    
    <div class="doc-content">
        <div class="section">
            <h2>Validation Summary</h2>
            <div class="validation-summary">
                <div class="summary-card total">
                    <div class="stat-number">{{ validation.summary.total_issues }}</div>
                    <div class="stat-label">Total Issues</div>
                </div>
                <div class="summary-card errors">
                    <div class="stat-number">{{ validation.summary.errors }}</div>
                    <div class="stat-label">Errors</div>
                </div>
                <div class="summary-card warnings">
                    <div class="stat-number">{{ validation.summary.warnings }}</div>
                    <div class="stat-label">Warnings</div>
                </div>
                <div class="summary-card info">
                    <div class="stat-number">{{ validation.summary.info }}</div>
                    <div class="stat-label">Suggestions</div>
                </div>
            </div>
        </div>
        
        {% if validation.summary.total_issues == 0 %}
        <div class="success-box">
            <h3>✅ No Issues Found</h3>
            <p>Great! The ontology passed all basic validation checks.</p>
        </div>
        {% endif %}
        
        {% if validation.errors %}
        <div class="section">
            <h2>Errors ({{ validation.errors|length }})</h2>
            {% for issue in validation.errors %}
            <div class="issue-item error">
                <div class="issue-title">{{ issue.type }}</div>
                <div class="issue-message">{{ issue.message }}</div>
                {% if issue.details %}
                <div class="issue-details">
                    {% for detail in issue.details %}
                    {{ detail }}<br>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if validation.warnings %}
        <div class="section">
            <h2>Warnings ({{ validation.warnings|length }})</h2>
            {% for issue in validation.warnings %}
            <div class="issue-item warning">
                <div class="issue-title">{{ issue.type }}</div>
                <div class="issue-message">{{ issue.message }}</div>
                {% if issue.details %}
                <div class="issue-details">
                    {% for detail in issue.details %}
                    {{ detail }}<br>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if validation.info %}
        <div class="section">
            <h2>Suggestions ({{ validation.info|length }})</h2>
            {% for issue in validation.info %}
            <div class="issue-item info">
                <div class="issue-title">{{ issue.type }}</div>
                <div class="issue-message">{{ issue.message }}</div>
                {% if issue.details %}
                <div class="issue-details">
                    {% for detail in issue.details %}
                    {{ detail }}<br>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="section">
            <h2>About This Validation</h2>
            <p>
                This validation report covers basic ontology quality checks including:
            </p>
            <ul>
                <li>Syntax validation</li>
                <li>Metadata completeness</li>
                <li>Class and property definitions</li>
                <li>Basic consistency checks</li>
                <li>Completeness suggestions</li>
            </ul>
            <p>
                <strong>Note:</strong> This is a basic validation. For comprehensive 
                ontology validation, consider using specialized tools like Pellet 
                or HermiT.
            </p>
        </div>
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
        return template.render(
            title=ontology_data.get('title', 'Ontology'),
            validation=validation
        )
    
    def _get_short_name(self, uri: str) -> str:
        """Extract short name from URI."""
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            return uri.split('/')[-1]
        return uri
