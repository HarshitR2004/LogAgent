from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="logagent"):
        """
        Initialize MongoDB client
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to use
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {database_name}")
            
            # Initialize collections
            self.logs_collection = self.db.logs
            self.metrics_collection = self.db.metrics
            self.commits_collection = self.db.commits
            
            # Create indexes for better performance
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Index for logs collection
            self.logs_collection.create_index("timestamp")
            self.logs_collection.create_index("level")
            self.logs_collection.create_index("status_code")
            
            # Index for metrics collection
            self.metrics_collection.create_index("timestamp")
            self.metrics_collection.create_index("metric_type")
            
            # Index for commits collection
            self.commits_collection.create_index("timestamp")
            self.commits_collection.create_index("repo_name")
            
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")

    # =============== LOGS OPERATIONS ===============
    
    def store_log(self, log_data: Dict[str, Any]) -> str:
        """
        Store a single log entry
        
        Args:
            log_data: Dictionary containing log information
            
        Returns:
            str: ID of the inserted document
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in log_data:
                log_data['timestamp'] = datetime.utcnow()
            elif isinstance(log_data['timestamp'], str):
                # Convert string timestamp to datetime if needed
                try:
                    log_data['timestamp'] = datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00'))
                except:
                    log_data['timestamp'] = datetime.utcnow()
                    
            result = self.logs_collection.insert_one(log_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to store log: {e}")
            raise

    def store_logs(self, logs_data: List[Dict[str, Any]]) -> List[str]:
        """
        Store multiple log entries
        
        Args:
            logs_data: List of dictionaries containing log information
            
        Returns:
            List[str]: List of IDs of the inserted documents
        """
        try:
            # Process timestamps for all logs
            for log in logs_data:
                if 'timestamp' not in log:
                    log['timestamp'] = datetime.utcnow()
                elif isinstance(log['timestamp'], str):
                    try:
                        log['timestamp'] = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                    except:
                        log['timestamp'] = datetime.utcnow()
                        
            result = self.logs_collection.insert_many(logs_data)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Failed to store logs: {e}")
            raise

    def get_logs(self, limit: int = 1000, level: Optional[str] = None, 
                 start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Retrieve logs with optional filtering
        
        Args:
            limit: Maximum number of logs to return
            level: Filter by log level (ERROR, WARNING, INFO, etc.)
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            
        Returns:
            List[Dict]: List of log documents
        """
        try:
            query = {}
            
            if level:
                query['level'] = level
                
            if start_time or end_time:
                timestamp_query = {}
                if start_time:
                    timestamp_query['$gte'] = start_time
                if end_time:
                    timestamp_query['$lte'] = end_time
                query['timestamp'] = timestamp_query
            
            cursor = self.logs_collection.find(query).sort("timestamp", -1).limit(limit)
            logs = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for log in logs:
                log['_id'] = str(log['_id'])
                
            return logs
        except Exception as e:
            logger.error(f"Failed to retrieve logs: {e}")
            return []

    def get_filtered_logs(self, levels: List[str] = ['ERROR', 'WARNING'], limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get logs filtered by levels (typically ERROR and WARNING)
        
        Args:
            levels: List of log levels to filter by
            limit: Maximum number of logs to return
            
        Returns:
            List[Dict]: List of filtered log documents
        """
        return self.get_logs(limit=limit, level={'$in': levels} if len(levels) > 1 else levels[0])

    def clear_logs(self) -> bool:
        """
        Clear all logs from the collection
        
        Returns:
            bool: True if successful
        """
        try:
            self.logs_collection.delete_many({})
            return True
        except Exception as e:
            logger.error(f"Failed to clear logs: {e}")
            return False

    # =============== METRICS OPERATIONS ===============
    
    def store_metric(self, metric_data: Dict[str, Any]) -> str:
        """
        Store a single metric entry
        
        Args:
            metric_data: Dictionary containing metric information
            
        Returns:
            str: ID of the inserted document
        """
        try:
            if 'timestamp' not in metric_data:
                metric_data['timestamp'] = datetime.utcnow()
            elif isinstance(metric_data['timestamp'], str):
                try:
                    metric_data['timestamp'] = datetime.fromisoformat(metric_data['timestamp'].replace('Z', '+00:00'))
                except:
                    metric_data['timestamp'] = datetime.utcnow()
                    
            result = self.metrics_collection.insert_one(metric_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
            raise

    def store_metrics(self, metrics_data: List[Dict[str, Any]]) -> List[str]:
        """
        Store multiple metric entries
        
        Args:
            metrics_data: List of dictionaries containing metric information
            
        Returns:
            List[str]: List of IDs of the inserted documents
        """
        try:
            for metric in metrics_data:
                if 'timestamp' not in metric:
                    metric['timestamp'] = datetime.utcnow()
                elif isinstance(metric['timestamp'], str):
                    try:
                        metric['timestamp'] = datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00'))
                    except:
                        metric['timestamp'] = datetime.utcnow()
                        
            result = self.metrics_collection.insert_many(metrics_data)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            raise

    def get_metrics(self, limit: int = 1000, metric_type: Optional[str] = None,
                   start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Retrieve metrics with optional filtering
        
        Args:
            limit: Maximum number of metrics to return
            metric_type: Filter by metric type (cpu, memory, etc.)
            start_time: Filter metrics after this time
            end_time: Filter metrics before this time
            
        Returns:
            List[Dict]: List of metric documents
        """
        try:
            query = {}
            
            if metric_type:
                query['metric_type'] = metric_type
                
            if start_time or end_time:
                timestamp_query = {}
                if start_time:
                    timestamp_query['$gte'] = start_time
                if end_time:
                    timestamp_query['$lte'] = end_time
                query['timestamp'] = timestamp_query
            
            cursor = self.metrics_collection.find(query).sort("timestamp", -1).limit(limit)
            metrics = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for metric in metrics:
                metric['_id'] = str(metric['_id'])
                
            return metrics
        except Exception as e:
            logger.error(f"Failed to retrieve metrics: {e}")
            return []

    def clear_metrics(self) -> bool:
        """
        Clear all metrics from the collection
        
        Returns:
            bool: True if successful
        """
        try:
            self.metrics_collection.delete_many({})
            return True
        except Exception as e:
            logger.error(f"Failed to clear metrics: {e}")
            return False

    # =============== COMMITS OPERATIONS ===============
    
    def store_commit(self, commit_data: Dict[str, Any]) -> str:
        """
        Store a single commit entry
        
        Args:
            commit_data: Dictionary containing commit information
            
        Returns:
            str: ID of the inserted document
        """
        try:
            if 'timestamp' not in commit_data:
                commit_data['timestamp'] = datetime.utcnow()
            elif isinstance(commit_data['timestamp'], str):
                try:
                    commit_data['timestamp'] = datetime.fromisoformat(commit_data['timestamp'].replace('Z', '+00:00'))
                except:
                    commit_data['timestamp'] = datetime.utcnow()
                    
            result = self.commits_collection.insert_one(commit_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to store commit: {e}")
            raise

    def store_commits(self, commits_data: List[Dict[str, Any]]) -> List[str]:
        """
        Store multiple commit entries
        
        Args:
            commits_data: List of dictionaries containing commit information
            
        Returns:
            List[str]: List of IDs of the inserted documents
        """
        try:
            for commit in commits_data:
                if 'timestamp' not in commit:
                    commit['timestamp'] = datetime.utcnow()
                elif isinstance(commit['timestamp'], str):
                    try:
                        commit['timestamp'] = datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00'))
                    except:
                        commit['timestamp'] = datetime.utcnow()
                        
            result = self.commits_collection.insert_many(commits_data)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Failed to store commits: {e}")
            raise

    def get_commits(self, limit: int = 100, repo_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve commits with optional filtering
        
        Args:
            limit: Maximum number of commits to return
            repo_name: Filter by repository name
            
        Returns:
            List[Dict]: List of commit documents
        """
        try:
            query = {}
            
            if repo_name:
                query['repo_name'] = repo_name
            
            cursor = self.commits_collection.find(query).sort("timestamp", -1).limit(limit)
            commits = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for commit in commits:
                commit['_id'] = str(commit['_id'])
                
            return commits
        except Exception as e:
            logger.error(f"Failed to retrieve commits: {e}")
            return []

    def clear_commits(self) -> bool:
        """
        Clear all commits from the collection
        
        Returns:
            bool: True if successful
        """
        try:
            self.commits_collection.delete_many({})
            return True
        except Exception as e:
            logger.error(f"Failed to clear commits: {e}")
            return False

    # =============== GENERAL OPERATIONS ===============
    
    def get_collection_stats(self) -> Dict[str, int]:
        """
        Get statistics about all collections
        
        Returns:
            Dict: Collection names and document counts
        """
        try:
            return {
                'logs': self.logs_collection.count_documents({}),
                'metrics': self.metrics_collection.count_documents({}),
                'commits': self.commits_collection.count_documents({})
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'logs': 0, 'metrics': 0, 'commits': 0}

    def close_connection(self):
        """Close the MongoDB connection"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Failed to close MongoDB connection: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_connection()