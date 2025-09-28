import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import LogsPanel from './LogsPanel';
import MetricsPanel from './MetricsPanel';
import CommitsPanel from './CommitsPanel';
import AnalysisPanel from './AnalysisPanel';
import { useApiStatus, useStreamingData, useCommitsData, useAgentAnalysis } from '../hooks/useApi';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
    const [autoRefresh, setAutoRefresh] = useState(false); // Disabled for demo - data loaded from files

  // Custom hooks for API data
  const apiStatus = useApiStatus();
  const { logsData, metricsData, error: streamError, fetchStreamingData, clearData } = useStreamingData(autoRefresh);
  const { commitsData, loading: commitsLoading, error: commitsError, fetchRepositoryCommits, fetchStaticCommits } = useCommitsData();
  const { analysisData, loading: analysisLoading, triggerAnalysis } = useAgentAnalysis();

  // Debug logging to help identify issues
  useEffect(() => {
    console.log('Dashboard render:', {
      activeTab,
      autoRefresh,
      logsCount: logsData?.length || 0,
      metricsCount: metricsData?.length || 0,
      streamError,
      apiConnected: apiStatus?.isApiConnected
    });
  }, [activeTab, autoRefresh, logsData, metricsData, streamError, apiStatus]);

  const handleToggleAutoRefresh = () => {
    setAutoRefresh(prev => !prev);
  };

  const renderTabContent = () => {
    // Add safety check
    if (!activeTab) return null;
    
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-[600px]">
            <div className="bg-gray-800 shadow-lg rounded-xl border border-gray-700 overflow-hidden flex flex-col min-h-[500px]">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 flex-shrink-0">
                <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <span>System Logs</span>
                </h2>
              </div>
              <div className="flex-1 p-6 bg-gray-800 overflow-hidden">
                <LogsPanel logsData={logsData || []} isLoading={false} />
              </div>
            </div>
            <div className="bg-gray-800 shadow-lg rounded-xl border border-gray-700 overflow-hidden flex flex-col min-h-[500px]">
              <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4 flex-shrink-0">
                <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <span>Performance </span>
                </h2>
              </div>
              <div className="flex-1 p-6 bg-gray-800 overflow-hidden">
                <MetricsPanel metricsData={metricsData || []} isLoading={false} />
              </div>
            </div>
          </div>
        );
      case 'commits':
        return (
          <div className="bg-gray-800 shadow-lg rounded-xl border border-gray-700 h-full overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
              <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                <span>Commits</span>
              </h2>
            </div>
            <div className="p-6 h-[calc(100%-64px)] bg-gray-800">
              <CommitsPanel 
                commitsData={commitsData} 
                isLoading={commitsLoading} 
                error={commitsError} 
              />
            </div>
          </div>
        );
      case 'analysis':
        return (
          <div className="bg-gray-800 shadow-lg rounded-xl border border-gray-700 h-full overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 px-6 py-4">
              <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                <span>AI  Analysis</span>
              </h2>
            </div>
            <div className="p-6 h-[calc(100%-64px)] bg-gray-800">
              <AnalysisPanel 
                analysisData={analysisData}
                loading={analysisLoading}
              />
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-gray-500 to-gray-100 flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-gradient-to-r from-gray-900 to-gray-800 shadow-sm border-b border-gray-700 flex-shrink-0">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                LogAgent Dashboard
              </h1>
            </div>
            
            {/* Status Indicator */}
            <div className="flex items-center space-x-4">
              {streamError && (
                <div className="bg-red-900 bg-opacity-20 border border-red-600 text-red-300 px-3 py-2 rounded-lg text-sm flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span>Error: {streamError}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          apiStatus={apiStatus}
          onStartMonitoring={apiStatus.startMonitoring}
          onStopMonitoring={apiStatus.stopMonitoring}
          onTriggerAnalysis={triggerAnalysis}
          onFetchRepositoryCommits={fetchRepositoryCommits}
          autoRefresh={autoRefresh}
          onToggleAutoRefresh={handleToggleAutoRefresh}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col bg-gradient-to-b from-gray-900 to-gray-800">
          {/* Tabs */}
          <div className="bg-gray-800 border-b border-gray-700 shadow-sm">
            <nav className="flex space-x-1 px-6">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`py-4 px-6 border-b-2 font-medium text-sm transition-all duration-200 ${
                  activeTab === 'dashboard'
                    ? 'border-blue-400 text-blue-400 bg-gray-700'
                    : 'border-transparent text-gray-300 hover:text-white hover:border-gray-500 hover:bg-gray-700'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('commits')}
                className={`py-4 px-6 border-b-2 font-medium text-sm transition-all duration-200 ${
                  activeTab === 'commits'
                    ? 'border-blue-400 text-blue-400 bg-gray-700'
                    : 'border-transparent text-gray-300 hover:text-white hover:border-gray-500 hover:bg-gray-700'
                }`}
              >
                Commits
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`py-4 px-6 border-b-2 font-medium text-sm transition-all duration-200 ${
                  activeTab === 'analysis'
                    ? 'border-blue-400 text-blue-400 bg-gray-700'
                    : 'border-transparent text-gray-300 hover:text-white hover:border-gray-500 hover:bg-gray-700'
                }`}
              >
                AI Analysis
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="flex-1 p-6 bg-gradient-to-br from-gray-900 to-gray-800 overflow-hidden">
            <div className="h-full overflow-auto">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;