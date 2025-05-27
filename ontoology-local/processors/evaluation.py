"""
Evaluation processor - integrates with OOPS! service for ontology evaluation.
"""

from typing import Dict, Any
from pathlib import Path
import requests
import logging
from jinja2 import Template


class EvaluationProcessor:
    """Generates ontology evaluation reports using OOPS! service."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the evaluation processor.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.oops_url = config.get('oops_url', 'http://oops.linkeddata.es/rest')
        self.timeout = config.get('timeout', 10)
        
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
            
            # Get evaluation from OOPS!
            evaluation_result = self._get_oops_evaluation(ontology_data)
            
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
    
    def _get_oops_evaluation(self, ontology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get evaluation results from OOPS! service."""
        try:
            # Read ontology file content
            with open(ontology_data['file_path'], 'r', encoding='utf-8') as f:
                ontology_content = f.read()
            
            # Prepare request data
            data = {
                'ontologyContent': ontology_content,
                'outputFormat': 'JSON'
            }
            
            # Make request to OOPS!
            self.logger.debug(f"Sending request to OOPS! service: {self.oops_url}")
            response = requests.post(
                self.oops_url,
                data=data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            self.logger.debug(f"OOPS! response status: {response.status_code}")
            self.logger.debug(f"OOPS! response content length: {len(response.text)}")
            
            if response.status_code == 200:
                # Check if response has content
                if not response.text.strip():
                    self.logger.warning("OOPS! service returned empty response")
                    return self._create_fallback_evaluation("Empty response from OOPS! service")
                
                try:
                    return response.json()
                except ValueError as json_error:
                    self.logger.warning(f"OOPS! service returned invalid JSON: {json_error}")
                    self.logger.debug(f"Response content: {response.text[:500]}...")
                    return self._create_fallback_evaluation("Invalid JSON response from OOPS! service")
            else:
                self.logger.warning(f"OOPS! service returned status {response.status_code}: {response.text[:200]}")
                return self._create_fallback_evaluation(f"OOPS! service error (HTTP {response.status_code})")
                
        except requests.RequestException as e:
            self.logger.warning(f"Could not connect to OOPS! service: {str(e)}")
            return self._create_fallback_evaluation(f"Connection error: {str(e)}")
        except Exception as e:
            self.logger.warning(f"Error during OOPS! evaluation: {str(e)}")
            return self._create_fallback_evaluation(f"Evaluation error: {str(e)}")
    
    def _create_fallback_evaluation(self, error_msg: str = None) -> Dict[str, Any]:
        """Create a fallback evaluation when OOPS! is not available."""
        warning_msg = error_msg or 'OOPS! service was not available during evaluation'
        return {
            'pitfalls': [],
            'suggestions': [],
            'warnings': [warning_msg],
            'summary': {
                'total_pitfalls': 0,
                'critical_pitfalls': 0,
                'important_pitfalls': 0,
                'minor_pitfalls': 0
            }
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
        
        .summary-card.critical { border-left: 4px solid #dc3545; }
        .summary-card.important { border-left: 4px solid #ffc107; }
        .summary-card.minor { border-left: 4px solid #17a2b8; }
        .summary-card.total { border-left: 4px solid #6c757d; }
        
        .pitfall-item {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .pitfall-item.critical {
            border-left: 4px solid #dc3545;
        }
        
        .pitfall-item.important {
            border-left: 4px solid #ffc107;
        }
        
        .pitfall-item.minor {
            border-left: 4px solid #17a2b8;
        }
        
        .pitfall-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .pitfall-description {
            color: #666;
            margin-bottom: 1rem;
        }
        
        .pitfall-elements {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9rem;
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
    </style>
</head>
<body>
    <div class="doc-header">
        <h1>{{ title }} - Evaluation Report</h1>
        <p>Ontology evaluation using OOPS! (OntOlogy Pitfall Scanner)</p>
    </div>
    
    <div class="doc-content">
        {% if evaluation.warnings %}
        <div class="warning-box">
            <h3>⚠️ Warnings</h3>
            <ul>
                {% for warning in evaluation.warnings %}
                <li>{{ warning }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% if evaluation.summary %}
        <div class="section">
            <h2>Evaluation Summary</h2>
            <div class="evaluation-summary">
                <div class="summary-card total">
                    <div class="stat-number">{{ evaluation.summary.total_pitfalls or 0 }}</div>
                    <div class="stat-label">Total Pitfalls</div>
                </div>
                <div class="summary-card critical">
                    <div class="stat-number">{{ evaluation.summary.critical_pitfalls or 0 }}</div>
                    <div class="stat-label">Critical</div>
                </div>
                <div class="summary-card important">
                    <div class="stat-number">{{ evaluation.summary.important_pitfalls or 0 }}</div>
                    <div class="stat-label">Important</div>
                </div>
                <div class="summary-card minor">
                    <div class="stat-number">{{ evaluation.summary.minor_pitfalls or 0 }}</div>
                    <div class="stat-label">Minor</div>
                </div>
            </div>
        </div>
        {% endif %}
        
        {% if evaluation.pitfalls %}
        <div class="section">
            <h2>Detected Pitfalls</h2>
            {% for pitfall in evaluation.pitfalls %}
            <div class="pitfall-item {{ pitfall.severity|lower }}">
                <div class="pitfall-title">
                    {{ pitfall.name or 'Pitfall #' + loop.index|string }}
                    {% if pitfall.severity %}
                    <span class="badge badge-{{ pitfall.severity|lower }}">{{ pitfall.severity }}</span>
                    {% endif %}
                </div>
                
                {% if pitfall.description %}
                <div class="pitfall-description">
                    {{ pitfall.description }}
                </div>
                {% endif %}
                
                {% if pitfall.elements %}
                <div class="pitfall-elements">
                    <strong>Affected elements:</strong><br>
                    {% for element in pitfall.elements %}
                    {{ element }}<br>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if pitfall.suggestion %}
                <div class="pitfall-suggestion">
                    <strong>Suggestion:</strong> {{ pitfall.suggestion }}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="success-box">
            <h3>✅ No Pitfalls Detected</h3>
            <p>Great! No common ontology pitfalls were detected in this ontology.</p>
        </div>
        {% endif %}
        
        {% if evaluation.suggestions %}
        <div class="section">
            <h2>General Suggestions</h2>
            <ul>
                {% for suggestion in evaluation.suggestions %}
                <li>{{ suggestion }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>About OOPS!</h2>
            <p>
                OOPS! (OntOlogy Pitfall Scanner) is a web-based tool that helps ontology developers 
                to detect some of the most common pitfalls appearing when developing ontologies. 
                The tool is based on a catalog of pitfalls and provides suggestions on how to fix them.
            </p>
            <p>
                <strong>Note:</strong> This evaluation is automated and may not catch all potential 
                issues. Manual review by domain experts is always recommended.
            </p>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by OnToology Local using OOPS! service</p>
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
