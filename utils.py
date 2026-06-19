# utils.py
import logging
import time
from typing import Dict
from models import TelemetryData

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CoreLoom Collector - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CoreLoom_Collector")

class Collector:
    """
    The Collector monitors the speed, usage, and efficiency of virtualized processors.
    In a full distributed setup, this would poll remote nodes. Here, it polls local Docker stats.
    """
    def __init__(self):
        self.active_monitors: Dict[str, dict] = {}

    def start_monitoring(self, container_id: str):
        logger.info(f"Starting telemetry collection for container: {container_id}")
        self.active_monitors[container_id] = {
            "start_time": time.time(),
            "status": "running"
        }

    def get_telemetry(self, container_id: str, docker_client) -> TelemetryData:
        """Polls Docker for real-time stats and formats for the frontend."""
        try:
            container = docker_client.containers.get(container_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU %
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                        stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                           stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
            
            # Calculate Memory %
            mem_usage = stats['memory_stats']['usage']
            mem_limit = stats['memory_stats']['limit']
            mem_percent = (mem_usage / mem_limit) * 100.0

            return TelemetryData(
                container_id=container_id[:12],
                cpu_usage=round(cpu_percent, 2),
                memory_usage=round(mem_percent, 2),
                thread_speed_mhz=3500.0, # Simulated thread speed
                status="running"
            )
        except Exception as e:
            logger.error(f"Telemetry error for {container_id}: {str(e)}")
            return TelemetryData(
                container_id=container_id[:12], cpu_usage=0, memory_usage=0, 
                thread_speed_mhz=0, status="error"
            )

# Global collector instance
collector = Collector()
