# OnToology Local

A standalone command-line tool for generating comprehensive ontology documentation locally. This tool provides the core functionality of OnToology as a local application that generates HTML documentation, diagrams, evaluations, and more from local ontology files.

## Features

- **HTML Documentation**: Generate comprehensive, browsable HTML documentation for ontologies
- **Visual Diagrams**: Create network diagrams showing ontology structure and relationships
- **Quality Evaluation**: Integrate with OOPS! service for ontology pitfall detection
- **JSON-LD Context**: Generate JSON-LD context files for semantic web applications
- **Validation Reports**: Perform basic ontology validation and quality checks
- **Local Output**: All outputs are generated as local HTML files that can be browsed offline

## Installation

1. **Clone or download this directory**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python cli.py --help
   ```

## Usage

### Basic Usage

Generate documentation for all ontologies in a directory:

```bash
python cli.py --input /path/to/ontologies --output /path/to/output
```

### Advanced Usage

```bash
# Generate only documentation and diagrams
python cli.py -i ./ontologies -o ./docs --tools doc,diagrams

# Use custom configuration
python cli.py -i ./ontologies -o ./docs --config config.yaml

# Enable verbose output
python cli.py -i ./ontologies -o ./docs --verbose

# Process ontologies in parallel (experimental)
python cli.py -i ./ontologies -o ./docs --parallel
```

### Command Line Options

- `--input, -i`: Input directory containing ontology files (.owl, .rdf, .ttl)
- `--output, -o`: Output directory for generated documentation
- `--tools, -t`: Comma-separated list of tools to run (default: all)
  - `doc`: HTML documentation
  - `eval`: OOPS! evaluation
  - `diagrams`: Visual diagrams
  - `jsonld`: JSON-LD context
  - `validation`: Basic validation
- `--config, -c`: Configuration file (YAML format)
- `--verbose, -v`: Enable verbose output
- `--parallel, -p`: Process ontologies in parallel

## Supported File Formats

- OWL files (`.owl`)
- RDF/XML files (`.rdf`)
- Turtle files (`.ttl`)
- N3 files (`.n3`)
- N-Triples files (`.nt`)

## Output Structure

The tool generates a flat directory structure optimized for local browsing:

```
output/
├── index.html                    # Main index page
├── assets/
│   ├── css/style.css             # Styling
│   └── js/script.js              # JavaScript
├── ontology1_documentation.html  # Documentation pages
├── ontology1_evaluation.html     # Evaluation reports
├── ontology1_validation.html     # Validation reports
├── ontology1_diagram.png         # Visual diagrams
├── ontology1_context.jsonld      # JSON-LD contexts
└── ...
```

## Configuration

Create a `config.yaml` file to customize the behavior:

```yaml
# Documentation settings
documentation:
  languages: ["en"]
  include_diagrams: true

# Evaluation settings  
evaluation:
  oops_url: "http://oops.linkeddata.es/rest"
  timeout: 30

# Diagram settings
diagrams:
  format: "png"
  include_properties: true
  max_nodes: 50

# JSON-LD settings
jsonld:
  include_standard_prefixes: true

# Validation settings
validation:
  check_consistency: true
  check_completeness: true
```

## Examples

### Example 1: Basic Documentation Generation

```bash
# Generate documentation for ontologies in the current directory
python cli.py -i . -o ./documentation

# Open the generated documentation
open documentation/index.html
```

### Example 2: Custom Tool Selection

```bash
# Generate only documentation and validation reports
python cli.py -i ./ontologies -o ./output --tools doc,validation
```

### Example 3: Using Configuration File

```bash
# Use custom settings from config file
python cli.py -i ./ontologies -o ./output -c my-config.yaml -v
```

## Dependencies

- **Python 3.7+**
- **RDFLib**: RDF parsing and manipulation
- **Jinja2**: HTML template rendering
- **Click**: Command-line interface
- **PyYAML**: Configuration file parsing
- **Requests**: HTTP requests for OOPS! service
- **NetworkX**: Graph algorithms for diagrams
- **Matplotlib**: Diagram generation

## Architecture

The tool is organized into several modules:

- **CLI (`cli.py`)**: Command-line interface and main orchestration
- **Utils**: Ontology discovery, parsing, and output management
- **Processors**: Individual tools for documentation, evaluation, etc.

### Key Components

1. **OntologyDiscovery**: Finds ontology files in directory trees
2. **OntologyParser**: Parses ontologies and extracts metadata using RDFLib
3. **OutputManager**: Manages output directory and generates index pages
4. **Processors**: Modular processors for different output types
   - DocumentationProcessor: HTML documentation
   - EvaluationProcessor: OOPS! integration
   - DiagramProcessor: Visual diagrams
   - JsonLdProcessor: JSON-LD contexts
   - ValidationProcessor: Basic validation

## Comparison with Original OnToology

| Feature | OnToology (Web) | OnToology Local |
|---------|----------------|-----------------|
| **Deployment** | Web service | Local command-line tool |
| **Input** | GitHub repositories | Local files |
| **Output** | GitHub pages | Local HTML files |
| **Dependencies** | GitHub, web server | Python environment |
| **Offline Use** | No | Yes |
| **Customization** | Limited | Full control |
| **Integration** | GitHub workflow | Local/CI pipeline |

## Troubleshooting

Sanity check: `cd ontoology-local && python example.py`

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

2. **OOPS! Service Unavailable**: The evaluation processor will generate a fallback report if the OOPS! service is unreachable

3. **Large Ontologies**: For very large ontologies, consider:
   - Reducing `max_nodes` in diagram configuration
   - Using `--tools` to skip diagram generation
   - Increasing timeout values

4. **Memory Issues**: For processing many large ontologies:
   - Process ontologies individually
   - Avoid using `--parallel` flag
   - Increase system memory

### Getting Help

- Check the verbose output with `-v` flag
- Review the generated log messages
- Ensure input files are valid RDF/OWL

## Contributing

This tool is designed to be modular and extensible. To add new processors:

1. Create a new processor class in `processors/`
2. Implement the `process()` method
3. Add the processor to the CLI initialization

## License

This tool maintains compatibility with the original OnToology project licensing.

## Acknowledgments

This local version is inspired by and maintains compatibility with the original OnToology project by the Ontology Engineering Group at Universidad Politécnica de Madrid.
