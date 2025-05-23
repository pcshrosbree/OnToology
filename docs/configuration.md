## OnToology.cfg Configuration File Documentation

The `OnToology.cfg` file is an INI-style configuration file that controls which tools are executed for each ontology and their specific settings. This file should be placed in the `OnToology/{ontology-path}/` directory alongside the generated outputs.

### File Location

```javascript
OnToology/{path-to-ontology}/OnToology.cfg
```

For example, if your ontology is at `src/myontology.owl`, the configuration file should be at:

```javascript
OnToology/src/myontology.owl/OnToology.cfg
```

### Configuration Format

The configuration file uses INI format with sections for each tool. Here's the complete structure:

```ini
[ar2dtool]
enable = false

[widoco]
enable = true
languages = en
webvowl = false

[oops]
enable = true

[owl2jsonld]
enable = true

[themis]
enable = false
```

### Tool Sections

#### 1. __[ar2dtool] - Diagram Generation__

Generates visual diagrams of the ontology structure using AR2DTool.

__Options:__

- `enable` (boolean): Whether to generate diagrams

  - `true` - Generate diagrams
  - `false` - Skip diagram generation (default)

__Output:__ PNG and GraphML files in `OnToology/{ontology-path}/diagrams/`

#### 2. __[widoco] - Documentation Generation__

Generates HTML documentation using Widoco (WIzard for DOCumenting Ontologies).

__Options:__

- `enable` (boolean): Whether to generate documentation

  - `true` - Generate documentation (default)
  - `false` - Skip documentation generation

- `languages` (list): Languages for documentation generation

  - Format: Comma-separated language codes

  - Default: `en` (English)

  - Examples:

    - `en` (English only)
    - `en,es` (English and Spanish)
    - `en,es,fr,de` (Multiple languages)

  - Supported languages: `en`, `es`, `fr`, `de`, `it`, `pt`, etc.

- `webvowl` (boolean): Whether to include WebVOWL visualization

  - `true` - Include interactive WebVOWL diagrams
  - `false` - Skip WebVOWL generation (default)

__Output:__ HTML documentation in `OnToology/{ontology-path}/documentation/`

#### 3. __[oops] - Ontology Evaluation__

Runs OOPS! (OntOlogy Pitfall Scanner) to detect common ontology pitfalls.

__Options:__

- `enable` (boolean): Whether to run evaluation

  - `true` - Generate evaluation report (default)
  - `false` - Skip evaluation

__Output:__ HTML evaluation report in `OnToology/{ontology-path}/evaluation/`

#### 4. __[owl2jsonld] - JSON-LD Context__

Generates JSON-LD context files for the ontology.

__Options:__

- `enable` (boolean): Whether to generate JSON-LD context

  - `true` - Generate JSON-LD context (default)
  - `false` - Skip JSON-LD generation

__Output:__ JSON-LD context file in `OnToology/{ontology-path}/context/`

#### 5. __[themis] - Ontology Validation__

Runs Themis validation tests on the ontology.

__Options:__

- `enable` (boolean): Whether to run validation

  - `true` - Run validation tests
  - `false` - Skip validation (default)

__Output:__ Validation results in `OnToology/{ontology-path}/validation/`

### Default Configuration

If no `OnToology.cfg` file exists, OnToology will create one with these default settings:

```ini
[ar2dtool]
enable = false

[widoco]
enable = true
languages = en
webvowl = false

[oops]
enable = true

[owl2jsonld]
enable = true

[themis]
enable = false
```

### Configuration Examples

#### Minimal Configuration (Documentation Only)

```ini
[ar2dtool]
enable = false

[widoco]
enable = true
languages = en
webvowl = false

[oops]
enable = false

[owl2jsonld]
enable = false

[themis]
enable = false
```

#### Full Processing with Multiple Languages

```ini
[ar2dtool]
enable = true

[widoco]
enable = true
languages = en,es,fr
webvowl = true

[oops]
enable = true

[owl2jsonld]
enable = true

[themis]
enable = true
```

#### Evaluation and Documentation Focus

```ini
[ar2dtool]
enable = false

[widoco]
enable = true
languages = en,es
webvowl = true

[oops]
enable = true

[owl2jsonld]
enable = true

[themis]
enable = true
```

### Configuration Management

#### Automatic Creation

- OnToology automatically creates `OnToology.cfg` with default settings if it doesn't exist
- The file is created during the first processing of an ontology

#### Manual Configuration

- You can manually create or edit the `OnToology.cfg` file in your repository
- Changes take effect on the next processing run
- The configuration file is committed back to your repository

#### Per-Ontology Configuration

- Each ontology can have its own configuration file
- Different ontologies in the same repository can have different tool settings
- Configuration is inherited from the ontology's specific directory

### Language Codes Reference

Common language codes for the `languages` option in Widoco:

- `en` - English
- `es` - Spanish (Español)
- `fr` - French (Français)
- `de` - German (Deutsch)
- `it` - Italian (Italiano)
- `pt` - Portuguese (Português)
- `nl` - Dutch (Nederlands)
- `ru` - Russian (Русский)

### Best Practices

1. __Start with defaults__: Use the default configuration initially, then customize as needed
2. __Enable diagrams selectively__: AR2DTool can be resource-intensive, enable only when needed
3. __Multiple languages__: Only specify languages you actually need to reduce processing time
4. __WebVOWL consideration__: Enable WebVOWL for complex ontologies where visualization helps
5. __Validation for quality__: Enable Themis for production ontologies to ensure quality
6. __Version control__: Commit your `OnToology.cfg` files to track configuration changes

This configuration system provides fine-grained control over ontology processing while maintaining sensible defaults for quick setup.
