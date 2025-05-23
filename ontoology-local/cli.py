#!/usr/bin/env python3
"""
OnToology Local - Standalone command-line tool for ontology documentation generation.
Generates HTML documentation, diagrams, evaluations, and more from local ontology files.
"""

import click
import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any

from utils.discovery import OntologyDiscovery
from utils.output_manager import OutputManager
from processors.documentation import DocumentationProcessor
from processors.evaluation import EvaluationProcessor
from processors.diagrams import DiagramProcessor
from processors.jsonld import JsonLdProcessor
from processors.validation import ValidationProcessor


@click.command()
@click.option('--input', '-i', 'input_dir', required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help='Input directory containing ontology files (.owl, .rdf, .ttl)')
@click.option('--output', '-o', 'output_dir', required=True, type=click.Path(file_okay=False, dir_okay=True),
              help='Output directory for generated documentation')
@click.option('--tools', '-t', default='doc,eval,diagrams,jsonld,validation',
              help='Comma-separated list of tools to run (doc,eval,diagrams,jsonld,validation)')
@click.option('--config', '-c', type=click.Path(exists=True, file_okay=True, dir_okay=False),
              help='Configuration file (YAML format)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--parallel', '-p', is_flag=True, help='Process ontologies in parallel')
def main(input_dir: str, output_dir: str, tools: str, config: str, verbose: bool, parallel: bool):
    """
    OnToology Local - Generate comprehensive documentation for ontologies.
    
    This tool processes OWL, RDF, and TTL files from a local directory and generates
    HTML documentation, diagrams, evaluation reports, JSON-LD contexts, and validation
    results in a flat output structure suitable for local browsing.
    """
    
    # Setup logging
    import logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("OnToology Local - Starting ontology processing")
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Load configuration
    config_data = load_config(config) if config else {}
    
    # Parse tools list
    enabled_tools = [tool.strip() for tool in tools.split(',')]
    logger.info(f"Enabled tools: {enabled_tools}")
    
    try:
        # Discover ontology files
        discovery = OntologyDiscovery(input_dir)
        ontology_files = discovery.find_ontologies()
        
        if not ontology_files:
            logger.error("No ontology files found in the input directory")
            sys.exit(1)
            
        logger.info(f"Found {len(ontology_files)} ontology files")
        
        # Setup output manager
        output_manager = OutputManager(output_dir)
        output_manager.setup_output_directory()
        
        # Initialize processors
        processors = initialize_processors(enabled_tools, config_data, logger)
        
        # Process each ontology
        results = []
        for i, ontology_file in enumerate(ontology_files, 1):
            logger.info(f"Processing {i}/{len(ontology_files)}: {ontology_file}")
            
            try:
                result = process_ontology(ontology_file, processors, output_manager, logger)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {ontology_file}: {str(e)}")
                if verbose:
                    import traceback
                    traceback.print_exc()
                continue
        
        # Generate index page
        output_manager.generate_index(results)
        
        logger.info(f"Processing complete! Generated documentation for {len(results)} ontologies")
        logger.info(f"Open {os.path.join(output_dir, 'index.html')} in your browser to view results")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        click.echo(f"Warning: Could not load config file {config_file}: {e}")
        return {}


def initialize_processors(enabled_tools: List[str], config: Dict[str, Any], logger) -> Dict[str, Any]:
    """Initialize the enabled processors."""
    processors = {}
    
    if 'doc' in enabled_tools:
        processors['documentation'] = DocumentationProcessor(config.get('documentation', {}), logger)
    
    if 'eval' in enabled_tools:
        processors['evaluation'] = EvaluationProcessor(config.get('evaluation', {}), logger)
    
    if 'diagrams' in enabled_tools:
        processors['diagrams'] = DiagramProcessor(config.get('diagrams', {}), logger)
    
    if 'jsonld' in enabled_tools:
        processors['jsonld'] = JsonLdProcessor(config.get('jsonld', {}), logger)
    
    if 'validation' in enabled_tools:
        processors['validation'] = ValidationProcessor(config.get('validation', {}), logger)
    
    return processors


def process_ontology(ontology_file: str, processors: Dict[str, Any], output_manager: OutputManager, logger) -> Dict[str, Any]:
    """Process a single ontology file with all enabled processors."""
    
    # Parse ontology
    from utils.ontology_parser import OntologyParser
    parser = OntologyParser(ontology_file)
    ontology_data = parser.parse()
    
    # Generate base filename for outputs
    base_name = Path(ontology_file).stem
    
    result = {
        'file': ontology_file,
        'base_name': base_name,
        'title': ontology_data.get('title', base_name),
        'description': ontology_data.get('description', ''),
        'outputs': {}
    }
    
    # Run each processor
    for processor_name, processor in processors.items():
        try:
            logger.debug(f"Running {processor_name} processor for {base_name}")
            output_files = processor.process(ontology_data, base_name, output_manager.output_dir)
            result['outputs'][processor_name] = output_files
        except Exception as e:
            logger.error(f"Error in {processor_name} processor for {base_name}: {str(e)}")
            result['outputs'][processor_name] = {'error': str(e)}
    
    return result


if __name__ == '__main__':
    main()
