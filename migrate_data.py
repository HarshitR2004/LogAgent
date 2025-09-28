#!/usr/bin/env python3
"""
Migration script to move existing data from text/JSON files to MongoDB
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
import sys

# Add the Backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backend'))

from Backend.Services.MongoClient import MongoDBClient

class DataMigration:
    def __init__(self, data_folder_path: str, mongo_client: MongoDBClient):
        """
        Initialize migration with data folder path and MongoDB client
        
        Args:
            data_folder_path: Path to the data folder containing txt and json files
            mongo_client: MongoDB client instance
        """
        self.data_folder = Path(data_folder_path)
        self.mongo_client = mongo_client
        
    def parse_log_line(self, line: str) -> dict:
        """
        Parse a single log line from filteredLogs.txt
        
        Example format:
        [2025-09-28T00:52:19.997949] WARNING - User: brenda09 - IP: 171.120.238.251 - POST /api/v1/users - Status: 403 - Latency: 145ms
        Message: Processing POST request
        """
        # Skip empty lines
        if not line.strip():
            return None
            
        # Check if it's a message line
        if line.startswith('Message: '):
            return {'type': 'message', 'message': line[9:].strip()}
            
        # Parse log entry line
        log_pattern = r'\[([^\]]+)\]\s+(\w+)\s+-\s+User:\s+([^\s]+)\s+-\s+IP:\s+([^\s]+)\s+-\s+(\w+)\s+([^\s]+)\s+-\s+Status:\s+(\d+)\s+-\s+Latency:\s+(\d+)ms'
        
        match = re.match(log_pattern, line)
        if not match:
            return None
            
        timestamp_str, level, user, ip, method, endpoint, status_code, latency = match.groups()
        
        return {
            'type': 'log',
            'timestamp': timestamp_str,
            'level': level,
            'user': user,
            'ip': ip,
            'method': method,
            'endpoint': endpoint,
            'status_code': int(status_code),
            'latency_ms': int(latency)
        }
    
    def parse_logs_file(self, file_path: Path) -> list:
        """
        Parse the entire filteredLogs.txt file
        
        Returns:
            List of log dictionaries
        """
        logs = []
        current_log = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parsed = self.parse_log_line(line.strip())
                    
                    if not parsed:
                        continue
                        
                    if parsed['type'] == 'log':
                        # If we have a current log, save it first
                        if current_log:
                            logs.append(current_log)
                        current_log = parsed.copy()
                        del current_log['type']
                        
                    elif parsed['type'] == 'message' and current_log:
                        current_log['message'] = parsed['message']
                        
                # Don't forget the last log
                if current_log:
                    logs.append(current_log)
                    
        except Exception as e:
            print(f"Error parsing logs file: {e}")
            
        return logs
    
    def parse_metrics_line(self, line: str) -> dict:
        """
        Parse a single metrics line
        
        Example format:
        [2025-09-28T00:52:19.771178] CPU: 44.791163057821926% - Memory: 61.933314423910815% - Memory Used: 2539MB - Memory Total: 8192MB
        """
        # Skip session headers and empty lines
        if line.startswith('===') or not line.strip():
            return None
            
        # Parse metrics line
        metrics_pattern = r'\[([^\]]+)\]\s+CPU:\s+([\d.]+)%\s+-\s+Memory:\s+([\d.]+)%\s+-\s+Memory Used:\s+(\d+)MB\s+-\s+Memory Total:\s+(\d+)MB'
        
        match = re.match(metrics_pattern, line)
        if not match:
            return None
            
        timestamp_str, cpu_percent, memory_percent, memory_used, memory_total = match.groups()
        
        return {
            'timestamp': timestamp_str,
            'metric_type': 'system',
            'cpu_percent': float(cpu_percent),
            'memory_percent': float(memory_percent),
            'memory_used_mb': int(memory_used),
            'memory_total_mb': int(memory_total)
        }
    
    def parse_metrics_file(self, file_path: Path) -> list:
        """
        Parse the entire metrics.txt file
        
        Returns:
            List of metrics dictionaries
        """
        metrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parsed = self.parse_metrics_line(line.strip())
                    if parsed:
                        metrics.append(parsed)
                        
        except Exception as e:
            print(f"Error parsing metrics file: {e}")
            
        return metrics
    
    def parse_commits_file(self, file_path: Path) -> list:
        """
        Parse the commit.json file
        
        Returns:
            List of commit dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                commits = data.get('commits', [])
                
                # Add metadata to commits
                for commit in commits:
                    commit['timestamp'] = datetime.utcnow()  # Since original doesn't have timestamps
                    commit['repo_name'] = 'logagent'  # Default repo name
                    
                return commits
                
        except Exception as e:
            print(f"Error parsing commits file: {e}")
            return []
    
    def migrate_logs(self):
        """Migrate logs from filteredLogs.txt to MongoDB"""
        logs_file = self.data_folder / 'filteredLogs.txt'
        
        if not logs_file.exists():
            print(f"Logs file not found: {logs_file}")
            return False
            
        print("Parsing logs file...")
        logs = self.parse_logs_file(logs_file)
        
        if not logs:
            print("No logs found to migrate")
            return True
            
        print(f"Found {len(logs)} logs to migrate")
        
        try:
            # Clear existing logs
            self.mongo_client.clear_logs()
            print("Cleared existing logs from MongoDB")
            
            # Store logs in MongoDB
            ids = self.mongo_client.store_logs(logs)
            print(f"Successfully migrated {len(ids)} logs to MongoDB")
            return True
            
        except Exception as e:
            print(f"Error migrating logs: {e}")
            return False
    
    def migrate_metrics(self):
        """Migrate metrics from metrics.txt to MongoDB"""
        metrics_file = self.data_folder / 'metrics.txt'
        
        if not metrics_file.exists():
            print(f"Metrics file not found: {metrics_file}")
            return False
            
        print("Parsing metrics file...")
        metrics = self.parse_metrics_file(metrics_file)
        
        if not metrics:
            print("No metrics found to migrate")
            return True
            
        print(f"Found {len(metrics)} metrics to migrate")
        
        try:
            # Clear existing metrics
            self.mongo_client.clear_metrics()
            print("Cleared existing metrics from MongoDB")
            
            # Store metrics in MongoDB
            ids = self.mongo_client.store_metrics(metrics)
            print(f"Successfully migrated {len(ids)} metrics to MongoDB")
            return True
            
        except Exception as e:
            print(f"Error migrating metrics: {e}")
            return False
    
    def migrate_commits(self):
        """Migrate commits from commit.json to MongoDB"""
        commits_file = self.data_folder / 'commit.json'
        
        if not commits_file.exists():
            print(f"Commits file not found: {commits_file}")
            return False
            
        print("Parsing commits file...")
        commits = self.parse_commits_file(commits_file)
        
        if not commits:
            print("No commits found to migrate")
            return True
            
        print(f"Found {len(commits)} commits to migrate")
        
        try:
            # Clear existing commits
            self.mongo_client.clear_commits()
            print("Cleared existing commits from MongoDB")
            
            # Store commits in MongoDB
            ids = self.mongo_client.store_commits(commits)
            print(f"Successfully migrated {len(ids)} commits to MongoDB")
            return True
            
        except Exception as e:
            print(f"Error migrating commits: {e}")
            return False
    
    def migrate_all(self):
        """Migrate all data types"""
        print("=" * 50)
        print("Starting data migration to MongoDB")
        print("=" * 50)
        
        results = {
            'logs': self.migrate_logs(),
            'metrics': self.migrate_metrics(),
            'commits': self.migrate_commits()
        }
        
        print("\n" + "=" * 50)
        print("Migration Results:")
        print("=" * 50)
        
        for data_type, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            print(f"{data_type.title()}: {status}")
        
        # Show final statistics
        stats = self.mongo_client.get_collection_stats()
        print(f"\nFinal MongoDB Statistics:")
        for collection, count in stats.items():
            print(f"  {collection}: {count} documents")
        
        print("=" * 50)
        return all(results.values())


def main():
    """Main migration function"""
    # Get the project root directory
    project_root = Path(__file__).parent
    data_folder = project_root / 'data'
    
    print(f"Project root: {project_root}")
    print(f"Data folder: {data_folder}")
    
    if not data_folder.exists():
        print(f"Data folder not found: {data_folder}")
        return
    
    # Initialize MongoDB client
    try:
        with MongoDBClient() as mongo_client:
            print(f"Connected to MongoDB successfully")
            
            # Create migration instance
            migration = DataMigration(data_folder, mongo_client)
            
            # Run migration
            success = migration.migrate_all()
            
            if success:
                print("\n✅ Migration completed successfully!")
            else:
                print("\n❌ Migration completed with errors!")
                
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017")


if __name__ == "__main__":
    main()