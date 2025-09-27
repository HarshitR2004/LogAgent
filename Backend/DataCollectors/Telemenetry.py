import asyncio
import websockets
import random
import datetime
import json
from faker import Faker

class TelemetryGenerator:
    def __init__(self, host="localhost", port=8765, min_delay=0.3, max_delay=1.5, callback=None):
        self.host = host
        self.port = port
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.fake = Faker()
        self.server = None
        self.callback = callback
        self.log_buffer = asyncio.Queue()
        self.metric_buffer = asyncio.Queue()
        self.is_running = False
        self.generator_task = None

        # Users for logs
        self.users = [{"username": self.fake.user_name(), "ip": self.fake.ipv4_public()} for _ in range(20)]

        # Weighted status codes
        self.status_codes = [200, 200, 200, 200, 201, 400, 401, 403, 404, 500]

        # Endpoints
        self.endpoints = [
            ("/api/v1/users", ["GET", "POST"]),
            ("/api/v1/login", ["POST"]),
            ("/api/v1/orders", ["GET", "POST"]),
            ("/health", ["GET"]),
            ("/", ["GET"]),
        ]


    def _choose_log_level(self, status):
        if status >= 500:
            return "ERROR"
        elif status >= 400:
            return "WARNING"
        else:
            return random.choices(["INFO", "DEBUG"], weights=[0.8, 0.2], k=1)[0]

    async def _generate_log(self):
        user = random.choice(self.users)
        endpoint, methods = random.choice(self.endpoints)
        method = random.choice(methods)
        status = random.choice(self.status_codes)

        # Correlate CPU spike with errors
        cpu_spike = status >= 500
        
        # Generate message with occasional error keywords (low probability)
        error_keywords = ["error", "failed", "exception", "critical"]
        
        # Base messages for different scenarios
        base_messages = [
            f"Request to {endpoint} completed",
            f"Processing {method} request",
            f"User {user['username']} accessed {endpoint}",
            f"API call from {user['ip']}",
            f"Handling {method} {endpoint}",
            f"Request processed successfully",
            f"API response sent",
            f"Service request completed"
        ]
        
        if random.random() < 0.20:
            error_word = random.choice(error_keywords)
            message = f"{random.choice(base_messages)} - {error_word} occurred"
        else:
            message = random.choice(base_messages)

        log = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": self._choose_log_level(status),
            "user": user["username"],
            "ip": user["ip"],
            "method": method,
            "endpoint": endpoint,
            "status_code": status,
            "request_id": self.fake.uuid4(),
            "latency_ms": max(1, int(random.gauss(120, 40) + (50 if cpu_spike else 0))),
            "cpu_spike": cpu_spike,
            "message": message
        }
        return log

   
    async def _generate_metric(self, correlate_cpu=False):
        base_cpu = random.gauss(30, 10)
        base_mem = random.gauss(50, 15)

        if correlate_cpu:
            base_cpu += random.randint(20, 30)  # spike during errors

        metric = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "cpu_percent": min(max(base_cpu, 0), 100),
            "memory_percent": min(max(base_mem, 0), 100),
            "memory_used_mb": random.randint(2000, 8000),
            "memory_total_mb": 8192
        }
        return metric


    async def _generator_loop(self, websocket, log_interval=0.5, metric_interval=0.3):
        while self.is_running:
            # Generate log
            log = await self._generate_log()
            await self.log_buffer.put(log)
            if self.callback:
                self.callback("log", log)
            if websocket:
                await websocket.send(json.dumps({"type": "log", "data": log}))

            # Generate metric (correlate CPU spike with log)
            metric = await self._generate_metric(correlate_cpu=log["cpu_spike"])
            await self.metric_buffer.put(metric)
            if self.callback:
                self.callback("metric", metric)
            if websocket:
                await websocket.send(json.dumps({"type": "metric", "data": metric}))

            await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))

  
    async def _start_async(self):
        self.server = await websockets.serve(self._generator_loop, self.host, self.port)
        print(f"Telemetry generator started at ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    def start(self):
        asyncio.run(self._start_async())

    def start_generation(self):
        """Start the telemetry generation process"""
        if not self.is_running:
            self.is_running = True
            print("Telemetry generation started")

    def stop_generation(self):
        """Stop the telemetry generation process"""
        if self.is_running:
            self.is_running = False
            print("Telemetry generation stopped")

    def is_generating(self):
        """Check if telemetry is currently being generated"""
        return self.is_running


    async def get_log(self):
        return await self.log_buffer.get()

    async def get_metric(self):
        return await self.metric_buffer.get()




