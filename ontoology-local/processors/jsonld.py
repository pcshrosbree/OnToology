"""
JSON-LD processor - generates JSON-LD context files for ontologies.
"""

from typing import Dict, Any
from pathlib import Path
import json
import logging
from rdflib.namespace import RDF, RDFS, OWL


class JsonLdProcessor:
    """Generates JSON-LD context files for ontologies."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the JSON-LD processor.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.include_standard_prefixes = config.get('include_standard_prefixes', True)
        
    def process(self, ontology_data: Dict[str, Any], base_name: str, 
                output_dir: str) -> Dict[str, Any]:
        """
        Generate JSON-LD context for an ontology.
        
        Args:
            ontology_data: Parsed ontology data
            base_name: Base filename for outputs
            output_dir: Output directory path
            
        Returns:
            Dictionary with output file information
        """
        try:
            output_file = f"{base_name}_context.jsonld"
            output_path = Path(output_dir) / output_file
            
            # Generate JSON-LD context
            context = self._generate_context(ontology_data)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Generated JSON-LD context: {output_file}")
            
            return {
                'file': output_file,
                'path': str(output_path),
                'context': context
            }
            
        except Exception as e:
            self.logger.error(f"JSON-LD generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _generate_context(self, ontology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the JSON-LD context."""
        
        context = {}
        
        # Add standard prefixes if enabled
        if self.include_standard_prefixes:
            context.update({
                "rdf": str(RDF),
                "rdfs": str(RDFS),
                "owl": str(OWL),
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "dc": "http://purl.org/dc/elements/1.1/",
                "dcterms": "http://purl.org/dc/terms/",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "skos": "http://www.w3.org/2004/02/skos/core#"
            })
        
        # Add ontology-specific namespaces
        namespaces = ontology_data.get('namespaces', {})
        for prefix, namespace in namespaces.items():
            if prefix and prefix not in context:
                context[prefix] = namespace
        
        # Add ontology base URI if available
        ontology_uri = ontology_data.get('ontology_uri')
        if ontology_uri:
            # Try to determine a good prefix for the ontology
            ontology_prefix = self._get_ontology_prefix(ontology_uri, namespaces)
            if ontology_prefix:
                context[ontology_prefix] = ontology_uri
        
        # Add classes
        classes = ontology_data.get('classes', [])
        for cls in classes:
            short_name = self._get_short_name(cls['uri'])
            if short_name and short_name not in context:
                context[short_name] = {
                    "@id": cls['uri'],
                    "@type": "@id"
                }
        
        # Add properties
        properties = ontology_data.get('properties', {})
        
        # Object properties
        for prop in properties.get('object_properties', []):
            short_name = self._get_short_name(prop['uri'])
            if short_name and short_name not in context:
                context[short_name] = {
                    "@id": prop['uri'],
                    "@type": "@id"
                }
        
        # Datatype properties
        for prop in properties.get('datatype_properties', []):
            short_name = self._get_short_name(prop['uri'])
            if short_name and short_name not in context:
                # Try to determine the datatype from range
                prop_context = {"@id": prop['uri']}
                
                ranges = prop.get('range', [])
                if ranges:
                    # Use the first range as the type hint
                    range_uri = ranges[0]
                    if 'XMLSchema' in range_uri:
                        prop_context["@type"] = range_uri
                    else:
                        prop_context["@type"] = "@id"
                
                context[short_name] = prop_context
        
        # Annotation properties
        for prop in properties.get('annotation_properties', []):
            short_name = self._get_short_name(prop['uri'])
            if short_name and short_name not in context:
                context[short_name] = prop['uri']
        
        # Add individuals
        individuals = ontology_data.get('individuals', [])
        for individual in individuals:
            short_name = self._get_short_name(individual['uri'])
            if short_name and short_name not in context:
                context[short_name] = {
                    "@id": individual['uri'],
                    "@type": "@id"
                }
        
        # Wrap in @context
        return {
            "@context": context
        }
    
    def _get_ontology_prefix(self, ontology_uri: str, 
                           namespaces: Dict[str, str]) -> str:
        """Determine a good prefix for the ontology."""
        
        # Check if there's already a prefix for this namespace
        for prefix, namespace in namespaces.items():
            if namespace == ontology_uri or ontology_uri.startswith(namespace):
                return prefix
        
        # Try to extract from URI
        if '#' in ontology_uri:
            base = ontology_uri.split('#')[0]
        elif '/' in ontology_uri:
            parts = ontology_uri.rstrip('/').split('/')
            base = '/'.join(parts[:-1]) + '/'
        else:
            return None
        
        # Generate a prefix based on the URI
        if '/' in base:
            potential_prefix = base.split('/')[-2] if base.endswith('/') else base.split('/')[-1]
        else:
            potential_prefix = 'ont'
        
        # Clean up the prefix
        potential_prefix = ''.join(c for c in potential_prefix if c.isalnum())
        
        return potential_prefix.lower() if potential_prefix else 'ont'
    
    def _get_short_name(self, uri: str) -> str:
        """Extract short name from URI."""
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            return uri.split('/')[-1]
        return uri
