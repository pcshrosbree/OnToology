This is a Django-based system for collaborative ontology development that generates documentation, diagrams, and validation reports for OWL/RDF ontologies. Currently, the system is designed to work with GitHub integration and publishes documentation to GitHub Pages.

To change this application to output documentation as local HTML files that can be browsed from the local file system:

## Current Documentation Generation Process

The application uses __Widoco__ (a documentation generator for ontologies) as its primary documentation tool, which:

- Generates HTML documentation in the `OnToology/{ontology-path}/documentation/` directory
- Creates `index.html` files and supporting assets (CSS, JS)
- Generates `.htaccess` files for content negotiation
- Currently publishes to GitHub Pages with redirects

## Proposed Plan for Local HTML Output

### 1. __Modify the Widoco Integration__ (`Integrator/widoco.py`)

- Remove GitHub-specific publishing logic
- Modify the output directory structure to be more suitable for local browsing
- Ensure all generated HTML files use relative paths instead of absolute URLs
- Remove `.htaccess` generation (not needed for local file system)

### 2. __Create a Local Documentation Generator__

- Add a new command-line interface or management command
- Allow users to specify input ontology files and output directory
- Generate a complete, self-contained documentation package
- Include all necessary CSS, JavaScript, and media files

### 3. __Modify File Path Handling__

- Update path generation to work with local file system structure
- Ensure cross-references between files work with `file://` protocol
- Make all asset references relative

### 4. __Add a Local Server Option__ (Optional)

- Include a simple HTTP server option for better local browsing
- This would handle content negotiation that `.htaccess` normally provides

### 5. __Create Documentation Packaging__

- Bundle all generated documentation into a single directory
- Include an index page that lists all processed ontologies
- Ensure the package is portable and self-contained

## Key Files That Would Need Modification

1. __`Integrator/widoco.py`__ - Core documentation generation
2. __`OnToology/autoncore.py`__ - Main processing logic
3. __`manage.py`__ - Add new management commands
4. __Configuration files__ - Add local output options

This plan would essentially create a "local mode" for OnToology that bypasses all the GitHub integration and produces documentation that can be opened directly in a web browser from the local file system.

## Detailed Implementation Plan

### 1. __Create Standalone CLI Tool Structure__

```javascript
ontoology-local/
├── cli.py                 # Main command-line interface
├── processors/
│   ├── __init__.py
│   ├── documentation.py   # Pure Python HTML doc generator
│   ├── evaluation.py      # OOPS! integration
│   ├── diagrams.py        # Python-based diagram generation
│   ├── jsonld.py          # JSON-LD context generation
│   └── validation.py      # Validation testing
├── templates/             # HTML templates for documentation
├── assets/               # CSS, JS, and other static files
└── utils/
    ├── __init__.py
    ├── ontology_parser.py # RDF/OWL parsing utilities
    └── file_utils.py      # File handling utilities
```

### 2. __Replace Java Dependencies with Python Alternatives__

__For Widoco (Documentation Generation):__

- Use __rdflib__ for ontology parsing
- Use __Jinja2__ for HTML template generation
- Create custom documentation templates similar to Widoco's output
- Generate index.html, ontology metadata, and cross-references

__For AR2DTool (Diagrams):__

- Use __networkx__ + __matplotlib__ or __graphviz__ for diagram generation
- Parse ontology structure to create class/property diagrams
- Generate PNG/SVG outputs

__For owl2jsonld:__

- Use __rdflib__ to parse ontology and generate JSON-LD context
- This is already mostly Python-compatible

### 3. __Command-Line Interface Design__

```bash
# Basic usage
ontoology-local --input /path/to/ontologies --output /path/to/docs

# With specific tools
ontoology-local --input /path/to/ontologies --output /path/to/docs --tools doc,eval,diagrams

# With configuration
ontoology-local --input /path/to/ontologies --output /path/to/docs --config config.yaml
```

### 4. __Core Processing Pipeline__

1. __Discovery__: Scan input directory for .owl, .rdf, .ttl files
2. __Parsing__: Use rdflib to parse each ontology
3. __Processing__: Run each enabled tool on each ontology
4. __Output__: Generate flat structure with all results

### 5. __Output Directory Structure__

```javascript
output/
├── index.html                    # Main index listing all ontologies
├── ontology1_documentation.html  # Flattened naming scheme
├── ontology1_evaluation.html
├── ontology1_diagram.png
├── ontology1_context.jsonld
├── ontology1_validation.html
├── ontology2_documentation.html
├── ontology2_evaluation.html
├── ...
├── assets/                       # Shared CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
└── data/                         # Raw data files if needed
```

### 6. __Pure Python Tool Implementations__

__Documentation Generator:__

- Parse ontology metadata (title, description, authors, etc.)
- Extract classes, properties, individuals
- Generate cross-reference tables
- Create HTML with embedded CSS for offline viewing

__Diagram Generator:__

- Use ontology structure to build networkx graph
- Generate class hierarchy diagrams
- Create property relationship diagrams
- Export as PNG/SVG with matplotlib or graphviz

__Evaluation Integration:__

- Keep OOPS! web service integration (it's already HTTP-based)
- Add local validation rules as Python functions
- Generate HTML reports

### 7. __Configuration System__

YAML configuration file to control:

- Which tools to run
- Output formats
- Template customization
- Tool-specific settings

## Implementation Challenges & Solutions

__Challenge 1: Replacing Widoco's sophisticated HTML generation__

- __Solution__: Create comprehensive Jinja2 templates that replicate Widoco's functionality
- Use rdflib to extract all the same metadata Widoco uses

__Challenge 2: Diagram generation without AR2DTool__

- __Solution__: Use networkx to model ontology relationships and matplotlib/graphviz for rendering
- May not be as sophisticated initially, but can be enhanced

__Challenge 3: Maintaining compatibility with existing configurations__

- __Solution__: Create a configuration converter that reads existing OnToology.cfg files

## Next Steps

Would you like me to proceed with implementing this plan? I can start by:

1. Creating the basic CLI structure and argument parsing
2. Implementing the ontology discovery and parsing logic
3. Building the pure Python documentation generator
4. Adding the other tool processors
5. Creating the output generation system

The tool would be completely self-contained and not require any Java dependencies or GitHub integration.
