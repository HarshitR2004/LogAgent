from datetime import datetime
import os
from .MongoClient import MongoDBClient

class MetricsCollector:
    def __init__(self, mongo_client=None):
        self.mongo_client = mongo_client or MongoDBClient()

    def collect_metric(self, metrics):
        """Collect and store a metric"""
        if isinstance(metrics, dict):
            metrics = [metrics]
            
        collected_metrics = []   
        for metric in metrics:
            if isinstance(metric, dict) and metric is not None:
                collected_metrics.append(metric)
        if collected_metrics:
            self.store_metrics(collected_metrics)
        
    def store_metrics(self, metrics):
        """Store metrics to MongoDB"""
        try:
            # Ensure all metrics have required fields
            for metric in metrics:
                if 'metric_type' not in metric:
                    metric['metric_type'] = 'system'
                if 'timestamp' not in metric:
                    metric['timestamp'] = datetime.utcnow()
            
            # Store in MongoDB
            self.mongo_client.store_metrics(metrics)
                
        except Exception as e:
            print(f"Error storing metrics to MongoDB: {e}")
    
    def get_metrics(self, limit=1000, metric_type=None):
        """Get metrics from MongoDB"""
        try:
            return self.mongo_client.get_metrics(limit=limit, metric_type=metric_type)
        except Exception as e:
            print(f"Error retrieving metrics from MongoDB: {e}")
            return []
    
    def clear_metrics(self):
        """Clear metrics from MongoDB"""
        try:
            return self.mongo_client.clear_metrics()
        except Exception as e:
            print(f"Error clearing metrics: {e}")
            return False