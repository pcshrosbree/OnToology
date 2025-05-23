"""
Ontology parsing utilities using RDFLib.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, DC, DCTERMS


class OntologyParser:
    """Parses ontology files and extracts metadata and structure."""
    
    def __init__(self, file_path: str):
        """
        Initialize the parser with an ontology file.
        
        Args:
            file_path: Path to the ontology file
        """
        self.file_path = Path(file_path)
        self.graph = Graph()
        self.ontology_uri = None
        
    def parse(self) -> Dict[str, Any]:
        """
        Parse the ontology file and extract comprehensive information.
        
        Returns:
            Dictionary containing ontology metadata and structure
        """
        try:
            # Load the ontology
            self.graph.parse(str(self.file_path))
            
            # Find the ontology URI
            self.ontology_uri = self._find_ontology_uri()
            
            # Extract all information
            return {
                'file_path': str(self.file_path),
                'ontology_uri': str(self.ontology_uri) if self.ontology_uri else None,
                'title': self._extract_title(),
                'description': self._extract_description(),
                'version': self._extract_version(),
                'authors': self._extract_authors(),
                'license': self._extract_license(),
                'imports': self._extract_imports(),
                'classes': self._extract_classes(),
                'properties': self._extract_properties(),
                'individuals': self._extract_individuals(),
                'namespaces': self._extract_namespaces(),
                'statistics': self._calculate_statistics(),
                'graph': self.graph  # Include the graph for processors
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse ontology {self.file_path}: {str(e)}")
    
    def _find_ontology_uri(self) -> Optional[URIRef]:
        """Find the main ontology URI."""
        # Look for owl:Ontology declarations
        for ontology in self.graph.subjects(RDF.type, OWL.Ontology):
            return ontology
        
        # If no explicit ontology declaration, try to infer from base URI
        base_uris = set()
        for s, p, o in self.graph:
            if isinstance(s, URIRef):
                base_uris.add(str(s).split('#')[0].split('/')[-1])
        
        return None
    
    def _extract_title(self) -> str:
        """Extract ontology title."""
        if self.ontology_uri:
            # Try various title properties
            for title_prop in [DC.title, DCTERMS.title, RDFS.label]:
                title = self.graph.value(self.ontology_uri, title_prop)
                if title:
                    return str(title)
        
        # Fallback to filename
        return self.file_path.stem
    
    def _extract_description(self) -> str:
        """Extract ontology description."""
        if self.ontology_uri:
            # Try various description properties
            for desc_prop in [DC.description, DCTERMS.description, RDFS.comment]:
                desc = self.graph.value(self.ontology_uri, desc_prop)
                if desc:
                    return str(desc)
        
        return ""
    
    def _extract_version(self) -> str:
        """Extract ontology version."""
        if self.ontology_uri:
            version = self.graph.value(self.ontology_uri, OWL.versionInfo)
            if version:
                return str(version)
        
        return ""
    
    def _extract_authors(self) -> List[str]:
        """Extract ontology authors."""
        authors = []
        if self.ontology_uri:
            for author_prop in [DC.creator, DCTERMS.creator, DC.contributor]:
                for author in self.graph.objects(self.ontology_uri, author_prop):
                    authors.append(str(author))
        
        return authors
    
    def _extract_license(self) -> str:
        """Extract license information."""
        if self.ontology_uri:
            license_uri = self.graph.value(self.ontology_uri, DCTERMS.license)
            if license_uri:
                return str(license_uri)
        
        return ""
    
    def _extract_imports(self) -> List[str]:
        """Extract imported ontologies."""
        imports = []
        if self.ontology_uri:
            for imported in self.graph.objects(self.ontology_uri, OWL.imports):
                imports.append(str(imported))
        
        return imports
    
    def _extract_classes(self) -> List[Dict[str, Any]]:
        """Extract OWL classes."""
        classes = []
        
        for cls in self.graph.subjects(RDF.type, OWL.Class):
            if isinstance(cls, URIRef):
                class_info = {
                    'uri': str(cls),
                    'label': self._get_label(cls),
                    'comment': self._get_comment(cls),
                    'subclasses': [str(sub) for sub in self.graph.subjects(RDFS.subClassOf, cls)],
                    'superclasses': [str(sup) for sup in self.graph.objects(cls, RDFS.subClassOf)]
                }
                classes.append(class_info)
        
        return sorted(classes, key=lambda x: x['label'])
    
    def _extract_properties(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract OWL properties."""
        properties = {
            'object_properties': [],
            'datatype_properties': [],
            'annotation_properties': []
        }
        
        # Object properties
        for prop in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(prop, URIRef):
                prop_info = self._get_property_info(prop)
                properties['object_properties'].append(prop_info)
        
        # Datatype properties
        for prop in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            if isinstance(prop, URIRef):
                prop_info = self._get_property_info(prop)
                properties['datatype_properties'].append(prop_info)
        
        # Annotation properties
        for prop in self.graph.subjects(RDF.type, OWL.AnnotationProperty):
            if isinstance(prop, URIRef):
                prop_info = self._get_property_info(prop)
                properties['annotation_properties'].append(prop_info)
        
        # Sort each category
        for category in properties.values():
            category.sort(key=lambda x: x['label'])
        
        return properties
    
    def _extract_individuals(self) -> List[Dict[str, Any]]:
        """Extract OWL individuals."""
        individuals = []
        
        for individual in self.graph.subjects(RDF.type, OWL.NamedIndividual):
            if isinstance(individual, URIRef):
                individual_info = {
                    'uri': str(individual),
                    'label': self._get_label(individual),
                    'comment': self._get_comment(individual),
                    'types': [str(t) for t in self.graph.objects(individual, RDF.type) 
                             if t != OWL.NamedIndividual]
                }
                individuals.append(individual_info)
        
        return sorted(individuals, key=lambda x: x['label'])
    
    def _extract_namespaces(self) -> Dict[str, str]:
        """Extract namespace prefixes."""
        namespaces = {}
        for prefix, namespace in self.graph.namespaces():
            if prefix:  # Skip empty prefixes
                namespaces[prefix] = str(namespace)
        
        return namespaces
    
    def _calculate_statistics(self) -> Dict[str, int]:
        """Calculate basic statistics about the ontology."""
        stats = {
            'total_triples': len(self.graph),
            'classes': len(list(self.graph.subjects(RDF.type, OWL.Class))),
            'object_properties': len(list(self.graph.subjects(RDF.type, OWL.ObjectProperty))),
            'datatype_properties': len(list(self.graph.subjects(RDF.type, OWL.DatatypeProperty))),
            'annotation_properties': len(list(self.graph.subjects(RDF.type, OWL.AnnotationProperty))),
            'individuals': len(list(self.graph.subjects(RDF.type, OWL.NamedIndividual)))
        }
        
        return stats
    
    def _get_property_info(self, prop: URIRef) -> Dict[str, Any]:
        """Get detailed information about a property."""
        return {
            'uri': str(prop),
            'label': self._get_label(prop),
            'comment': self._get_comment(prop),
            'domain': [str(d) for d in self.graph.objects(prop, RDFS.domain)],
            'range': [str(r) for r in self.graph.objects(prop, RDFS.range)],
            'subproperties': [str(sub) for sub in self.graph.subjects(RDFS.subPropertyOf, prop)],
            'superproperties': [str(sup) for sup in self.graph.objects(prop, RDFS.subPropertyOf)]
        }
    
    def _get_label(self, resource: URIRef) -> str:
        """Get the label for a resource, with fallback to local name."""
        label = self.graph.value(resource, RDFS.label)
        if label:
            return str(label)
        
        # Fallback to local name
        uri_str = str(resource)
        if '#' in uri_str:
            return uri_str.split('#')[-1]
        elif '/' in uri_str:
            return uri_str.split('/')[-1]
        
        return uri_str
    
    def _get_comment(self, resource: URIRef) -> str:
        """Get the comment for a resource."""
        comment = self.graph.value(resource, RDFS.comment)
        return str(comment) if comment else ""
