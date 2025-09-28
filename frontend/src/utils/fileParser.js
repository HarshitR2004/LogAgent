// Utility functions to parse data from text files for demo purposes

export const parseLogsFromText = (logText) => {
  if (!logText || typeof logText !== 'string') return [];
  
  const lines = logText.split('\n').filter(line => line.trim() && !line.startsWith('='));
  const logs = [];
  
  for (let i = 0; i < lines.length; i += 2) {
    const logLine = lines[i];
    const messageLine = lines[i + 1];
    
    if (!logLine) continue;
    
    try {
      // Parse log line format: [timestamp] LEVEL - User: username - IP: ip - METHOD path - Status: status - Latency: latencyms
      const timestampMatch = logLine.match(/^\[([^\]]+)\]/);
      const levelMatch = logLine.match(/\] (\w+) -/);
      const userMatch = logLine.match(/User: ([^\s]+)/);
      const ipMatch = logLine.match(/IP: ([^\s]+)/);
      const methodMatch = logLine.match(/(\w+) (\/[^\s]*)/);
      const statusMatch = logLine.match(/Status: (\d+)/);
      const latencyMatch = logLine.match(/Latency: (\d+)ms/);
      
      // Parse message line
      const message = messageLine ? messageLine.replace('Message: ', '').trim() : '';
      
      if (timestampMatch && levelMatch) {
        const log = {
          timestamp: timestampMatch[1],
          level: levelMatch[1],
          user: userMatch ? userMatch[1] : '',
          ip: ipMatch ? ipMatch[1] : '',
          method: methodMatch ? methodMatch[1] : '',
          path: methodMatch ? methodMatch[2] : '',
          status: statusMatch ? parseInt(statusMatch[1]) : 0,
          latency: latencyMatch ? parseInt(latencyMatch[1]) : 0,
          message: message,
          source: 'filtered_logs'
        };
        
        logs.push(log);
      }
    } catch (e) {
      console.warn('Failed to parse log line:', logLine, e);
    }
  }
  
  return logs.slice(-50); // Return last 50 logs
};

export const parseMetricsFromText = (metricsText) => {
  if (!metricsText || typeof metricsText !== 'string') return [];
  
  const lines = metricsText.split('\n').filter(line => line.trim());
  const metrics = [];
  
  for (const line of lines) {
    // Skip session headers
    if (line.startsWith('===') || !line.includes('CPU:')) continue;
    
    try {
      // Parse metrics line format: [timestamp] CPU: xx% - Memory: xx% - Memory Used: xxMB - Memory Total: xxMB
      const timestampMatch = line.match(/^\[([^\]]+)\]/);
      const cpuMatch = line.match(/CPU: ([0-9.]+)%/);
      const memoryMatch = line.match(/Memory: ([0-9.]+)%/);
      const memoryUsedMatch = line.match(/Memory Used: ([0-9]+)MB/);
      const memoryTotalMatch = line.match(/Memory Total: ([0-9]+)MB/);
      
      if (timestampMatch && cpuMatch && memoryMatch) {
        const metric = {
          timestamp: timestampMatch[1],
          cpu: parseFloat(cpuMatch[1]),
          memory: parseFloat(memoryMatch[1]),
          cpu_usage: parseFloat(cpuMatch[1]),
          memory_usage: parseFloat(memoryMatch[1]),
          memory_used_mb: memoryUsedMatch ? parseInt(memoryUsedMatch[1]) : 0,
          memory_total_mb: memoryTotalMatch ? parseInt(memoryTotalMatch[1]) : 0,
          source: 'metrics_file'
        };
        
        metrics.push(metric);
      }
    } catch (e) {
      console.warn('Failed to parse metrics line:', line, e);
    }
  }
  
  return metrics.slice(-30); // Return last 30 metrics
};

export const loadTextFile = async (filePath) => {
  try {
    const response = await fetch(filePath);
    if (!response.ok) {
      throw new Error(`Failed to load file: ${response.status}`);
    }
    return await response.text();
  } catch (error) {
    console.error('Error loading text file:', filePath, error);
    return '';
  }
};

export const loadJsonFile = async (filePath) => {
  try {
    const response = await fetch(filePath);
    if (!response.ok) {
      throw new Error(`Failed to load file: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading JSON file:', filePath, error);
    return null;
  }
};

export const parseCommitsFromJson = (jsonData) => {
  if (!jsonData || !jsonData.commits) return [];
  
  return jsonData.commits.map(commit => ({
    hash: commit.hash,
    message: commit.message,
    files: commit.files || [],
    author: commit.author || 'Unknown',
    date: commit.date || new Date().toISOString(),
    url: commit.url || '',
    source: 'static_file'
  }));
};