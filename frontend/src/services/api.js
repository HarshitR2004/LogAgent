import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

// Create axios instance with common config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// API endpoints
export const endpoints = {
  logs: `${API_BASE}/logs`,
  metrics: `${API_BASE}/metrics`,
  commits: `${API_BASE}/commits`,
  commitsInfo: `${API_BASE}/commits/info`,
  status: `${API_BASE}/status`,
  start: `${API_BASE}/start`,
  stop: `${API_BASE}/stop`,
  agentAnalysis: `${API_BASE}/agent-analysis`,
  triggerAnalysis: `${API_BASE}/trigger-analysis`,
};

// API service functions
export const apiService = {
  // Check API status and get monitoring status
  async checkStatus() {
    try {
      const response = await api.get('/status');
      console.log('API Status Response:', response.data);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Start monitoring
  async startMonitoring() {
    try {
      const response = await api.post('/start');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Stop monitoring
  async stopMonitoring() {
    try {
      const response = await api.post('/stop');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Fetch agent analysis results
  async fetchAgentAnalysis() {
    try {
      const response = await api.get('/agent-analysis');
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        data: { status: "error", message: `Failed to fetch analysis: ${error.message}` }
      };
    }
  },

  // Trigger analysis
  async triggerAnalysis() {
    try {
      const response = await api.post('/trigger-analysis');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Fetch commits data
  async fetchCommits(repo = null, k = 5, useStatic = false) {
    try {
      // If loading static commits, load directly from file
      if (useStatic) {
        const { loadJsonFile, parseCommitsFromJson } = await import('../utils/fileParser.js');
        const jsonData = await loadJsonFile('/data/commit.json');
        if (jsonData) {
          const commits = parseCommitsFromJson(jsonData);
          const limitedCommits = k ? commits.slice(0, k) : commits;
          console.log(`Loaded ${limitedCommits.length} commits from file`);
          return { success: true, data: { commits: limitedCommits } };
        }
        throw new Error('Failed to load commits from file');
      }

      // For repository commits, use API
      const params = { k, use_static: useStatic };
      if (repo) params.repo = repo;

      const response = await api.get('/commits', { params });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching commits:', error);
      return { success: false, error: error.message };
    }
  },

  // Get commits info
  async getCommitsInfo() {
    try {
      const response = await api.get('/commits/info');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Fetch logs from text file
  async fetchLogs() {
    try {
      const { loadTextFile, parseLogsFromText } = await import('../utils/fileParser.js');
      const logText = await loadTextFile('/data/filteredLogs.txt');
      const logs = parseLogsFromText(logText);
      
      console.log(`Loaded ${logs.length} logs from file`);
      return { success: true, data: logs };
    } catch (error) {
      console.error('Error fetching logs from file:', error);
      return { success: false, error: error.message };
    }
  },

  // Fetch metrics from text file
  async fetchMetrics() {
    try {
      const { loadTextFile, parseMetricsFromText } = await import('../utils/fileParser.js');
      const metricsText = await loadTextFile('/data/metrics.txt');
      const metrics = parseMetricsFromText(metricsText);
      
      console.log(`Loaded ${metrics.length} metrics from file`);
      return { success: true, data: metrics };
    } catch (error) {
      console.error('Error fetching metrics from file:', error);
      return { success: false, error: error.message };
    }
  }
};

export default apiService;