import React, { memo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, Cpu, HardDrive } from 'lucide-react';

const MetricsPanel = memo(({ metricsData, isLoading }) => {
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const getLatestMetrics = () => {
    if (!metricsData || metricsData.length === 0) return null;
    return metricsData[metricsData.length - 1];
  };

  const prepareChartData = () => {
    if (!metricsData || metricsData.length === 0) return [];
    
    return metricsData.map((metric, index) => ({
      time: formatTimestamp(metric.timestamp) || `Point ${index + 1}`,
      cpu: metric.cpu_usage || metric.cpu || 0,
      memory: metric.memory_usage || metric.memory || 0,
    })).slice(-20); // Show last 20 data points
  };

  const latestMetrics = getLatestMetrics();
  const chartData = prepareChartData();

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-gray-400">Loading metrics...</div>
      </div>
    );
  }

  if (!metricsData || metricsData.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <Activity className="w-12 h-12 mx-auto mb-2 text-gray-600" />
          <p className="text-white">No metrics available</p>
          <p className="text-sm">System metrics will appear here when monitoring is active</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto space-y-6">
      {/* Current Metrics Cards */}
      {latestMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-900 bg-opacity-30 border border-blue-600 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-blue-400" />
              <h3 className="text-sm font-medium text-blue-300">CPU Usage</h3>
            </div>
            <p className="text-2xl font-bold text-blue-400 mt-2">
              {(latestMetrics.cpu_usage || latestMetrics.cpu || 0).toFixed(1)}%
            </p>
          </div>

          <div className="bg-green-900 bg-opacity-30 border border-green-600 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <HardDrive className="w-5 h-5 text-green-400" />
              <h3 className="text-sm font-medium text-green-300">Memory</h3>
            </div>
            <p className="text-2xl font-bold text-green-400 mt-2">
              {(latestMetrics.memory_usage || latestMetrics.memory || 0).toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* CPU Usage Chart */}
      {chartData.length > 1 && (
        <div className="bg-gray-700 border border-gray-600 rounded-lg p-4">
          <h3 className="text-lg font-medium text-white mb-4 flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <span>CPU Usage Over Time</span>
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  domain={[0, 100]}
                  fontSize={12}
                  label={{ value: '%', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value) => [`${value.toFixed(1)}%`, 'CPU Usage']}
                  labelStyle={{ color: '#374151' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="cpu" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Memory Usage Chart */}
      {chartData.length > 1 && (
        <div className="bg-gray border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-200 mb-4 flex items-center space-x-2">
            <HardDrive className="w-5 h-5 text-green-600" />
            <span>Memory Usage Over Time</span>
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  fontSize={12}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis 
                  domain={[0, 100]}
                  fontSize={12}
                  label={{ value: '%', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value) => [`${value.toFixed(1)}%`, 'Memory Usage']}
                  labelStyle={{ color: '#374151' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="memory" 
                  stroke="#10B981" 
                  fill="#10B981"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}


    </div>
  );
});

MetricsPanel.displayName = 'MetricsPanel';

export default MetricsPanel;