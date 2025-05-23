## Current Directory Monitoring System

The OnToology application monitors a directory using the `DirectoryWatch` model and `DirectoryMonitor` class. Here's how it works:

### Supported File Types

The system monitors for ontology files with these extensions:

- `.owl` (Web Ontology Language)
- `.rdf` (Resource Description Framework)
- `.ttl` (Turtle)

### How to Add Directories for Monitoring

There are several ways to specify directories for monitoring:

#### 1. __Programmatically via Python Code__

You can use the `DirectoryMonitor` class directly:

```python
from OnToology.directory_monitor import get_monitor
from OnToology.models import OUser

# Get the monitor instance
monitor = get_monitor()

# Add a directory to monitor
user = OUser.objects.get(username='your_username')
directory_watch = monitor.add_directory(
    path='/path/to/your/ontology/directory',
    user=user,
    recursive=True,  # Monitor subdirectories too
    description='My ontology collection'
)
```

#### 2. __Database Direct Entry__

You can create `DirectoryWatch` entries directly in the database:

```python
from OnToology.models import DirectoryWatch, OUser

user = OUser.objects.get(username='your_username')
dir_watch = DirectoryWatch.objects.create(
    path='/path/to/your/ontology/directory',
    user=user,
    recursive=True,
    description='Description of this directory',
    active=True
)
```

#### 3. __Django Shell__

You can use Django's management shell:

```bash
python manage.py shell
```

Then run the Python code above.

### Key Configuration Options

When adding a directory, you can specify:

- __`path`__: The full filesystem path to monitor
- __`recursive`__: Whether to monitor subdirectories (True/False)
- __`description`__: A human-readable description
- __`active`__: Whether monitoring is currently enabled
- __`user`__: The user who owns this directory watch

### Starting the Monitor

To actually start monitoring, you need to run the directory monitoring service:

```python
from OnToology.directory_monitor import start_monitoring_service
start_monitoring_service()
```

Or run it as a daemon:

```python
python -c "from OnToology.directory_monitor import run_monitor_daemon; run_monitor_daemon()"
```

### What Happens When Files Are Detected

When the monitor detects changes to ontology files:

1. It validates the file has a supported extension (.owl, .rdf, .ttl)
2. It queues the file for processing via the `sqclient` message queue
3. The file gets processed by the `autoncore_directory.py` module
4. Various ontology tools are applied (validation, documentation generation, etc.)

### Current Limitations

- There's no web UI currently implemented for managing directory watches
- No REST API endpoints are exposed for directory management
- Directory management must be done programmatically or via Django shell
