import asyncio
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from DataCollectors.Telemenetry import TelemetryGenerator
from DataCollectors.CommitsCollector import CommitsCollector
from Services.LogFilter import LogFilter
from Services.CollectMetrics import MetricsCollector
from Services.EventDetection import EventDetection

app = FastAPI()
generator = TelemetryGenerator(min_delay=0.2, max_delay=0.8)
log_filter = LogFilter()
metrics_collector = MetricsCollector()
event_detector = EventDetection()

def telemetry_callback(data_type, data):
    # Always process the data first, then check for events
    if data_type == "log":
        log_filter.filter_logs(data)
        
        # Check for log-based events and stop if detected
        if event_detector.detect_from_log(data):
            print(f"EVENT DETECTED IN LOG - STOPPING TELEMETRY")
            generator.stop_generation()
    
    elif data_type == "metric":
        metrics_collector.collect_metric(data)
        
        # Check for metric-based events and stop if detected
        if event_detector.detect_from_metric(data):
            print(f"EVENT DETECTED IN METRICS - STOPPING TELEMETRY")
            generator.stop_generation()

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
        # If use_static is True or no repo provided, use static data
        if use_static or not repo:
            collector = CommitsCollector("")
            commits = collector.get_commits_from_json(k)
            return {"commits": commits}
        
        # Try to use real repository
        collector = CommitsCollector(repo)
        try:
            commits_data = collector.get_last_k_commits(k)
            return {"commits": commits_data}
        except Exception as repo_error:
            print(f"Repository access failed: {repo_error}")
            # Fallback to static data
            commits = collector.get_commits_from_json(k)
            return {"commits": commits}
    
    except Exception as e:
        return {"commits": []}


@app.get("/commits/info")
async def get_commits_info():
    """Get information about available commit data sources"""
    # Check if static data exists
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
   

@app.get("/")
async def health():
    return {"status": "ok"}