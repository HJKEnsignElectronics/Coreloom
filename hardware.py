# hardware.py
import psutil
import docker
from typing import Tuple
from utils import logger

class VirtualizationEngine:
    """
    Calculates CPU density and provisions Docker containers acting as Virtual Cores.
    """
    def __init__(self):
        try:
            self.docker_client = docker.from_env()
            logger.info("Connected to Docker Daemon successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            self.docker_client = None

    def get_cluster_density(self) -> dict:
        """
        Reads physical hardware density. 
        In a 10-node setup, this would aggregate psutil data from all 10 nodes.
        """
        physical_cores = psutil.cpu_count(logical=False)
        logical_threads = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            "physical_cores": physical_cores,
            "logical_threads": logical_threads,
            "base_frequency_mhz": cpu_freq.current if cpu_freq else 3000.0,
            "total_density_score": physical_cores * (cpu_freq.current if cpu_freq else 3000.0)
        }

    def synthesize_virtual_cores(self, requested_compute_percent: float) -> int:
        """
        Converts requested compute % into actual thread allocations (Virtual Cores/Coins).
        """
        density = self.get_cluster_density()
        # Simulate a 10-node cluster by multiplying local threads by 10
        cluster_threads = density["logical_threads"] * 10 
        
        available_threads = int(cluster_threads * (requested_compute_percent / 100))
        # Cap at a reasonable number for local testing, but logic remains for distributed
        return min(available_threads, 32) 

    def provision_container(self, virtual_cores: int, rom_percent: float) -> str:
        """
        Spins up an isolated Docker container injected with the specific CPU density.
        """
        if not self.docker_client:
            raise RuntimeError("Docker daemon is not connected.")

        # Calculate Docker CPU limits (1 CPU = 1,000,000,000 nano_cpus)
        # We allocate a fraction of a CPU based on the virtual cores requested
        nano_cpus = int((virtual_cores / 10) * 1e9) 
        
        # Memory limit based on ROM/Storage request (simulated)
        mem_limit = f"{max(int(rom_percent * 5), 128)}m" 

        try:
            logger.info(f"Provisioning container: {virtual_cores} v-cores, {mem_limit} memory.")
            container = self.docker_client.containers.run(
                "alpine:latest",
                command="sh -c 'while true; do echo \"CoreLoom processing...\"; sleep 5; done'",
                detach=True,
                nano_cpus=nano_cpus,
                mem_limit=mem_limit,
                name=f"coreloom_node_{virtual_cores}"
            )
            return container.id
        except Exception as e:
            logger.error(f"Container provisioning failed: {e}")
            raise

# Global engine instance
engine = VirtualizationEngine()
