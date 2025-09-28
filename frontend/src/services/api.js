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

  // Fetch commits data from MongoDB via API
  async fetchCommits(repo = null, k = 5, useStatic = false) {
    try {
      const params = { k, use_static: useStatic };
      if (repo) params.repo = repo;

      const response = await api.get('/commits', { params });
      console.log(`Loaded ${response.data.commits?.length || 0} commits from MongoDB`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching commits:', error);
      return { success: false, error: error.message };
    }
  },

  // Get commits info from MongoDB
  async getCommitsInfo() {
    try {
      const response = await api.get('/commits/info');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Fetch logs from MongoDB via API
  async fetchLogs() {
    try {
      const response = await api.get('/logs');
      console.log(`Loaded ${response.data.logs?.length || 0} logs from MongoDB`);
      return { success: true, data: response.data.logs || [] };
    } catch (error) {
      console.error('Error fetching logs from MongoDB:', error);
      return { success: false, error: error.message };
    }
  },

  // Fetch metrics from MongoDB via API
  async fetchMetrics() {
    try {
      const response = await api.get('/metrics');
      console.log(`Loaded ${response.data.metrics?.length || 0} metrics from MongoDB`);
      return { success: true, data: response.data.metrics || [] };
    } catch (error) {
      console.error('Error fetching metrics from MongoDB:', error);
      return { success: false, error: error.message };
    }
  }
};

export default apiService;