import React, { memo } from 'react';
import { FileText, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const LogsPanel = memo(({ logsData, isLoading }) => {
  const getLogIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'info':
        return <Info className="w-4 h-4 text-blue-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const getLogColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return 'border-red-500 bg-red-900 bg-opacity-20';
      case 'warning':
        return 'border-yellow-500 bg-yellow-900 bg-opacity-20';
      case 'info':
        return 'border-blue-500 bg-blue-900 bg-opacity-20';
      case 'success':
        return 'border-green-500 bg-green-900 bg-opacity-20';
      default:
        return 'border-gray-600 bg-gray-700';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-gray-400">Loading logs...</div>
      </div>
    );
  }

  if (!logsData || logsData.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-2 text-gray-600" />
          <p className="text-white">No logs available</p>
          <p className="text-sm">Logs will appear here when monitoring is active</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="space-y-3">
        {logsData.map((log, index) => (
          <div
            key={`log-${index}-${log.timestamp || Date.now()}-${log.message?.substring(0, 20) || ''}`}
            className={`p-4 rounded-lg border ${getLogColor(log.level)}`}
          >
            <div className="flex items-start space-x-3">
              {getLogIcon(log.level)}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  {log.level && (
                    <span className={`px-2 py-1 text-xs font-medium rounded uppercase ${
                      log.level === 'error' ? 'bg-red-800 text-red-200' :
                      log.level === 'warning' ? 'bg-yellow-800 text-yellow-200' :
                      log.level === 'info' ? 'bg-blue-800 text-blue-200' :
                      log.level === 'success' ? 'bg-green-800 text-green-200' :
                      'bg-gray-600 text-gray-200'
                    }`}>
                      {log.level}
                    </span>
                  )}
                  {log.timestamp && (
                    <span className="text-xs text-gray-400">
                      {formatTimestamp(log.timestamp)}
                    </span>
                  )}
                </div>
                
                <div className="text-sm text-white">
                  {log.message || log.text || JSON.stringify(log)}
                </div>
                
                
                {log.details && (
                  <div className="text-xs text-gray-300 mt-2 bg-gray-600 p-2 rounded">
                    <pre className="whitespace-pre-wrap break-words">
                      {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

LogsPanel.displayName = 'LogsPanel';

export default LogsPanel;