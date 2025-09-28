# LogAgent - AI-Powered System Monitoring Agent

LogAgent is an advanced real-time system monitoring platform with AI-powered root cause analysis. The system provides comprehensive insights into system performance, logs, and code changes while leveraging artificial intelligence to automatically identify potential issues and their underlying causes.

## 🚀 Features

### Real-Time Monitoring
- **Live System Telemetry**: Real-time collection of system logs, performance metrics, and application data
- **Interactive Dashboard**: Web-based interface with real-time data visualization and metrics
- **Multi-Source Data Integration**: Unified monitoring of logs, system metrics, and code repository changes

### AI-Powered Analysis
- **Comprehensive Root Cause Analysis**: AI agent that analyzes multiple data sources simultaneously
- **Multi-Tool Analysis**: Uses specialized analyzers for logs, metrics, and commits


## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework for API development
- **MongoDB**: NoSQL database for storing logs, metrics, and commit data
- **PyMongo**: Official MongoDB driver for Python

### Frontend & Visualization
- **React**: Modern JavaScript framework with hooks and functional components
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
- MongoDB 4.4 or higher (local installation or MongoDB Atlas)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/HarshitR2004/LogAgent.git
cd LogAgent
```

### 2. Set Up MongoDB
#### Option A: Local MongoDB Installation
1. Install MongoDB Community Edition from [MongoDB Downloads](https://www.mongodb.com/try/download/community)
2. Start the MongoDB service:
   ```bash
   # On Windows (as Administrator)
   net start MongoDB
   
   # On macOS/Linux
   sudo systemctl start mongod
   ```
3. Ensure MongoDB is running on the default port `27017`

#### Option B: MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster and get the connection string
3. Update the MongoDB connection string in `Backend/Services/MongoClient.py` if using a custom connection

### 3. Install Dependencies

#### Backend Dependencies
```bash
pip install -r requirements.txt
```

#### Frontend Dependencies
```bash
cd frontend
npm install
```

### 4. Environment Configuration
Create a `.env` file in the root directory with your API keys:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
# Optional: Custom MongoDB connection string
# MONGODB_URI=your_mongodb_connection_string_here
```

### 5. Initialize Database (First Time Setup)
Run the data migration script to set up the database structure:
```bash
python migrate_data.py
```

### 6. Start the Backend Services
```bash
cd Backend
uvicorn main:app --reload --port 8000
```

### 7. Launch the Frontend Dashboard
In a new terminal:
```bash
cd frontend
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
- **MongoDB Client**: Centralized database operations for all data storage and retrieval
- **Log Filter**: Processes and categorizes log entries, stores in MongoDB
- **Metrics Collector**: Gathers system performance data, persists to MongoDB
- **Event Detection**: Identifies significant system events
- **Commits Collector**: Analyzes repository changes, stores commit data in MongoDB

#### Data Storage
- **MongoDB Collections**:
  - **logs**: System logs with filtering and categorization
  - **metrics**: Performance metrics and system telemetry
  - **commits**: Repository commit history and code changes
- **Indexed Collections**: Optimized database queries for real-time performance

#### AI Analysis Engine
- **Agent Controller**: Orchestrates multi-tool analysis workflow
- **Specialized Analyzers**:
  - **Logs Analyzer**: Identifies error patterns and system issues
  - **Metrics Analyzer**: Analyzes performance trends and anomalies
  - **Commits Analyzer**: Correlates code changes with system issues

#### Frontend Components
- **Modern React Architecture**: Component-based architecture with hooks and context
- **Real-time Updates**: Live data streaming and automatic refresh capabilities
- **Interactive Charts**: Dynamic metrics visualization using Recharts library



### Data Flow
1. **Collection**: Multiple collectors gather data from various sources
2. **Storage**: All data is stored in MongoDB collections with proper indexing
3. **Processing**: Data is filtered, categorized, and structured in the database
4. **Retrieval**: Frontend and AI components query MongoDB for real-time data
5. **Analysis**: AI agent processes all data sources for root cause analysis
6. **Visualization**: Results displayed in interactive React components with modern UI

## 🗃 Database Configuration

### MongoDB Setup
LogAgent uses MongoDB to store all monitoring data including logs, metrics, and commit information. The system creates three main collections:

- **logs**: Stores system logs with timestamp, level, user info, and messages
- **metrics**: Contains system performance data (CPU, memory usage, etc.)
- **commits**: Repository commit history with file changes and metadata

### Database Configuration Options
The MongoDB client can be configured in `Backend/Services/MongoClient.py`:
- **Connection String**: Default is `mongodb://localhost:27017/`
- **Database Name**: Default is `logagent`
- **Collections**: Automatically created with proper indexing

### Troubleshooting MongoDB
- **Connection Issues**: Ensure MongoDB is running and accessible
- **Performance**: The system creates indexes automatically for optimal query performance
- **Storage**: Monitor disk space as logs and metrics can grow over time
- **Migration**: Use the provided migration script to initialize or transfer data









