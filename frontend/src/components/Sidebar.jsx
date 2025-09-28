import React, { useState } from 'react';
import { 
  Power, 
  Square, 
  GitBranch,
  Brain,
  CheckCircle,
  XCircle,
  Loader,
  Github
} from 'lucide-react';

const Sidebar = ({
  apiStatus,
  onStartMonitoring,
  onStopMonitoring,
  onTriggerAnalysis,
  onFetchRepositoryCommits,
  autoRefresh,
  onToggleAutoRefresh,
}) => {
  const [repoInput, setRepoInput] = useState('');
  const [isAnalysisTriggering, setIsAnalysisTriggering] = useState(false);

  const handleStartMonitoring = async () => {
    await onStartMonitoring();
  };

  const handleStopMonitoring = async () => {
    await onStopMonitoring();
  };

  const handleTriggerAnalysis = async () => {
    setIsAnalysisTriggering(true);
    await onTriggerAnalysis();
    setIsAnalysisTriggering(false);
  };

  const handleFetchRepository = () => {
    if (repoInput.trim()) {
      onFetchRepositoryCommits(repoInput.trim());
    }
  };

  return (
    <div className="w-80 bg-gradient-to-b from-gray-900 to-gray-800 text-white p-6 overflow-y-auto shadow-xl border-r border-gray-700">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-2 flex items-center space-x-2">
          <span>Controls</span>
        </h2>
        <div className="w-full h-px bg-gradient-to-r from-blue-400 to-transparent"></div>
      </div>

      {/* API Status */}
      <div className="mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center space-x-2 mb-3">
            {apiStatus.loading ? (
              <Loader className="w-5 h-5 text-gray-400 animate-spin" />
            ) : apiStatus.isApiConnected ? (
              <CheckCircle className="w-5 h-5 text-green-400" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400" />
            )}
            <span className={`font-medium ${
              apiStatus.isApiConnected ? 'text-green-400' : 'text-red-400'
            }`}>
              {apiStatus.loading ? 'Checking...' : apiStatus.isApiConnected ? 'API Connected' : 'API Not Available'}
            </span>
          </div>

          {apiStatus.isApiConnected ? (
            <div className="space-y-3">
              {apiStatus.isGenerating ? (
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-blue-400">
                    <Loader className="w-4 h-4 animate-spin" />
                    <span className="text-sm font-medium">Monitoring Active</span>
                  </div>
                  <button
                    onClick={handleStopMonitoring}
                    className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    <Square className="w-4 h-4" />
                    <span>Stop Monitoring</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="text-yellow-400 text-sm font-medium">Monitoring Stopped</div>
                  <button
                    onClick={handleStartMonitoring}
                    className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    <Power className="w-4 h-4" />
                    <span>Start Monitoring</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-red-400 text-sm">
              <p>Make sure the FastAPI server is running on port 8000</p>
            </div>
          )}
        </div>
      </div>

      <div className="w-full h-px bg-gradient-to-r from-gray-600 to-transparent mb-6"></div>

      {/* AI Analysis */}
      {apiStatus.isApiConnected && (
        <div className="mb-6">
          <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <span>AI Analysis</span>
          </h3>
          <button
            onClick={handleTriggerAnalysis}
            disabled={isAnalysisTriggering}
            className="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:from-purple-300 disabled:to-purple-400 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            {isAnalysisTriggering ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Brain className="w-4 h-4" />
            )}
            <span>
              {isAnalysisTriggering ? 'Triggering...' : 'Run Root Cause Analysis'}
            </span>
          </button>
        </div>
      )}

      {/* Auto Refresh */}
      <div className="mb-6">
        <label className="flex items-center space-x-3 cursor-pointer">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={onToggleAutoRefresh}
            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
          />
          <span className="text-sm font-medium text-white">Auto Refresh</span>
        </label>
      </div>

      <div className="w-full h-px bg-gradient-to-r from-gray-600 to-transparent mb-6"></div>

      {/* Commit Analysis */}
      <div className="mb-6">
        <h3 className="font-semibold text-white mb-3 flex items-center space-x-2">
          <GitBranch className="w-4 h-4 text-green-400" />
          <span>Github Configuration</span>
        </h3>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Repository URL
            </label>
            <input
              type="text"
              value={repoInput}
              onChange={(e) => setRepoInput(e.target.value)}
              placeholder="https://github.com/user/repo.git"
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            onClick={handleFetchRepository}
            disabled={!repoInput.trim()}
            className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Github className="w-4 h-4" />
            <span>Fetch Repository Commits</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;