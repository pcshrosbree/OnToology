## Application Outputs

OnToology processes ontology files (.owl, .rdf, .ttl) and generates several types of outputs using different tools. Here's what gets generated and where:

### 1. __Diagrams (AR2DTool)__

- __Output__: Visual diagrams of the ontology structure

- __Format__: PNG files and GraphML files

- __Location__: `OnToology/{ontology-path}/diagrams/`

- __Specific files__:

  - `{ontology-name}.png.graphml`
  - Various diagram types based on configuration

### 2. __Documentation (Widoco)__

- __Output__: HTML documentation for the ontology

- __Format__: HTML files, CSS, JavaScript

- __Location__: `OnToology/{ontology-path}/documentation/`

- __Key files__:

  - `index.html` (main documentation page)
  - `index-{language}.html` (language-specific versions)
  - `.htaccess` (for content negotiation)
  - Various supporting files for the documentation website

### 3. __Evaluation Reports (OOPS!)__

- __Output__: Ontology evaluation and pitfall detection
- __Format__: HTML report
- __Location__: `OnToology/{ontology-path}/evaluation/`
- __Key file__: `oopsEval.html`

### 4. __JSON-LD Context (owl2jsonld)__

- __Output__: JSON-LD context for the ontology
- __Format__: JSON-LD file
- __Location__: `OnToology/{ontology-path}/context/`
- __Key file__: `context.jsonld`

### 5. __Validation Results (Themis)__

- __Output__: Ontology validation test results

- __Format__: TSV (Tab-Separated Values) and text files

- __Location__: `OnToology/{ontology-path}/validation/`

- __Key files__:

  - `results.tsv` (validation results)
  - `tests.txt` (test definitions)

### 6. __Configuration Files__

- __Output__: Tool configuration for each ontology
- __Format__: INI-style configuration file
- __Location__: `OnToology/{ontology-path}/OnToology.cfg`
- __Purpose__: Controls which tools are enabled and their settings

## Output Directory Structure

For an ontology located at `path/to/myontology.owl`, the complete output structure would be:

```javascript
OnToology/
└── path/
    └── to/
        └── myontology.owl/
            ├── OnToology.cfg
            ├── diagrams/
            │   └── [diagram files]
            ├── documentation/
            │   ├── index.html
            │   ├── .htaccess
            │   └── [other doc files]
            ├── evaluation/
            │   └── oopsEval.html
            ├── context/
            │   └── context.jsonld
            └── validation/
                ├── results.tsv
                └── tests.txt
```

## Where Outputs Are Stored

### Local Processing

- __Base Directory__: Defined by `github_repos_dir` environment variable
- __Working Directory__: `{base_dir}/{user}/OnToology/{ontology-path}/`
- __Temporary Processing__: Files are processed in cloned repository directories

### GitHub Integration

- __Repository Storage__: All outputs are committed back to the source GitHub repository
- __Branch__: Typically committed to the same branch as the source ontology
- __Pull Requests__: Changes are submitted via pull requests for review

### Published Ontologies

- __Publication Directory__: Defined by `publish_dir` environment variable
- __W3ID Integration__: Published ontologies get redirects set up for w3id.org
- __GitHub Pages__: Documentation is served via GitHub Pages at `{username}.github.io/{repo}/OnToology/{ontology-path}/documentation/`

## Output Processing Flow

1. __Detection__: Directory monitor detects changes to .owl/.rdf/.ttl files
2. __Processing__: Each enabled tool processes the ontology and generates outputs
3. __Validation__: Outputs are verified to ensure they were generated successfully
4. __Commit__: All outputs are committed to the repository
5. __Pull Request__: Changes are submitted via pull request
6. __Publication__: If configured, ontologies can be published with persistent URIs

## Configuration Control

Each ontology can have its own `OnToology.cfg` file that controls:

- Which tools are enabled/disabled
- Tool-specific settings (e.g., documentation languages)
- Output preferences

The default configuration enables:

- __Widoco__ (documentation): ✅ Enabled
- __OOPS!__ (evaluation): ✅ Enabled
- __owl2jsonld__ (JSON-LD context): ✅ Enabled
- __AR2DTool__ (diagrams): ❌ Disabled by default
- __Themis__ (validation): ❌ Disabled by default

This comprehensive output system ensures that ontologies are well-documented, validated, and ready for publication with proper content negotiation and persistent identifiers.
