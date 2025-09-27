import asyncio
import json
import os
from datetime import datetime

class LogFilter:
    def __init__(self, status_filter=None, es_host="http://localhost:9200", index_name="logs"):
        self.status_filter = status_filter or []
        # Set path to data folder in project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.filtered_logs_file = os.path.join(project_root, "data", "filteredLogs.txt")

    
    def filter_logs(self, logs):
        
        if isinstance(logs, dict):
            logs = [logs]
        
        # Filter logs for ERROR and WARNING levels
        filtered_logs = []
        for log in logs:
            if isinstance(log, dict) and log.get('level') in ['ERROR', 'WARNING']:
                filtered_logs.append(log)
        
        # Save filtered logs to file
        if filtered_logs:
            self._save_filtered_logs(filtered_logs)
            
        return filtered_logs
    
    def _save_filtered_logs(self, filtered_logs):
    
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.filtered_logs_file)
            
            with open(file_path, 'a', encoding='utf-8') as f:
                for log in filtered_logs:
                    # Format log entry for better readability
                    log_entry = (f"[{log.get('timestamp', 'N/A')}] "
                               f"{log.get('level', 'UNKNOWN')} - "
                               f"User: {log.get('user', 'N/A')} - "
                               f"IP: {log.get('ip', 'N/A')} - "
                               f"{log.get('method', 'N/A')} {log.get('endpoint', 'N/A')} - "
                               f"Status: {log.get('status_code', 'N/A')} - "
                               f"Latency: {log.get('latency_ms', 'N/A')}ms\n"
                               f"Message: {log.get('message', 'N/A')}\n")
                    f.write(log_entry)
                                
        except Exception as e:
            print(f"Error saving filtered logs: {e}")
    
    def clear_filtered_logs(self):
        """
        Clear the filtered logs file
        """
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.filtered_logs_file)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error clearing filtered logs: {e}")
        return False
