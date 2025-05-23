"""
Diagram processor - generates visual diagrams for ontologies using NetworkX and Matplotlib.
"""

from typing import Dict, Any
from pathlib import Path
import logging
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from rdflib.namespace import RDF, RDFS, OWL


class DiagramProcessor:
    """Generates visual diagrams for ontologies."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize the diagram processor.
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.diagram_format = config.get('format', 'png')
        self.include_properties = config.get('include_properties', True)
        self.max_nodes = config.get('max_nodes', 50)
        
    def process(self, ontology_data: Dict[str, Any], base_name: str, 
                output_dir: str) -> Dict[str, Any]:
        """
        Generate diagram for an ontology.
        
        Args:
            ontology_data: Parsed ontology data
            base_name: Base filename for outputs
            output_dir: Output directory path
            
        Returns:
            Dictionary with output file information
        """
        try:
            output_file = f"{base_name}_diagram.{self.diagram_format}"
            output_path = Path(output_dir) / output_file
            
            # Create the diagram
            self._create_ontology_diagram(ontology_data, output_path)
            
            self.logger.info(f"Generated diagram: {output_file}")
            
            return {
                'file': output_file,
                'path': str(output_path),
                'format': self.diagram_format
            }
            
        except Exception as e:
            self.logger.error(f"Diagram generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _create_ontology_diagram(self, ontology_data: Dict[str, Any], 
                                output_path: Path):
        """Create and save the ontology diagram."""
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add classes as nodes
        classes = ontology_data.get('classes', [])
        for cls in classes[:self.max_nodes]:  # Limit nodes for readability
            label = self._get_short_name(cls['uri'])
            G.add_node(cls['uri'], 
                      label=label, 
                      node_type='class',
                      full_label=cls.get('label', label))
        
        # Add subclass relationships
        for cls in classes:
            if cls['uri'] in G.nodes:
                for superclass in cls.get('superclasses', []):
                    if superclass in G.nodes:
                        G.add_edge(cls['uri'], superclass, 
                                 edge_type='subClassOf')
        
        # Add properties if enabled
        if self.include_properties:
            properties = ontology_data.get('properties', {})
            
            # Add object properties
            for prop in properties.get('object_properties', []):
                if len(G.nodes) >= self.max_nodes:
                    break
                    
                prop_label = self._get_short_name(prop['uri'])
                G.add_node(prop['uri'], 
                          label=prop_label, 
                          node_type='object_property',
                          full_label=prop.get('label', prop_label))
                
                # Connect to domain and range
                for domain in prop.get('domain', []):
                    if domain in G.nodes:
                        G.add_edge(domain, prop['uri'], edge_type='domain')
                
                for range_cls in prop.get('range', []):
                    if range_cls in G.nodes:
                        G.add_edge(prop['uri'], range_cls, edge_type='range')
        
        # Create the visualization
        self._visualize_graph(G, output_path, ontology_data.get('title', 'Ontology'))
    
    def _visualize_graph(self, G: nx.DiGraph, output_path: Path, title: str):
        """Create and save the graph visualization."""
        
        # Set up the plot
        plt.figure(figsize=(16, 12))
        plt.title(f"{title} - Ontology Structure", fontsize=16, fontweight='bold')
        
        # Choose layout algorithm
        if len(G.nodes) > 20:
            pos = nx.spring_layout(G, k=3, iterations=50)
        else:
            pos = nx.spring_layout(G, k=5, iterations=100)
        
        # Define colors for different node types
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            node_type = G.nodes[node].get('node_type', 'class')
            if node_type == 'class':
                node_colors.append('#4CAF50')  # Green for classes
                node_sizes.append(2000)
            elif node_type == 'object_property':
                node_colors.append('#2196F3')  # Blue for object properties
                node_sizes.append(1500)
            else:
                node_colors.append('#FF9800')  # Orange for other
                node_sizes.append(1000)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8)
        
        # Draw edges with different styles
        subclass_edges = [(u, v) for u, v, d in G.edges(data=True) 
                         if d.get('edge_type') == 'subClassOf']
        domain_edges = [(u, v) for u, v, d in G.edges(data=True) 
                       if d.get('edge_type') == 'domain']
        range_edges = [(u, v) for u, v, d in G.edges(data=True) 
                      if d.get('edge_type') == 'range']
        
        # Draw subclass edges (solid arrows)
        if subclass_edges:
            nx.draw_networkx_edges(G, pos, edgelist=subclass_edges,
                                  edge_color='#333333', 
                                  arrows=True, 
                                  arrowsize=20,
                                  arrowstyle='->')
        
        # Draw domain edges (dashed)
        if domain_edges:
            nx.draw_networkx_edges(G, pos, edgelist=domain_edges,
                                  edge_color='#666666', 
                                  arrows=True, 
                                  arrowsize=15,
                                  arrowstyle='->',
                                  style='dashed')
        
        # Draw range edges (dotted)
        if range_edges:
            nx.draw_networkx_edges(G, pos, edgelist=range_edges,
                                  edge_color='#999999', 
                                  arrows=True, 
                                  arrowsize=15,
                                  arrowstyle='->',
                                  style='dotted')
        
        # Add labels
        labels = {}
        for node in G.nodes():
            label = G.nodes[node].get('label', self._get_short_name(node))
            # Truncate long labels
            if len(label) > 15:
                label = label[:12] + '...'
            labels[node] = label
        
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        # Create legend
        legend_elements = [
            mpatches.Patch(color='#4CAF50', label='Classes'),
            mpatches.Patch(color='#2196F3', label='Object Properties'),
            plt.Line2D([0], [0], color='#333333', label='subClassOf'),
            plt.Line2D([0], [0], color='#666666', linestyle='--', label='domain'),
            plt.Line2D([0], [0], color='#999999', linestyle=':', label='range')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
        
        # Remove axes
        plt.axis('off')
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
    
    def _get_short_name(self, uri: str) -> str:
        """Extract short name from URI."""
        if '#' in uri:
            return uri.split('#')[-1]
        elif '/' in uri:
            return uri.split('/')[-1]
        return uri
