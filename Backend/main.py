import asyncio
import json
import sys
import os
import random
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from DataCollectors.Telemenetry import TelemetryGenerator
from DataCollectors.CommitsCollector import CommitsCollector
from Services.LogFilter import LogFilter
from Services.CollectMetrics import MetricsCollector
from Services.EventDetection import EventDetection

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'AI'))
from Agent import Agent

app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
generator = TelemetryGenerator(min_delay=0.2, max_delay=0.8)
log_filter = LogFilter()
metrics_collector = MetricsCollector()
event_detector = EventDetection()

ai_agent = Agent()
agent_analysis_result = None
analysis_in_progress = False
telemetry_auto_stopped = False  # Track internal auto-stop state 

async def run_agent_analysis():
    global agent_analysis_result, analysis_in_progress
    
    # Prevent multiple simultaneous analyses
    if analysis_in_progress:
        print("Agent analysis already in progress - skipping")
        return
    
    analysis_in_progress = True
    try:
        print("Starting comprehensive AI Agent root cause analysis...")
        
        # Run the agent in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, ai_agent.invoke)
        
        print(f"DEBUG: Raw agent result type: {type(result)}")
        print(f"DEBUG: Raw agent result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Handle the new sequential execution result format
        if isinstance(result, dict):
            if 'error' in result:
                # Handle error case
                error_msg = result['error']
                partial_results = result.get('partial_results', {})
                print(f"Agent analysis error: {error_msg}")
                print(f"Partial results available: {list(partial_results.keys())}")
                
                # Try to use partial results if available
                if partial_results.get('root_cause_analysis'):
                    agent_analysis_result = partial_results['root_cause_analysis']
                    print("Using partial root cause analysis from error result")
                else:
                    agent_analysis_result = f"Analysis partially completed with error: {error_msg}. Partial results: {partial_results}"
                    
            elif 'output' in result:
                # Handle successful result
                agent_analysis_result = result['output']
                intermediate_steps = result.get('intermediate_steps', [])
                print(f"DEBUG: Analysis completed successfully")
                print(f"DEBUG: Intermediate steps: {[step[0] for step in intermediate_steps]}")
                print(f"DEBUG: Final analysis length: {len(str(agent_analysis_result))}")
                
            else:
                # Fallback for unexpected format
                agent_analysis_result = str(result)
                print(f"DEBUG: Unexpected result format, converted to string")
        else:
            agent_analysis_result = str(result)
            print(f"DEBUG: Result was not a dict, converted to string")
            
        print("Comprehensive AI Agent root cause analysis completed!")
        print(f"DEBUG: Final agent_analysis_result is None: {agent_analysis_result is None}")
        print(f"DEBUG: Final agent_analysis_result length: {len(str(agent_analysis_result)) if agent_analysis_result else 0}")
        
    except Exception as e:
        print(f"Error running AI Analysis: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        agent_analysis_result = f"Error during root cause analysis: {e}"
    finally:
        analysis_in_progress = False

def start_agent_analysis_background():
    """Start agent analysis as a background task"""
    asyncio.create_task(run_agent_analysis())

def telemetry_callback(data_type, data):
    """Handle telemetry data - save to files in background"""
    try:
        if data_type == "log":
            log_filter.filter_logs(data)
        elif data_type == "metric":
            metrics_collector.collect_metric(data)
    except Exception as e:
        print(f"Error in telemetry callback: {e}")

async def auto_stop_telemetry():
    """Automatically stop telemetry generation after 10 seconds"""
    global telemetry_auto_stopped
    
    print("Starting 10-second telemetry collection...")
    await asyncio.sleep(10)  # Wait for 10 seconds
    
    print("10 seconds elapsed - automatically stopping telemetry generation")
    generator.stop_generation()
    telemetry_auto_stopped = True
    print("Telemetry data collection completed and saved to files")
    print("Note: Frontend will continue showing 'running' status but no new data will be generated")

async def generator_loop():
    """Run the telemetry generator loop"""
    print("Starting telemetry generator loop...")
    try:
        # Run the generator loop without websocket
        while generator.is_running:
            # Generate log
            log = await generator._generate_log()
            await generator.log_buffer.put(log)
            if generator.callback:
                generator.callback("log", log)
            print(f"Generated log: {log.get('message', 'No message')} (Status: {log.get('status_code', 'N/A')})")

            # Generate metric (correlate CPU spike with log)
            metric = await generator._generate_metric(correlate_cpu=log.get("cpu_spike", False))
            await generator.metric_buffer.put(metric)
            if generator.callback:
                generator.callback("metric", metric)
            print(f"Generated metric: CPU={metric.get('cpu_percent', 0):.1f}% Memory={metric.get('memory_percent', 0):.1f}%")

            await asyncio.sleep(random.uniform(generator.min_delay, generator.max_delay))
            
        print("Generator loop stopped (is_running=False)")
    except Exception as e:
        print(f"Error in generator loop: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
    
@app.on_event("startup")
async def startup_event():
    print("=== APPLICATION STARTUP ===")
    generator.callback = telemetry_callback
    print("Setting up telemetry callback")
    
    print("Starting telemetry generation...")
    generator.start_generation()
    
    print("Creating generator loop task...")
    asyncio.create_task(generator_loop())
    
    print("Creating auto-stop timer task...")
    asyncio.create_task(auto_stop_telemetry())
    
    print("=== STARTUP COMPLETE ===")
    print("Telemetry should now be generating data for 10 seconds")

async def log_event_stream():
    """Stream logs in real-time during generation, then stop"""
    print("=== LOG STREAMING STARTED ===")
    log_count = 0
    while True:
        try:
            # Always try to get real-time logs from the generator
            print(f"Waiting for log data... (count: {log_count})")
            log = await asyncio.wait_for(generator.get_log(), timeout=2.0)
            print(f"Got log data: {log}")
            log_count += 1
            yield f"data: {json.dumps(log)}\n\n"
        except asyncio.TimeoutError:
            # If no logs available, send keep-alive
            print("No log data available, sending keep-alive")
            yield f"data: {json.dumps({'message': 'Waiting for logs...', 'timestamp': '', 'level': 'INFO'})}\n\n"
            await asyncio.sleep(0.5)

@app.get("/logs")
async def stream_logs():
    return StreamingResponse(log_event_stream(), media_type="text/event-stream")

async def metric_event_stream():
    """Stream metrics in real-time during generation, then stop"""
    print("=== METRICS STREAMING STARTED ===")
    metric_count = 0
    while True:
        try:
            # Always try to get real-time metrics from the generator
            print(f"Waiting for metric data... (count: {metric_count})")
            metric = await asyncio.wait_for(generator.get_metric(), timeout=2.0)
            print(f"Got metric data: {metric}")
            metric_count += 1
            yield f"data: {json.dumps(metric)}\n\n"
        except asyncio.TimeoutError:
            # If no metrics available, send keep-alive with sample data
            print("No metric data available, sending keep-alive")
            yield f"data: {json.dumps({'cpu': 0, 'memory': 0, 'message': 'Waiting for metrics...', 'timestamp': ''})}\n\n"
            await asyncio.sleep(0.5)

@app.get("/metrics")
async def stream_metrics():
    return StreamingResponse(metric_event_stream(), media_type="text/event-stream")


@app.get("/commits")
async def collect_commits(repo: str = None, k: int = 3, use_static: bool = False):
    
    try:
        if use_static or not repo:
            collector = CommitsCollector("")
            commits = collector.get_commits_from_json(k)
            return {"commits": commits}
        
        collector = CommitsCollector(repo)
        try:
            commits_data = collector.get_last_k_commits(k)
            return {"commits": commits_data}
        except Exception as repo_error:
            print(f"Repository access failed: {repo_error}")
            commits = collector.get_commits_from_json(k)
            return {"commits": commits}
    
    except Exception as e:
        return {"commits": []}


@app.get("/commits/info")
async def get_commits_info():
    static_data_available = False
    static_commit_count = 0
    try:
        path_obj = Path("data/commit.json")
        if path_obj.exists():
            with open(path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)
            static_commit_count = len(data.get("commits", []))
            static_data_available = True
    except Exception:
        pass
    
    return {
        "static_data_available": static_data_available,
        "static_commit_count": static_commit_count,
        "usage_examples": {
            "use_static_data": "/commits?use_static=true&k=5",
            "try_repo_fallback_static": "/commits?repo=https://github.com/user/repo.git&k=3",
            "force_static_with_repo": "/commits?repo=my-repo&use_static=true&k=10"
        }
    }


@app.post("/stop")
async def stop_telemetry():
    global telemetry_auto_stopped
    
    generator.stop_generation()
    telemetry_auto_stopped = False  # Reset auto-stop state when manually stopped
    return {"status": "stopped", "message": "Telemetry generation stopped"}

@app.post("/start")
async def start_telemetry():
    global telemetry_auto_stopped
    
    generator.start_generation()
    telemetry_auto_stopped = False  # Reset auto-stop state when manually started
    
    # Start a new 10-second auto-stop timer
    asyncio.create_task(auto_stop_telemetry())
    
    return {"status": "started", "message": "Telemetry generation started"}

@app.get("/status")
async def get_status():
    global telemetry_auto_stopped
    
    # If telemetry was auto-stopped internally, still show as "running" to frontend
    if telemetry_auto_stopped:
        return {
            "status": "running",  # Hide the auto-stop from frontend
            "is_generating": True  # Frontend thinks it's still generating
        }
    
    # Normal status check
    return {
        "status": "running" if generator.is_generating() else "stopped",
        "is_generating": generator.is_generating()
    }

@app.get("/agent-analysis")
async def get_agent_analysis():
    """Get the comprehensive AI Agent root cause analysis results"""
    global agent_analysis_result, analysis_in_progress
    
    # Debug logging
    print(f"DEBUG: analysis_in_progress={analysis_in_progress}")
    print(f"DEBUG: agent_analysis_result is None: {agent_analysis_result is None}")
    if agent_analysis_result:
        print(f"DEBUG: agent_analysis_result length: {len(str(agent_analysis_result))}")
    
    if analysis_in_progress:
        return {
            "status": "in_progress",
            "message": "Root cause analysis is currently running. Sequential execution: Step 1 (Logs) → Step 2 (Metrics) → Step 3 (Commits) → Step 4 (Final Analysis)",
            "analysis": None
        }
    
    if agent_analysis_result is None:
        return {
            "status": "no_analysis",
            "message": "No root cause analysis available. Use the 'Run Root Cause Analysis' button to trigger sequential analysis of logs, metrics, and commits.",
            "analysis": None
        }
    
    return {
        "status": "completed",
        "message": "Sequential root cause analysis completed: Logs → Metrics → Commits → Final Analysis",
        "analysis": agent_analysis_result
    }

@app.post("/trigger-analysis")
async def trigger_analysis_manually():
    """Manually trigger agent analysis for testing"""
    if analysis_in_progress:
        return {
            "status": "error", 
            "message": "Analysis already in progress - sequential execution is running"
        }
    
    start_agent_analysis_background()
    return {
        "status": "started", 
        "message": "Sequential root cause analysis started: Logs → Metrics → Commits → Final Analysis"
    }

@app.get("/")
async def health():
    return {"status": "ok"}