"""
Evaluation processor - provides basic ontology evaluation capabilities.
"""

from typing import Dict, Any
from pathlib import Path
import logging
from jinja2 import Template


class EvaluationProcessor:
    """Generates basic ontology evaluation reports."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the evaluation processor.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
    def process(self, ontology_data: Dict[str, Any], base_name: str, 
                output_dir: str) -> Dict[str, Any]:
        """
        Generate evaluation report for an ontology.
        
        Args:
            ontology_data: Parsed ontology data
            base_name: Base filename for outputs
            output_dir: Output directory path
            
        Returns:
            Dictionary with output file information
        """
        try:
            output_file = f"{base_name}_evaluation.html"
            output_path = Path(output_dir) / output_file
            
            # Generate basic evaluation
            evaluation_result = self._generate_basic_evaluation(ontology_data)
            
            # Generate HTML report
            html_content = self._generate_html_report(
                ontology_data, evaluation_result
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Generated evaluation: {output_file}")
            
            return {
                'file': output_file,
                'path': str(output_path),
                'evaluation': evaluation_result
            }
            
        except Exception as e:
            self.logger.error(f"Evaluation generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _generate_basic_evaluation(self, ontology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic evaluation metrics for the ontology."""
        try:
            metrics = {
                'classes': len(ontology_data.get('classes', [])),
                'properties': len(ontology_data.get('properties', [])),
                'individuals': len(ontology_data.get('individuals', [])),
                'annotations': len(ontology_data.get('annotations', [])),
            }
            
            # Basic quality checks
            issues = []
            suggestions = []
            
            # Check for missing documentation
            if not ontology_data.get('description'):
                issues.append("Ontology lacks a description")
                suggestions.append(
                    "Add rdfs:comment or dc:description to provide "
                    "ontology documentation"
                )
            
            # Check for missing labels
            unlabeled_classes = [
                c for c in ontology_data.get('classes', []) 
                if not c.get('label')
            ]
            if unlabeled_classes:
                issues.append(f"{len(unlabeled_classes)} classes lack "
                             "rdfs:label")
                suggestions.append(
                    "Add rdfs:label to all classes for better readability"
                )
            
            unlabeled_properties = [
                p for p in ontology_data.get('properties', []) 
                if not p.get('label')
            ]
            if unlabeled_properties:
                issues.append(f"{len(unlabeled_properties)} properties lack "
                             "rdfs:label")
                suggestions.append(
                    "Add rdfs:label to all properties for better readability"
                )
            
            # Check for missing comments
            uncommented_classes = [
                c for c in ontology_data.get('classes', []) 
                if not c.get('comment')
            ]
            if uncommented_classes:
                issues.append(f"{len(uncommented_classes)} classes lack "
                             "rdfs:comment")
                suggestions.append(
                    "Add rdfs:comment to classes to explain their purpose"
                )
            
            return {
                'metrics': metrics,
                'issues': issues,
                'suggestions': suggestions,
                'summary': {
                    'total_issues': len(issues),
                    'documentation_issues': len([
                        i for i in issues 
                        if 'label' in i or 'comment' in i or 'description' in i
                    ])
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Error during basic evaluation: {str(e)}")
            return {
                'metrics': {},
                'issues': [f"Evaluation error: {str(e)}"],
                'suggestions': [],
                'summary': {'total_issues': 1, 'documentation_issues': 0}
            }
    
    def _generate_html_report(self, ontology_data: Dict[str, Any], 
                             evaluation: Dict[str, Any]) -> str:
        """Generate HTML evaluation report."""
        
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Evaluation Report</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .evaluation-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
        
        .summary-card.total { border-left: 4px solid #6c757d; }
        .summary-card.documentation { border-left: 4px solid #17a2b8; }
        
        .issue-item {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #ffc107;
        }
        
        .issue-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .success-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-number {
            font-size: 2rem;
            font-weight: bold;
            color: #007bff;
        }
        
        .metric-label {
            color: #6c757d;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="doc-header">
        <h1>{{ title }} - Evaluation Report</h1>
        <p>Basic ontology quality evaluation</p>
    </div>
    
    <div class="doc-content">
        {% if evaluation.metrics %}
        <div class="section">
            <h2>Ontology Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-number">{{ evaluation.metrics.classes }}</div>
                    <div class="metric-label">Classes</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{{ evaluation.metrics.properties }}</div>
                    <div class="metric-label">Properties</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{{ evaluation.metrics.individuals }}</div>
                    <div class="metric-label">Individuals</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{{ evaluation.metrics.annotations }}</div>
                    <div class="metric-label">Annotations</div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if evaluation.summary %}
        <div class="section">
            <h2>Quality Summary</h2>
            <div class="evaluation-summary">
                <div class="summary-card total">
                    <div class="stat-number">{{ evaluation.summary.total_issues }}</div>
                    <div class="stat-label">Total Issues</div>
                </div>
                <div class="summary-card documentation">
                    <div class="stat-number">{{ evaluation.summary.documentation_issues }}</div>
                    <div class="stat-label">Documentation Issues</div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if evaluation.issues %}
        <div class="section">
            <h2>Detected Issues</h2>
            {% for issue in evaluation.issues %}
            <div class="issue-item">
                <div class="issue-title">{{ issue }}</div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="success-box">
            <h3>✅ No Issues Detected</h3>
            <p>Great! No quality issues were detected in this ontology.</p>
        </div>
        {% endif %}
        
        {% if evaluation.suggestions %}
        <div class="section">
            <h2>Suggestions for Improvement</h2>
            <ul>
                {% for suggestion in evaluation.suggestions %}
                <li>{{ suggestion }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>About This Evaluation</h2>
            <p>
                This evaluation performs basic quality checks on the ontology, 
                focusing on documentation completeness and structural consistency.
            </p>
            <p>
                <strong>Note:</strong> This evaluation is automated and may not 
                catch all potential issues. Manual review by domain experts is 
                always recommended.
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
            evaluation=evaluation
        )
