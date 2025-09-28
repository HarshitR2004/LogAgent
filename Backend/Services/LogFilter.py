import asyncio
import json
import os
from datetime import datetime
from .MongoClient import MongoDBClient

class LogFilter:
    def __init__(self, status_filter=None, mongo_client=None):
        self.status_filter = status_filter or []
        self.mongo_client = mongo_client or MongoDBClient()
    
    def filter_logs(self, logs):
        
        if isinstance(logs, dict):
            logs = [logs]
        
        # Filter logs for ERROR and WARNING levels
        filtered_logs = []
        for log in logs:
            if isinstance(log, dict) and log.get('level') in ['ERROR', 'WARNING']:
                filtered_logs.append(log)
        
        # Save filtered logs to MongoDB
        if filtered_logs:
            self._save_filtered_logs(filtered_logs)
            
        return filtered_logs
    
    def _save_filtered_logs(self, filtered_logs):
        """Save filtered logs to MongoDB"""
        try:
            # Store logs in MongoDB
            self.mongo_client.store_logs(filtered_logs)
        except Exception as e:
            print(f"Error saving filtered logs to MongoDB: {e}")
    
    def get_filtered_logs(self, limit=1000):
        """Get filtered logs from MongoDB"""
        try:
            return self.mongo_client.get_filtered_logs(limit=limit)
        except Exception as e:
            print(f"Error retrieving filtered logs from MongoDB: {e}")
            return []
    
    def clear_filtered_logs(self):
        """
        Clear the filtered logs from MongoDB
        """
        try:
            return self.mongo_client.clear_logs()
        except Exception as e:
            print(f"Error clearing filtered logs: {e}")
            return False
