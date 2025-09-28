import React from 'react';
import { GitCommit, GitBranch, User, Calendar, FileText } from 'lucide-react';

const CommitsPanel = ({ commitsData, isLoading, error }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const formatChanges = (changes) => {
    if (!changes) return '';
    if (typeof changes === 'object') {
      const additions = changes.additions || 0;
      const deletions = changes.deletions || 0;
      return `+${additions} -${deletions}`;
    }
    return changes;
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-gray-500">Loading commits...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-red-600">
          <GitCommit className="w-12 h-12 mx-auto mb-2 text-red-300" />
          <p>Error loading commits</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!commitsData) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-500">
          <GitCommit className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p>No commits data available</p>
          <p className="text-sm">Use the sidebar to load commits</p>
        </div>
      </div>
    );
  }

  const commits = commitsData.commits || [];
  const repoInfo = commitsData.repository_info || {};

  return (
    <div className="h-full overflow-y-auto space-y-6">
      {/* Repository Info */}
      {repoInfo.name && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <GitBranch className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-medium text-blue-900">{repoInfo.name}</h3>
          </div>
          {repoInfo.description && (
            <p className="text-sm text-blue-700 mb-2">{repoInfo.description}</p>
          )}
          <div className="flex items-center space-x-4 text-sm text-blue-600">
            {repoInfo.default_branch && (
              <span>Default: {repoInfo.default_branch}</span>
            )}
            {repoInfo.language && (
              <span>Language: {repoInfo.language}</span>
            )}
          </div>
        </div>
      )}

      {/* Commits List */}
      {commits.length === 0 ? (
        <div className="text-center text-gray-900 py-8">
          <GitCommit className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p>No commits found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {commits.map((commit, index) => (
            <div
              key={commit.sha || commit.hash || index}
              className="bg-gray-900 border border-white rounded-lg p-4 hover:border-gray-300 transition-colors"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                    <GitCommit className="w-5 h-5 text-white" />
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  {/* Commit Message */}
                  <h4 className="text-sm font-medium text-white mb-2">
                    {commit.message || commit.commit_message || 'No message'}
                  </h4>
                  
                  {/* Author and Date */}
                  <div className="flex items-center space-x-4 text-xs text-white mb-2">
                    <div className="flex items-center space-x-1">
                      <User className="w-3 h-3" />
                      <span>{commit.author || commit.author_name || 'Unknown author'}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3" />
                      <span>{formatDate(commit.date || commit.timestamp)}</span>
                    </div>
                  </div>
                  
                  {/* SHA */}
                  {(commit.sha || commit.hash) && (
                    <div className="text-xs text-white font-mono mb-2">
                      {(commit.sha || commit.hash).substring(0, 8)}
                    </div>
                  )}
                  
                  {/* Changes */}
                  {(commit.changes || commit.stats) && (
                    <div className="flex items-center space-x-2 text-xs">
                      <FileText className="w-3 h-3 text-gray-400" />
                      <span className="text-green-600">
                        +{commit.changes?.additions || commit.stats?.additions || 0}
                      </span>
                      <span className="text-red-600">
                        -{commit.changes?.deletions || commit.stats?.deletions || 0}
                      </span>
                      <span className="text-gray-500">
                        {commit.changes?.total || commit.stats?.total || 
                         ((commit.changes?.additions || 0) + (commit.changes?.deletions || 0))} changes
                      </span>
                    </div>
                  )}
                  
                  {/* Files Changed */}
                  {commit.files && commit.files.length > 0 && (
                    <div className="mt-2">
                      <details className="text-xs">
                        <summary className="cursor-pointer text-white">
                          {commit.files.length} file{commit.files.length !== 1 ? 's' : ''} changed
                        </summary>
                        <div className="mt-1 ml-4">
                          {commit.files.slice(0, 5).map((file, fileIndex) => (
                            <div key={fileIndex} className="text-white">
                              {file.filename || file.name || file}
                            </div>
                          ))}
                          {commit.files.length > 5 && (
                            <div className="text-gray-500">
                              ... and {commit.files.length - 5} more
                            </div>
                          )}
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CommitsPanel;