# LogAgent - AI-Powered System Monitoring Agent

LogAgent is an advanced real-time system monitoring platform with AI-powered root cause analysis. The system provides comprehensive insights into system performance, logs, and code changes while leveraging artificial intelligence to automatically identify potential issues and their underlying causes.

## 🚀 Features

### Real-Time Monitoring
- **Live System Telemetry**: Real-time collection of system logs, performance metrics, and application data
- **Interactive Dashboard**: Web-based interface with real-time data visualization and metrics
- **Multi-Source Data Integration**: Unified monitoring of logs, system metrics, and code repository changes

### AI-Powered Analysis
- **Comprehensive Root Cause Analysis**: AI agent that analyzes multiple data sources simultaneously
- **Pattern Recognition**: Identifies recurring issues and system vulnerabilities
- **Multi-Tool Analysis**: Uses specialized analyzers for logs, metrics, and commits

### Advanced Capabilities
- **Automated Event Detection**: Intelligent detection of system anomalies and performance issues
- **Code Change Correlation**: Analyzes recent commits in relation to system issues
- **Performance Trend Analysis**: Tracks system performance patterns over time

## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework for API development

### Frontend & Visualization
- **React 19**: Modern JavaScript framework with hooks and functional components
- **Tailwind CSS v4**: Utility-first CSS framework for responsive design
- **Vite**: Lightning-fast build tool and development server
- **Recharts**: Interactive data visualization library for metrics and analytics
- **Lucide React**: Modern icon library for UI components

### AI & Machine Learning
- **LangChain**: Framework for building AI agent workflows
- **Google Gemini 2.5 Flash**: Large language model for natural language processing
- **Custom AI Tools**: Specialized analyzers for different data types


## 📋 System Requirements

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn package manager

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/HarshitR2004/LogAgent.git
```

### 2. Install Dependencies

#### Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install
```

### 3. Environment Configuration
Create a `.env` file in the root directory with your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Start the Backend Services
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Launch the Frontend Dashboard
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Usage

### Starting the System
1. **Launch Backend**: Start the FastAPI server to begin data collection
2. **Open Dashboard**: Access the web interface at `http://localhost:5173`
3. **Start Monitoring**: Click "Start Monitoring" to begin real-time data collection

### Monitoring Features
- **Real-Time Logs**: View system logs with filtering capabilities
- **Performance Metrics**: Monitor CPU, memory usage, and system performance
- **Repository Analysis**: Track code commits and changes
- **AI Analysis**: Trigger comprehensive root cause analysis

### AI Analysis Workflow
1. **Data Collection**: System continuously collects logs, metrics, and repository data
2. **Trigger**: Use "Run Root Cause Analysis" button to start AI analysis
3. **Multi-Tool Processing**: AI agent uses specialized analysis tools:
   - Log Analysis Tool
   - Metrics Analysis Tool
   - Commits Analysis Tool
4. **Comprehensive Report**: Receive detailed analysis with root cause identification

## 🏗 Architecture

### System Components

#### Backend Services
- **Telemetry Generator**: Produces realistic system telemetry data
- **Log Filter**: Processes and categorizes log entries
- **Metrics Collector**: Gathers system performance data
- **Event Detection**: Identifies significant system events
- **Commits Collector**: Analyzes repository changes

#### AI Analysis Engine
- **Agent Controller**: Orchestrates multi-tool analysis workflow
- **Specialized Analyzers**:
  - **Logs Analyzer**: Identifies error patterns and system issues
  - **Metrics Analyzer**: Analyzes performance trends and anomalies
  - **Commits Analyzer**: Correlates code changes with system issues

#### Frontend Components
- **Modern React Architecture**: Component-based architecture with hooks and context
- **Responsive Dashboard**: Adaptive layout that works on desktop and tablet devices  
- **Real-time Updates**: Live data streaming and automatic refresh capabilities
- **Interactive Charts**: Dynamic metrics visualization using Recharts library
- **Error Boundaries**: Robust error handling to prevent application crashes

#### Data Storage
- **File-based Demo Mode**: Loads sample data from static files for demonstration
- **In-Memory Buffers**: Real-time data streaming queues for live monitoring

### Data Flow
1. **Collection**: Multiple collectors gather data from various sources
2. **Processing**: Data is filtered, categorized, and stored
5. **Analysis**: AI agent processes all data sources for root cause analysis
6. **Visualization**: Results displayed in interactive React components with modern UI









