from DataCollectors.Telemenetry import TelemetryGenerator

class EventDetection:
    def __init__(self):
        self.cpu_threshold = 85
        self.memory_threshold = 90
        self.error_keywords = ["error", "failed", "exception", "critical"]
    
    def detect_from_metric(self, metric):
        """Detect events from a single metric entry"""
        if metric.get("cpu_percent", 0) > self.cpu_threshold:
            return True
        if metric.get("memory_percent", 0) > self.memory_threshold:
            return True
        return False
    
    def detect_from_log(self, log):
        """Detect events from a single log entry"""
        message = log.get("message", "").lower()
        if any(keyword in message for keyword in self.error_keywords):
            return True
        return False