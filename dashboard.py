import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
import time
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure Streamlit page
st.set_page_config(
    page_title="Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoints
API_BASE = "http://127.0.0.1:8000"
LOGS_STREAM = f"{API_BASE}/logs"
METRICS_STREAM = f"{API_BASE}/metrics"
COMMITS_ENDPOINT = f"{API_BASE}/commits"
COMMITS_INFO_ENDPOINT = f"{API_BASE}/commits/info"
STATUS_ENDPOINT = f"{API_BASE}/status"
START_ENDPOINT = f"{API_BASE}/start"
STOP_ENDPOINT = f"{API_BASE}/stop"
AGENT_ANALYSIS_ENDPOINT = f"{API_BASE}/agent-analysis"

# Initialize session state
if 'logs_data' not in st.session_state:
    st.session_state.logs_data = []
if 'metrics_data' not in st.session_state:
    st.session_state.metrics_data = []
if 'commits_data' not in st.session_state:
    st.session_state.commits_data = []
if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False
if 'agent_analysis' not in st.session_state:
    st.session_state.agent_analysis = None
if 'agent_analysis_loading' not in st.session_state:
    st.session_state.agent_analysis_loading = False
if 'analysis_steps' not in st.session_state:
    st.session_state.analysis_steps = {
        "logs": {"status": "pending", "name": "System Logs Analysis"},
        "metrics": {"status": "pending", "name": "Performance Metrics Analysis"},
        "commits": {"status": "pending", "name": "Code Commits Analysis"}
    }

def check_api_status():
    """Check if the API is running and get monitoring status"""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def start_monitoring():
    """Start monitoring generation"""
    try:
        response = requests.post(START_ENDPOINT, timeout=5)
        return response.status_code == 200
    except:
        return False

def stop_monitoring():
    """Stop monitoring generation"""
    try:
        response = requests.post(STOP_ENDPOINT, timeout=5)
        return response.status_code == 200
    except:
        return False

def fetch_agent_analysis():
    """Fetch AI Agent analysis results"""
    try:
        response = requests.get(AGENT_ANALYSIS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch analysis: {e}"}

def update_analysis_steps(analysis_result):
    """Update analysis steps based on the current analysis content"""
    if not analysis_result or analysis_result.get("status") != "in_progress":
        return
    
    # Get the current analysis content
    analysis_content = analysis_result.get("analysis", {})
    
    # Initialize all steps as pending
    for step in st.session_state.analysis_steps:
        if st.session_state.analysis_steps[step]["status"] not in ["completed"]:
            st.session_state.analysis_steps[step]["status"] = "pending"
    
    # Analyze the content to determine which tools have been used
    if isinstance(analysis_content, dict):
        content_str = str(analysis_content).lower()
    elif isinstance(analysis_content, str):
        content_str = analysis_content.lower()
    else:
        return
    
    # Check for evidence of each tool being used
    if "logs" in content_str or "log analysis" in content_str or "error" in content_str:
        st.session_state.analysis_steps["logs"]["status"] = "completed"
    
    if "metrics" in content_str or "cpu" in content_str or "memory" in content_str or "performance" in content_str:
        st.session_state.analysis_steps["metrics"]["status"] = "completed"
        
    if "commit" in content_str or "code" in content_str or "repository" in content_str:
        st.session_state.analysis_steps["commits"]["status"] = "completed"
    
    # Determine current step based on what's completed
    completed_count = sum(1 for step in st.session_state.analysis_steps.values() if step["status"] == "completed")
    
    if completed_count == 0:
        st.session_state.analysis_steps["logs"]["status"] = "running"
    elif completed_count == 1 and st.session_state.analysis_steps["logs"]["status"] == "completed":
        st.session_state.analysis_steps["metrics"]["status"] = "running"
    elif completed_count == 2:
        st.session_state.analysis_steps["commits"]["status"] = "running"

def fetch_commits_data(repo=None, k=5, use_static=False):
    """Fetch commits data from API"""
    try:
        params = {"k": k, "use_static": use_static}
        if repo:
            params["repo"] = repo
            
        response = requests.get(COMMITS_ENDPOINT, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching commits: {e}")
        return None

def get_commits_info():
    """Get commits info from API"""
    try:
        response = requests.get(COMMITS_INFO_ENDPOINT, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_streaming_data():
    """Fetch data from streaming endpoints"""
    try:
        # Get a few logs
        response = requests.get(LOGS_STREAM, stream=True, timeout=2)
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        log_data = json.loads(line[6:])  # Remove 'data: ' prefix
                        st.session_state.logs_data.append(log_data)
                        # Keep only last 100 logs
                        if len(st.session_state.logs_data) > 100:
                            st.session_state.logs_data = st.session_state.logs_data[-100:]
                        break
                    except json.JSONDecodeError:
                        continue
        
        # Get a few metrics
        response = requests.get(METRICS_STREAM, stream=True, timeout=2)
        if response.status_code == 200:
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        metric_data = json.loads(line[6:])  # Remove 'data: ' prefix
                        st.session_state.metrics_data.append(metric_data)
                        # Keep only last 100 metrics
                        if len(st.session_state.metrics_data) > 50:
                            st.session_state.metrics_data = st.session_state.metrics_data[-50:]
                        break
                    except json.JSONDecodeError:
                        continue
        
    except:
        pass

def main():
    st.title("LogAgent Dashboard")
    st.markdown("---")
    
    if not st.session_state.commits_data:
        static_commits = fetch_commits_data(repo=None, k=5, use_static=True)
        if static_commits:
            st.session_state.commits_data = static_commits
    
    auto_refresh = False
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        
        # Check API status
        api_running, status_data = check_api_status()
        
        if api_running:
            st.success("API Connected")
            is_generating = status_data.get('is_generating', False)
            
            if is_generating:
                st.info("Monitoring Active")
                if st.button("Stop Monitoring", type="primary"):
                    if stop_monitoring():
                        st.success("Monitoring stopped!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("Monitoring Stopped")
                if st.button("Start Monitoring", type="primary"):
                    if start_monitoring():
                        st.success("Monitoring started!")
                        time.sleep(1)
                        st.rerun()
                        st.rerun()
        else:
            st.error("API Not Available")
            st.markdown("Make sure the FastAPI server is running on port 8000")
        
        st.markdown("---")
        
        if api_running:
            st.subheader("AI Analysis")
            if st.button("Run Root Cause Analysis", type="primary", help="Manually trigger comprehensive root cause analysis"):
                try:
                    response = requests.post(f"{API_BASE}/trigger-analysis")
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == "started":
                            st.success("Root cause analysis started!")
                            st.session_state.agent_analysis_loading = True
                            # Reset analysis steps for new analysis
                            st.session_state.analysis_steps = {
                                "logs": {"status": "pending", "name": "System Logs Analysis"},
                                "metrics": {"status": "pending", "name": "Performance Metrics Analysis"},
                                "commits": {"status": "pending", "name": "Code Commits Analysis"}
                            }
                        else:
                            st.warning(result.get("message", "Unknown response"))
                    else:
                        st.error("Failed to trigger analysis")
                except Exception as e:
                    st.error(f"Error triggering analysis: {e}")
        
        # Auto-refresh controls
        auto_refresh = st.checkbox("Auto Refresh", value=auto_refresh)
            
        st.markdown("---")
        st.subheader("Commit Analysis")
        
        # Repository URL input
        repo_input = st.text_input("Repository URL (optional)", placeholder="https://github.com/user/repo.git")
        
        if st.button("Fetch Repository Commits"):
            if repo_input.strip():
                with st.spinner("Fetching repository commits..."):
                    # Fetch from the provided repository
                    commits_result = fetch_commits_data(repo=repo_input.strip(), k=10, use_static=False)
                    if commits_result and commits_result.get('commits'):
                        st.session_state.commits_data = commits_result
                        st.success(f"Fetched {len(commits_result.get('commits', []))} commits from repository")
                    else:
                        st.error("Failed to fetch commits from repository")
            else:
                st.warning("Please enter a repository URL")
                
        # Button to reload static commits
        if st.button("Load Static Commits"):
            with st.spinner("Loading static commits..."):
                static_commits = fetch_commits_data(repo=None, k=10, use_static=True)
                if static_commits:
                    st.session_state.commits_data = static_commits
                    st.success(f"Loaded {len(static_commits.get('commits', []))} static commits")
                else:
                    st.error("Failed to load static commits")
        
        st.markdown("---")
        
        # Clear data button
        if st.button("Clear Data"):
            st.session_state.logs_data = []
            st.session_state.metrics_data = []
            st.session_state.commits_data = []
            st.rerun()
    
    # Main content area
    if api_running:
        # Fetch new data if auto-refresh is enabled
        if auto_refresh:
            fetch_streaming_data()
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Dashboard", "Commits", "AI Agent Analysis"])
        
        # Tab 1: Dashboard (Logs and Metrics)
        with tab1:
            # Create two columns for logs and metrics
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.header("Recent Logs")
                
                if st.session_state.logs_data:
                    # Create DataFrame from logs
                    logs_df = pd.DataFrame(st.session_state.logs_data)
                    
                    # Display log count and filters
                    st.metric("Total Logs", len(st.session_state.logs_data))
                    
                    # Log level filter
                    log_levels = logs_df['level'].unique() if 'level' in logs_df.columns else []
                    selected_levels = st.multiselect("Filter by Log Level", log_levels, default=log_levels)
                    
                    # Filter logs
                    if selected_levels:
                        filtered_logs = logs_df[logs_df['level'].isin(selected_levels)]
                    else:
                        filtered_logs = logs_df
                    
                    # Display recent logs
                    for idx, log in filtered_logs.tail(10).iterrows():
                        level = log.get('level', 'INFO')
                        timestamp = log.get('timestamp', '')[:19]  # Trim microseconds
                        status_code = log.get('status_code', 'N/A')
                        endpoint = log.get('endpoint', '')
                        user = log.get('user', '')
                        
                        # Color code based on log level
                        if level == 'ERROR':
                            st.error(f"**{timestamp}** | {level} | {status_code} | {endpoint} | User: {user}")
                        elif level == 'WARNING':
                            st.warning(f"**{timestamp}** | {level} | {status_code} | {endpoint} | User: {user}")
                        else:
                            st.info(f"**{timestamp}** | {level} | {status_code} | {endpoint} | User: {user}")
                else:
                    st.info("No logs available yet. Start monitoring to see data.")
            
            with col2:
                st.header("System Metrics")
                
                if st.session_state.metrics_data:
                    # Create DataFrame from metrics
                    metrics_df = pd.DataFrame(st.session_state.metrics_data)
                    
                    if not metrics_df.empty:
                        # Convert timestamp to datetime
                        metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
                        
                        # Display current metrics
                        latest_metric = metrics_df.iloc[-1]
                        
                        # Metrics cards
                        metric_col1, metric_col2 = st.columns(2)
                        with metric_col1:
                            st.metric(
                                "CPU Usage", 
                                f"{latest_metric.get('cpu_percent', 0):.1f}%",
                                delta=None
                            )
                            st.metric(
                                "Memory Usage", 
                                f"{latest_metric.get('memory_percent', 0):.1f}%",
                                delta=None
                            )
                        
                        with metric_col2:
                            st.metric(
                                "Memory Used", 
                                f"{latest_metric.get('memory_used_mb', 0)} MB",
                                delta=None
                            )
                            st.metric(
                                "Total Memory", 
                                f"{latest_metric.get('memory_total_mb', 0)} MB",
                                delta=None
                            )
                        
                        # Create time series chart
                        fig = make_subplots(
                            rows=2, cols=1,
                            subplot_titles=('CPU Usage Over Time', 'Memory Usage Over Time'),
                            vertical_spacing=0.25
                        )
                        
                        # CPU chart
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_df['timestamp'],
                                y=metrics_df['cpu_percent'],
                                mode='lines+markers',
                                name='CPU %',
                                line=dict(color='#ff6b6b', width=2),
                                marker=dict(size=4)
                            ),
                            row=1, col=1
                        )
                        
                        # Memory chart
                        fig.add_trace(
                            go.Scatter(
                                x=metrics_df['timestamp'],
                                y=metrics_df['memory_percent'],
                                mode='lines+markers',
                                name='Memory %',
                                line=dict(color='#4ecdc4', width=2),
                                marker=dict(size=4)
                            ),
                            row=2, col=1
                        )
                        
                        # Update layout
                        fig.update_layout(
                            height=600,
                            showlegend=False,
                            title_text="System Performance Metrics",
                            margin=dict(t=80, b=80, l=50, r=50)
                        )
                        fig.update_xaxes(title_text="Time", row=2, col=1)
                        fig.update_yaxes(title_text="CPU %", row=1, col=1)
                        fig.update_yaxes(title_text="Memory %", row=2, col=1)
                        
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No metrics available yet. Start monitoring to see data.")
        
        # Tab 2: Commits
        with tab2:
            st.header("Commits")
            
            if st.session_state.commits_data:
                commits_info = st.session_state.commits_data
                commits = commits_info.get('commits', [])
                
                if commits:
                    # Display simple commit count
                    st.metric("Total Commits", len(commits))
                    
                    # Show commits list
                    st.subheader("Recent Commits")
                    for i, commit in enumerate(commits[:10]):  # Show latest 10
                        with st.expander(f"#{i+1} - {commit.get('hash', 'N/A')[:8]} - {commit.get('message', 'No message')[:50]}..."):
                            st.write(f"**Hash:** `{commit.get('hash', 'N/A')}`")
                            st.write(f"**Message:** {commit.get('message', 'No message')}")
                            
                            files = commit.get('files', [])
                            if files:
                                st.write(f"**Files Modified:** {len(files)}")
                                for file in files:
                                    st.write(f"- `{file.get('filename', 'unknown')}`")
                                    if file.get('code'):
                                        with st.expander(f"View code: {file.get('filename', 'unknown')}"):
                                            st.code(file['code'], language='python')
                else:
                    st.info("No commits data available.")
            else:
                st.info("Loading static commits...")
                # Try to load static commits if not already loaded
                static_commits = fetch_commits_data(repo=None, k=5, use_static=True)
                if static_commits:
                    st.session_state.commits_data = static_commits
                    st.rerun()
        
        # Tab 3: AI Agent Analysis
        with tab3:
            st.header("Comprehensive Root Cause Analysis")
            
            # Automatically fetch and update analysis status
            analysis_result = fetch_agent_analysis()
            if analysis_result:
                st.session_state.agent_analysis = analysis_result
                if analysis_result.get("status") == "in_progress":
                    st.session_state.agent_analysis_loading = True
                    update_analysis_steps(analysis_result)
                elif analysis_result.get("status") == "completed":
                    st.session_state.agent_analysis_loading = False
                    # Mark all steps as completed
                    for step in st.session_state.analysis_steps:
                        st.session_state.analysis_steps[step]["status"] = "completed"
                if st.session_state.agent_analysis_loading:
                    st.warning("Comprehensive Root Cause Analysis in Progress")
                    
                    # Use st.status to show detailed analysis steps
                    with st.status("AI Agent Root Cause Analysis", expanded=True) as status:
                        for step_key, step_info in st.session_state.analysis_steps.items():
                            step_name = step_info["name"]
                            step_status = step_info["status"]
                            
                            if step_status == "completed":
                                st.success(f"{step_name} - Completed")
                            elif step_status == "running":
                                st.info(f"{step_name} - Currently analyzing...")
                            else:  # pending
                                st.write(f"{step_name} - Waiting to start")
                        
                        # Show overall status
                        completed_steps = sum(1 for step in st.session_state.analysis_steps.values() if step["status"] == "completed")
                        total_steps = len(st.session_state.analysis_steps)
                        
                        if completed_steps == total_steps:
                            st.success(f"Analysis complete! All {total_steps} tools have finished.")
                            status.update(label="Analysis Complete ✅", state="complete", expanded=False)
                        else:
                            running_steps = [step["name"] for step in st.session_state.analysis_steps.values() if step["status"] == "running"]
                            if running_steps:
                                current_step = running_steps[0]
                                status.update(label=f"Running: {current_step}", state="running")
                            else:
                                status.update(label="Initializing analysis...", state="running")
                    
                elif st.session_state.agent_analysis:
                    analysis_data = st.session_state.agent_analysis
                    if analysis_data.get("status") == "completed":
                        st.success("Comprehensive root cause analysis completed!")
                        
                        # Display analysis in a structured format for RCA
                        analysis_content = analysis_data.get("analysis", {})
                        
                        # Check if analysis_content has the 'output' key (LangChain agent result format)
                        if isinstance(analysis_content, dict) and 'output' in analysis_content:
                            analysis_text = analysis_content['output']
                        elif isinstance(analysis_content, str):
                            analysis_text = analysis_content
                        else:
                            analysis_text = str(analysis_content)
                                                
                        # Try to parse structured RCA format
                        rca_sections = {
                            "Timeline": ["Timeline:", "Error Timeline:"],
                            "Root Cause Indicators": ["Root Cause Indicators:", "Root Causes:"],
                            "Risk Factors": ["Risk Factors:", "Correlation:", "Performance Anomalies:"],
                            "System Impact": ["System Impact:", "Technical Impact:", "Failure Patterns:"],
                            "Recurring Patterns": ["Recurring Patterns:", "System Vulnerabilities:"],
                            "Resource Constraints": ["Resource Constraints:", "Trend Analysis:"],
                            "Trigger Conditions": ["Trigger Conditions:", "Correlation Indicators:"]
                        }
                        
                        st.markdown("### Root Cause Analysis Results")
                        st.markdown(analysis_text)
                        
                        
                    elif analysis_data.get("status") == "in_progress":
                        st.warning("Comprehensive root cause analysis in progress...")
                        st.info("The AI Agent is systematically analyzing all data sources. This may take a few moments.")
                        
                    elif analysis_data.get("status") == "error":
                        st.error(f"Analysis error: {analysis_data.get('message', 'Unknown error')}")
                else:
                    # No analysis available - show manual trigger instructions
                    st.info("**Manual Root Cause Analysis**")
                    st.markdown("""
                    **To perform comprehensive analysis:**
                    1. Click the "Run Root Cause Analysis" button in the sidebar
                    2. The AI Agent will analyze all available data sources
                    3. Results will appear here when analysis is complete
                    """)
                    
                    st.markdown("---")
                    st.info("**Use the 'Run Root Cause Analysis' button in the sidebar to start analysis**")
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(3) 
            st.rerun()
    
    else:
        st.error("Cannot connect to the API")
        st.markdown("""
        **To fix this:**
        1. Make sure your FastAPI server is running
        2. Navigate to the Backend directory
        3. Run: `uvicorn main:app --reload`
        4. Refresh this page
        """)

if __name__ == "__main__":
    main()