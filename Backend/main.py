import asyncio
import json
import sys
import os
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from DataCollectors.Telemenetry import TelemetryGenerator
from DataCollectors.CommitsCollector import CommitsCollector
from Services.LogFilter import LogFilter
from Services.CollectMetrics import MetricsCollector
from Services.EventDetection import EventDetection

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'AI'))
from Agent import Agent

app = FastAPI()
generator = TelemetryGenerator(min_delay=0.2, max_delay=0.8)
log_filter = LogFilter()
metrics_collector = MetricsCollector()
event_detector = EventDetection()

ai_agent = Agent()
agent_analysis_result = None
analysis_in_progress = False 

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
        print(f"DEBUG: Raw agent result: {result}")
        
        if isinstance(result, dict) and 'output' in result:
            agent_analysis_result = result['output']
            print(f"DEBUG: Extracted output: {agent_analysis_result}")
        else:
            agent_analysis_result = str(result)
            print(f"DEBUG: Converted to string: {agent_analysis_result}")
            
        print("Comprehensive AI Agent root cause analysis completed!")
        print(f"DEBUG: Final agent_analysis_result is None: {agent_analysis_result is None}")
        print(f"DEBUG: Final agent_analysis_result length: {len(str(agent_analysis_result)) if agent_analysis_result else 0}")
        
    except Exception as e:
        print(f"Error running AI Agent analysis: {e}")
        agent_analysis_result = f"Error during root cause analysis: {e}"
    finally:
        analysis_in_progress = False

def start_agent_analysis_background():
    """Start agent analysis as a background task"""
    asyncio.create_task(run_agent_analysis())

def telemetry_callback(data_type, data):
    # Just collect data without automatic analysis triggers
    if data_type == "log":
        log_filter.filter_logs(data)
    elif data_type == "metric":
        metrics_collector.collect_metric(data)

async def generator_loop():
    await generator._generator_loop(websocket=None)
    
@app.on_event("startup")
async def startup_event():
    generator.callback = telemetry_callback
    generator.start_generation()
    asyncio.create_task(generator_loop())

async def log_event_stream():
    while True:
        log = await generator.get_log()
        yield f"data: {json.dumps(log)}\n\n"

@app.get("/logs")
async def stream_logs():
    return StreamingResponse(log_event_stream(), media_type="text/event-stream")

async def metric_event_stream():
    while True:
        metric = await generator.get_metric()
        yield f"data: {json.dumps(metric)}\n\n"

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
    generator.stop_generation()
    return {"status": "stopped", "message": "Telemetry generation stopped"}

@app.post("/start")
async def start_telemetry():
    generator.start_generation()
    return {"status": "started", "message": "Telemetry generation started"}

@app.get("/status")
async def get_status():
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
            "message": "Root cause analysis is currently running. Analysis uses all 4 tools: commits, logs, metrics, and past events.",
            "analysis": None
        }
    
    if agent_analysis_result is None:
        return {
            "status": "no_analysis",
            "message": "No root cause analysis available. Use the 'Run Root Cause Analysis' button to trigger manual analysis.",
            "analysis": None
        }
    
    return {
        "status": "completed",
        "message": "Comprehensive root cause analysis completed using all analysis tools",
        "analysis": agent_analysis_result
    }

@app.post("/trigger-analysis")
async def trigger_analysis_manually():
    """Manually trigger agent analysis for testing"""
    if analysis_in_progress:
        return {"status": "error", "message": "Analysis already in progress"}
    
    start_agent_analysis_background()
    return {"status": "started", "message": "Agent analysis started in background"}

@app.get("/")
async def health():
    return {"status": "ok"}