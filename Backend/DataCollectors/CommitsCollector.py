from pydriller import Repository
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the Backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Services.MongoClient import MongoDBClient

class CommitsCollector:
    def __init__(self, repo_path: str = None, mongo_client=None):
        """
        Initialize the collector with a repository path or URL.
        """
        self.repo_path = repo_path
        self.mongo_client = mongo_client or MongoDBClient()

    def get_all_commits(self):
        """
        Get all commits with filenames and source code.
        Returns a list of dicts: [{hash, message, files: [{filename, code}]}]
        """
        commits_data = []
        for commit in Repository(self.repo_path).traverse_commits():
            commit_info = {
                "hash": commit.hash,
                "message": commit.msg,
                "timestamp": commit.committer_date,
                "author": commit.author.name,
                "repo_name": Path(self.repo_path).name if self.repo_path else "unknown",
                "files": []
            }
            for mod in commit.modifications:
                if mod.source_code:  # Only include files with source code
                    commit_info["files"].append({
                        "filename": mod.filename,
                        "code": mod.source_code
                    })
            commits_data.append(commit_info)
        
        # Store in MongoDB
        if commits_data:
            self.mongo_client.store_commits(commits_data)
        
        return commits_data

    def get_latest_commit(self):
        """
        Get the latest commit only.
        """
        if not self.repo_path:
            # Return from MongoDB if no repo path
            commits = self.mongo_client.get_commits(limit=1)
            return commits[0] if commits else None
            
        repo = Repository(self.repo_path)
        latest_commit = next(repo.traverse_commits())
        commit_info = {
            "hash": latest_commit.hash,
            "message": latest_commit.msg,
            "timestamp": latest_commit.committer_date,
            "author": latest_commit.author.name,
            "repo_name": Path(self.repo_path).name,
            "files": []
        }
        for mod in latest_commit.modifications:
            if mod.source_code:  # Only include files with source code
                commit_info["files"].append({
                    "filename": mod.filename,
                    "code": mod.source_code
                })
        
        # Store in MongoDB
        self.mongo_client.store_commit(commit_info)
        
        return commit_info

    def get_last_k_commits(self, k: int):
        """
        Get the last k commits (most recent first).
        """
        if not self.repo_path:
            # Return from MongoDB if no repo path
            return self.mongo_client.get_commits(limit=k)
            
        commits_data = []
        for i, commit in enumerate(Repository(self.repo_path).traverse_commits()):
            if i >= k:
                break
            commit_info = {
                "hash": commit.hash,
                "message": commit.msg,
                "timestamp": commit.committer_date,
                "author": commit.author.name,
                "repo_name": Path(self.repo_path).name,
                "files": []
            }
            for mod in commit.modifications:
                if mod.source_code:  # Only include files with source code
                    commit_info["files"].append({
                        "filename": mod.filename,
                        "code": mod.source_code
                    })
            commits_data.append(commit_info)
        
        # Store in MongoDB
        if commits_data:
            self.mongo_client.store_commits(commits_data)
        
        return commits_data

    def get_commits_from_mongo(self, k: int = None, repo_name: str = None):
        """
        Get commits data from MongoDB.
        """
        try:
            return self.mongo_client.get_commits(limit=k or 100, repo_name=repo_name)
        except Exception as e:
            print(f"Error retrieving commits from MongoDB: {e}")
            return []

        