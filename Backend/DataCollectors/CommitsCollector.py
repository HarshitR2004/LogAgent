from pydriller import Repository
import json
from pathlib import Path

class CommitsCollector:
    def __init__(self, repo_path: str):
        """
        Initialize the collector with a repository path or URL.
        """
        self.repo_path = repo_path

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
                "files": []
            }
            for mod in commit.modifications:
                commit_info["files"].append({
                    "filename": mod.filename,
                    "code": mod.source_code
                })
            commits_data.append(commit_info)
        return commits_data

    def get_latest_commit(self):
        """
        Get the latest commit only.
        """
        repo = Repository(self.repo_path)
        latest_commit = next(repo.traverse_commits())
        commit_info = {
            "hash": latest_commit.hash,
            "message": latest_commit.msg,
            "files": []
        }
        for mod in latest_commit.modifications:
            commit_info["files"].append({
                "filename": mod.filename,
                "code": mod.source_code
            })
        return commit_info

    def get_last_k_commits(self, k: int):
        """
        Get the last k commits (most recent first).
        """
        commits_data = []
        for i, commit in enumerate(Repository(self.repo_path).traverse_commits()):
            if i >= k:
                break
            commit_info = {
                "hash": commit.hash,
                "message": commit.msg,
                "files": []
            }
            for mod in commit.modifications:
                commit_info["files"].append({
                    "filename": mod.filename,
                    "code": mod.source_code
                })
            commits_data.append(commit_info)
        return commits_data

    def get_commits_from_json(self, k: int = None):
        """
        Get commits data from commit.json file.
        """
        commit_file_path = Path("data/commit.json")
        
        with open(commit_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        commits = data.get("commits", [])
        
        if k is not None:
            return commits[:k]
        
        return commits

        