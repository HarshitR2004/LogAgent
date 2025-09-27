from datetime import datetime
import os

class MetricsCollector:
    def __init__(self):
        # Set path to data folder in project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.metrics_file = os.path.join(project_root, "data", "metrics.txt")

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
        """Store metric to file"""
        try:
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Metrics Session - {datetime.now().isoformat()} ===\n")
                for metric in metrics:
                    # Format metric entry as a string
                    metric_entry = (f"[{metric.get('timestamp', 'N/A')}] "
                                  f"CPU: {metric.get('cpu_percent', 'N/A')}% - "
                                  f"Memory: {metric.get('memory_percent', 'N/A')}% - "
                                  f"Memory Used: {metric.get('memory_used_mb', 'N/A')}MB - "
                                  f"Memory Total: {metric.get('memory_total_mb', 'N/A')}MB\n")
                    f.write(metric_entry)
                
                
        except Exception as e:
            print(f"Error storing metric: {e}")