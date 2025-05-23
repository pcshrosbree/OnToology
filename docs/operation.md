## OnToology Application Architecture

OnToology is a __multi-component distributed system__ that operates as both a __web application__ and a __background processing service__. Here's the complete breakdown:

### 1. __Primary Nature: Django Web Application__

OnToology is fundamentally a __Django-based web application__ that provides:

- __Web Interface__: Full-featured web UI for managing ontology repositories
- __REST API__: RESTful endpoints for programmatic access
- __User Authentication__: GitHub OAuth integration for user management
- __Repository Management__: Interface for adding/managing GitHub repositories

__Key Web Features:__

- User dashboard for repository management
- Configuration interface for ontology processing tools
- Progress tracking and status monitoring
- Publication management for ontologies
- Statistics and analytics views

### 2. __Background Processing Service__

The application includes a __message queue-based processing system__:

- __Queue System__: Uses `stiqueue` (Simple Task Queue) for asynchronous processing
- __Worker Processes__: Background workers that consume processing tasks
- __Multi-threading__: Handles concurrent ontology processing jobs
- __Directory Monitoring__: Real-time file system monitoring service

### 3. __Deployment Architecture__

#### __Web Server Component__

```javascript
Apache HTTP Server (mod_wsgi)
├── Django Web Application (OnToology)
├── Static File Serving (/media/)
├── Published Ontology Serving (/publish/)
└── WSGI Application Server
```

#### __Background Services__

```javascript
Message Queue System
├── SQClient (Message Producer/Consumer)
├── Directory Monitor Daemon
├── Processing Workers
└── GitHub Integration Service
```

### 4. __Service Components__

#### __A. Web Application Service__

- __Type__: WSGI-based Django application
- __Server__: Apache with mod_wsgi
- __Purpose__: User interface, API endpoints, repository management
- __Access__: HTTP/HTTPS web interface

#### __B. Directory Monitoring Service__

- __Type__: Python daemon process
- __Purpose__: Real-time monitoring of file system changes
- __Trigger__: Detects .owl/.rdf/.ttl file modifications
- __Integration__: Sends processing messages to queue

#### __C. Queue Processing Service__

- __Type__: Multi-threaded Python service

- __Purpose__: Asynchronous ontology processing

- __Components__:

  - Message queue server (stiqueue)
  - Worker processes for tool execution
  - GitHub integration for commits/PRs

#### __D. Tool Integration Services__

- __AR2DTool__: Diagram generation service
- __Widoco__: Documentation generation service
- __OOPS!__: Ontology evaluation service
- __owl2jsonld__: JSON-LD context generation
- __Themis__: Validation service

### 5. __Operational Modes__

#### __Production Deployment__

```bash
# Web application
apache2 start  # Serves Django web app via mod_wsgi

# Background services
python OnToology/sqclient.py  # Queue processing service
python OnToology/directory_monitor.py  # File monitoring daemon
```

#### __Development Mode__

```bash
# Django development server
python manage.py runserver

# Background processing (separate terminals)
python OnToology/sqclient.py
python -c "from OnToology.directory_monitor import run_monitor_daemon; run_monitor_daemon()"
```

#### __Console/CLI Usage__

```bash
# Direct processing
python OnToology/cmd.py updatestats

# Django management commands
python manage.py shell
python manage.py migrate
python manage.py collectstatic
```

### 6. __Integration Points__

#### __GitHub Integration__

- __Webhooks__: Receives push notifications from GitHub
- __OAuth__: User authentication via GitHub
- __API__: Creates forks, commits, pull requests
- __Repository Access__: Clones and processes repositories

#### __File System Integration__

- __Directory Monitoring__: Watches local directories for changes
- __Processing Workspace__: Temporary directories for tool execution
- __Output Storage__: Generated files stored in repository structure

#### __External Tools__

- __Java Applications__: Widoco, AR2DTool, owl2jsonld
- __System Tools__: Git, Graphviz (dot), Apache
- __Python Libraries__: Django, PyGithub, watchdog

### 7. __Scalability Architecture__

The system is designed for __horizontal scaling__:

- __Web Tier__: Multiple Django instances behind load balancer
- __Processing Tier__: Multiple queue workers for parallel processing
- __Storage Tier__: Distributed file storage and database
- __Queue Tier__: Clustered message queue system

### 8. __Service Dependencies__

```javascript
OnToology System
├── Web Application (Django + Apache)
├── Database (SQLite/PostgreSQL/MySQL)
├── Message Queue (stiqueue)
├── File System (Local/NFS)
├── GitHub API
├── Java Runtime (for tools)
└── System Tools (Git, Graphviz)
```

## Summary

OnToology is a __hybrid application__ that combines:

1. __Web Application__: Django-based interface for user interaction
2. __Background Services__: Daemon processes for file monitoring and processing
3. __Message Queue System__: Asynchronous task processing
4. __Tool Integration Platform__: Orchestrates multiple ontology processing tools

It operates as a __distributed service architecture__ where the web interface handles user interactions while background services perform the heavy computational work of ontology processing. The system can run as a single-server deployment or be distributed across multiple servers for scalability.

The application is designed to be __event-driven__ (responding to GitHub webhooks and file system changes) and __asynchronous__ (using message queues for processing), making it suitable for handling multiple repositories and users simultaneously.
