import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

export const useApiStatus = () => {
  const [status, setStatus] = useState({
    isApiConnected: false,
    isGenerating: false,
    error: null,
    loading: true,
  });

  const checkStatus = useCallback(async () => {
    setStatus(prev => ({ ...prev, loading: true }));
    const result = await apiService.checkStatus();
    
    if (result.success) {
      setStatus({
        isApiConnected: true,
        isGenerating: result.data.is_generating || false,
        error: null,
        loading: false,
      });
    } else {
      setStatus({
        isApiConnected: false,
        isGenerating: false,
        error: result.error,
        loading: false,
      });
    }
  }, []);

  const startMonitoring = async () => {
    const result = await apiService.startMonitoring();
    if (result.success) {
      await checkStatus();
      return true;
    }
    return false;
  };

  const stopMonitoring = async () => {
    const result = await apiService.stopMonitoring();
    if (result.success) {
      await checkStatus();
      return true;
    }
    return false;
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, [checkStatus]);

  return {
    ...status,
    checkStatus,
    startMonitoring,
    stopMonitoring,
  };
};

export const useStreamingData = (autoRefresh = false) => {
  const [logsData, setLogsData] = useState([]);
  const [metricsData, setMetricsData] = useState([]);
  const [error, setError] = useState(null);

  const fetchStreamingData = useCallback(async () => {
    try {
      // Fetch logs from file
      const logsResult = await apiService.fetchLogs();
      if (logsResult && logsResult.success && Array.isArray(logsResult.data)) {
        setLogsData(logsResult.data); // Replace data completely since it's from file
      } else {
        console.warn('Failed to load logs:', logsResult?.error);
      }

      // Fetch metrics from file
      const metricsResult = await apiService.fetchMetrics();
      if (metricsResult && metricsResult.success && Array.isArray(metricsResult.data)) {
        setMetricsData(metricsResult.data); // Replace data completely since it's from file
      } else {
        console.warn('Failed to load metrics:', metricsResult?.error);
      }

      setError(null);
    } catch (err) {
      console.error('Error in fetchStreamingData:', err);
      setError(err.message);
    }
  }, []);

  const clearData = () => {
    setLogsData([]);
    setMetricsData([]);
    setError(null);
  };

  // Initial fetch on mount
  useEffect(() => {
    fetchStreamingData();
  }, []); // Run once on mount

  // Auto-refresh effect (optional for demo)
  useEffect(() => {
    let intervalId = null;
    
    if (autoRefresh) {
      intervalId = setInterval(() => {
        fetchStreamingData();
      }, 10000); // Refresh every 10 seconds for demo
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoRefresh, fetchStreamingData]);

  return {
    logsData,
    metricsData,
    error,
    fetchStreamingData,
    clearData,
  };
};

export const useCommitsData = () => {
  const [commitsData, setCommitsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCommits = async (repo = null, k = 5, useStatic = false) => {
    setLoading(true);
    setError(null);
    
    console.log('Fetching commits:', { repo, k, useStatic });
    const result = await apiService.fetchCommits(repo, k, useStatic);
    console.log('Commits result:', result);
    
    if (result.success) {
      setCommitsData(result.data);
      console.log('Commits data set:', result.data);
    } else {
      console.error('Commits fetch error:', result.error);
      setError(result.error);
    }
    
    setLoading(false);
    return result.success;
  };

  const fetchStaticCommits = () => fetchCommits(null, 10, true);
  const fetchRepositoryCommits = (repoUrl) => fetchCommits(repoUrl, 10, false);

  // Load static commits on mount
  useEffect(() => {
    fetchStaticCommits();
  }, []);

  return {
    commitsData,
    loading,
    error,
    fetchCommits,
    fetchStaticCommits,
    fetchRepositoryCommits,
  };
};

export const useAgentAnalysis = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisSteps, setAnalysisSteps] = useState({
    logs: { status: "pending", name: "System Logs Analysis" },
    metrics: { status: "pending", name: "Performance Metrics Analysis" },
    commits: { status: "pending", name: "Code Commits Analysis" }
  });

  const updateAnalysisSteps = useCallback((analysisResult) => {
    if (!analysisResult || analysisResult.status !== "in_progress") {
      return;
    }

    const analysisContent = analysisResult.analysis || {};
    const contentStr = typeof analysisContent === 'string' 
      ? analysisContent.toLowerCase() 
      : JSON.stringify(analysisContent).toLowerCase();

    setAnalysisSteps(prev => {
      const newSteps = { ...prev };
      
      // Initialize all as pending
      Object.keys(newSteps).forEach(step => {
        if (newSteps[step].status !== "completed") {
          newSteps[step].status = "pending";
        }
      });

      // Check for evidence of each tool being used
      if (contentStr.includes("logs") || contentStr.includes("log analysis") || contentStr.includes("error")) {
        newSteps.logs.status = "completed";
      }

      if (contentStr.includes("metrics") || contentStr.includes("cpu") || contentStr.includes("memory") || contentStr.includes("performance")) {
        newSteps.metrics.status = "completed";
      }

      if (contentStr.includes("commit") || contentStr.includes("code") || contentStr.includes("repository")) {
        newSteps.commits.status = "completed";
      }

      // Set current running step
      const completedCount = Object.values(newSteps).filter(step => step.status === "completed").length;
      
      if (completedCount === 0) {
        newSteps.logs.status = "running";
      } else if (completedCount === 1 && newSteps.logs.status === "completed") {
        newSteps.metrics.status = "running";
      } else if (completedCount === 2) {
        newSteps.commits.status = "running";
      }

      return newSteps;
    });
  }, []);

  const fetchAnalysis = useCallback(async () => {
    const result = await apiService.fetchAgentAnalysis();
    
    if (result.success) {
      setAnalysisData(result.data);
      
      if (result.data.status === "in_progress") {
        setLoading(true);
        updateAnalysisSteps(result.data);
      } else if (result.data.status === "completed") {
        setLoading(false);
        setAnalysisSteps(prev => {
          const newSteps = { ...prev };
          Object.keys(newSteps).forEach(step => {
            newSteps[step].status = "completed";
          });
          return newSteps;
        });
      } else {
        setLoading(false);
      }
    } else {
      setAnalysisData(result.data);
      setLoading(false);
    }
  }, [updateAnalysisSteps]);

  const triggerAnalysis = async () => {
    setLoading(true);
    const result = await apiService.triggerAnalysis();
    
    if (result.success) {
      // Reset steps and start fetching
      setAnalysisSteps({
        logs: { status: "pending", name: "System Logs Analysis" },
        metrics: { status: "pending", name: "Performance Metrics Analysis" },
        commits: { status: "pending", name: "Code Commits Analysis" }
      });
      setTimeout(fetchAnalysis, 1000); // Give backend time to start
    } else {
      setLoading(false);
    }
    
    return result.success;
  };

  // Auto-refresh analysis when loading
  useEffect(() => {
    if (loading) {
      const interval = setInterval(fetchAnalysis, 3000);
      return () => clearInterval(interval);
    }
  }, [loading, fetchAnalysis]);

  // Fetch analysis on mount
  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    analysisData,
    loading,
    analysisSteps,
    fetchAnalysis,
    triggerAnalysis,
  };
};