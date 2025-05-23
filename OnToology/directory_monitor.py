#!/usr/bin/python
#
# Copyright 2012-2013 Ontology Engineering Group, Universidad Politécnica de Madrid, Spain
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import time
import logging
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.utils import timezone
from OnToology.models import DirectoryWatch, Repo, OUser
from OnToology import sqclient
import json

# Supported ontology file extensions
ONTOLOGY_EXTENSIONS = ['.owl', '.rdf', '.ttl']

logger = logging.getLogger(__name__)


class OntologyFileHandler(FileSystemEventHandler):
    """Handles file system events for ontology files"""
    
    def __init__(self, directory_watch):
        self.directory_watch = directory_watch
        self.processed_files = set()  # Track recently processed files to avoid duplicates
        
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'modified')
    
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_event(event.src_path, 'created')
    
    def _handle_file_event(self, file_path, event_type):
        """Process ontology file events"""
        try:
            # Check if it's an ontology file
            if not self._is_ontology_file(file_path):
                return
                
            # Avoid processing the same file multiple times in quick succession
            file_key = f"{file_path}_{event_type}_{int(time.time())}"
            if file_key in self.processed_files:
                return
                
            self.processed_files.add(file_key)
            
            # Clean up old entries (keep only last 100)
            if len(self.processed_files) > 100:
                self.processed_files = set(list(self.processed_files)[-50:])
            
            logger.info(f"Detected {event_type} ontology file: {file_path}")
            
            # Get relative path from the monitored directory
            rel_path = os.path.relpath(file_path, self.directory_watch.path)
            
            # Send to processing queue
            self._queue_for_processing(rel_path, event_type)
            
        except Exception as e:
            logger.error(f"Error handling file event for {file_path}: {str(e)}")
    
    def _is_ontology_file(self, file_path):
        """Check if the file is an ontology file"""
        return any(file_path.lower().endswith(ext) for ext in ONTOLOGY_EXTENSIONS)
    
    def _queue_for_processing(self, rel_path, event_type):
        """Queue the file for processing"""
        try:
            # Create a processing message
            message = {
                'action': 'directory_magic',
                'directory_watch_id': self.directory_watch.id,
                'file_path': rel_path,
                'event_type': event_type,
                'created': str(timezone.now()),
            }
            
            # Send to queue
            sqclient.send(message)
            logger.info(f"Queued {rel_path} for processing")
            
        except Exception as e:
            logger.error(f"Error queuing file {rel_path}: {str(e)}")


class DirectoryMonitor:
    """Main directory monitoring service"""
    
    def __init__(self):
        self.observers = {}
        self.running = False
        
    def start_monitoring(self):
        """Start monitoring all configured directories"""
        try:
            self.running = True
            
            # Get all active directory watches
            directory_watches = DirectoryWatch.objects.filter(active=True)
            
            for dir_watch in directory_watches:
                self._start_watching_directory(dir_watch)
                
            logger.info(f"Started monitoring {len(directory_watches)} directories")
            
        except Exception as e:
            logger.error(f"Error starting directory monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Stop monitoring all directories"""
        try:
            self.running = False
            
            for observer in self.observers.values():
                observer.stop()
                observer.join()
                
            self.observers.clear()
            logger.info("Stopped all directory monitoring")
            
        except Exception as e:
            logger.error(f"Error stopping directory monitoring: {str(e)}")
    
    def _start_watching_directory(self, directory_watch):
        """Start watching a specific directory"""
        try:
            if not os.path.exists(directory_watch.path):
                logger.warning(f"Directory does not exist: {directory_watch.path}")
                return
                
            # Create event handler
            event_handler = OntologyFileHandler(directory_watch)
            
            # Create observer
            observer = Observer()
            observer.schedule(
                event_handler, 
                directory_watch.path, 
                recursive=directory_watch.recursive
            )
            
            # Start observer
            observer.start()
            self.observers[directory_watch.id] = observer
            
            logger.info(f"Started watching directory: {directory_watch.path}")
            
        except Exception as e:
            logger.error(f"Error watching directory {directory_watch.path}: {str(e)}")
    
    def add_directory(self, path, user, recursive=True, description=""):
        """Add a new directory to monitor"""
        try:
            # Validate path
            if not os.path.exists(path):
                raise ValueError(f"Directory does not exist: {path}")
                
            # Check if already being monitored
            existing = DirectoryWatch.objects.filter(path=path, active=True).first()
            if existing:
                raise ValueError(f"Directory already being monitored: {path}")
            
            # Create directory watch
            dir_watch = DirectoryWatch.objects.create(
                path=path,
                user=user,
                recursive=recursive,
                description=description,
                active=True
            )
            
            # Start watching if monitor is running
            if self.running:
                self._start_watching_directory(dir_watch)
                
            logger.info(f"Added directory watch: {path}")
            return dir_watch
            
        except Exception as e:
            logger.error(f"Error adding directory {path}: {str(e)}")
            raise
    
    def remove_directory(self, directory_watch_id):
        """Remove a directory from monitoring"""
        try:
            dir_watch = DirectoryWatch.objects.get(id=directory_watch_id)
            
            # Stop observer if running
            if directory_watch_id in self.observers:
                observer = self.observers[directory_watch_id]
                observer.stop()
                observer.join()
                del self.observers[directory_watch_id]
            
            # Deactivate the watch
            dir_watch.active = False
            dir_watch.save()
            
            logger.info(f"Removed directory watch: {dir_watch.path}")
            
        except Exception as e:
            logger.error(f"Error removing directory watch {directory_watch_id}: {str(e)}")
            raise
    
    def scan_directory_now(self, directory_watch_id):
        """Manually scan a directory for ontology files"""
        try:
            dir_watch = DirectoryWatch.objects.get(id=directory_watch_id)
            
            if not os.path.exists(dir_watch.path):
                raise ValueError(f"Directory does not exist: {dir_watch.path}")
            
            ontology_files = []
            
            # Scan for ontology files
            if dir_watch.recursive:
                for root, dirs, files in os.walk(dir_watch.path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in ONTOLOGY_EXTENSIONS):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, dir_watch.path)
                            ontology_files.append(rel_path)
            else:
                for file in os.listdir(dir_watch.path):
                    if os.path.isfile(os.path.join(dir_watch.path, file)):
                        if any(file.lower().endswith(ext) for ext in ONTOLOGY_EXTENSIONS):
                            ontology_files.append(file)
            
            # Queue all found files for processing
            for rel_path in ontology_files:
                message = {
                    'action': 'directory_magic',
                    'directory_watch_id': dir_watch.id,
                    'file_path': rel_path,
                    'event_type': 'manual_scan',
                    'created': str(timezone.now()),
                }
                sqclient.send(message)
            
            logger.info(f"Queued {len(ontology_files)} files from manual scan of {dir_watch.path}")
            return ontology_files
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory_watch_id}: {str(e)}")
            raise


# Global monitor instance
_monitor = None


def get_monitor():
    """Get the global directory monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = DirectoryMonitor()
    return _monitor


def start_monitoring_service():
    """Start the directory monitoring service"""
    monitor = get_monitor()
    monitor.start_monitoring()


def stop_monitoring_service():
    """Stop the directory monitoring service"""
    monitor = get_monitor()
    monitor.stop_monitoring()


def run_monitor_daemon():
    """Run the monitor as a daemon process"""
    try:
        logger.info("Starting OnToology Directory Monitor")
        start_monitoring_service()
        
        # Keep the daemon running
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Monitor daemon error: {str(e)}")
    finally:
        stop_monitoring_service()
        logger.info("Directory monitor stopped")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the daemon
    run_monitor_daemon()
