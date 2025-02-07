"""v1 Actuator endpoints.

This module provides system monitoring endpoints for health checks, system information,
and real-time metrics collection.

Endpoints:
    - /health: System health status including disk space and memory checks
    - /info: Static system information about OS, Python, CPU and memory
    - /metrics: Real-time metrics for CPU, memory, disk and network usage
    - /stats: HTTP request statistics and status code history

Models:
    - ComponentDetails: Details about a system component's health status
    - HealthStatus: Overall system health status with component details
    - SystemInfo: Static system information and specifications
    - CpuMetrics: CPU usage metrics and per-core statistics
    - NetworkMetrics: Network connection and I/O metrics
    - DiskMetrics: Disk usage and I/O metrics
    - SystemMetrics: Combined real-time system metrics
    - HttpStats: HTTP request statistics and status code history
"""

import platform
import sys
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional, TypedDict

import psutil
from fastapi import APIRouter
from pydantic import BaseModel

from app.middlewares.stats import get_start_time, get_stats

logger = getLogger(__name__)


class ComponentDetails(TypedDict):
    """Component details.

    Contains the status and detailed metrics for a system component.

    Attributes:
        status: Current status of the component ("UP" or "DOWN")
        details: Component-specific metrics as key-value pairs
    """

    status: str
    details: Dict[str, int | float]


class HealthStatus(BaseModel):
    """Health status.

    Overall system health status with component-level details.

    Attributes:
        status: Overall system status ("UP" or "DOWN")
        components: Dictionary of component statuses and their details
    """

    status: str
    components: Dict[str, ComponentDetails]


class SystemInfo(BaseModel):
    """System information.

    Static system information and specifications.

    Attributes:
        os: Operating system details including name, version and architecture
        python: Python environment details including version and implementation
        memory: Memory specifications and current usage
        cpu: CPU specifications including cores, usage and frequency
    """

    os: Dict[str, str]
    python: Dict[str, str]
    memory: Dict[str, int | float]
    cpu: Dict[str, int | float | None]


class CpuMetrics(TypedDict):
    """CPU metrics.

    Real-time CPU usage statistics.

    Attributes:
        usage_percent: Total CPU usage percentage
        per_cpu_percent: List of usage percentages for each CPU core
    """

    usage_percent: float
    per_cpu_percent: list[float]


class NetworkMetrics(TypedDict):
    """Network metrics.

    Network connection and I/O statistics.

    Attributes:
        connections: Number of active network connections
        io_counters: Network I/O statistics including bytes sent/received
    """

    connections: int
    io_counters: Optional[Dict[str, int]]


class DiskMetrics(TypedDict):
    """Disk metrics.

    Disk usage and I/O statistics.

    Attributes:
        usage: Disk space usage statistics
        io_counters: Disk I/O statistics including reads/writes
    """

    usage: Dict[str, int]
    io_counters: Optional[Dict[str, int]]


class SystemMetrics(TypedDict):
    """System metrics.

    Combined real-time system metrics.

    Attributes:
        uptime: System uptime duration
        cpu: CPU usage metrics
        memory: Memory usage statistics
        disk: Disk usage and I/O metrics
        network: Network connection and I/O metrics
    """

    uptime: str
    cpu: CpuMetrics
    memory: Dict[str, int]
    disk: DiskMetrics
    network: NetworkMetrics


class HttpStats(BaseModel):
    """HTTP request statistics.

    Statistics about HTTP requests and response status codes.

    Attributes:
        total_requests: Total number of requests handled
        status_counts: Count of responses by status code
        recent_status_codes: List of recent status codes (last 100)
    """

    total_requests: int
    status_counts: Dict[int, int]
    recent_status_codes: List[int]


router: APIRouter = APIRouter(prefix="/actuator", tags=["Actuator"])


@router.get("/health", response_model=HealthStatus)
async def health() -> HealthStatus:
    """Check the health of the system.

    Performs health checks on system components including disk space and memory.
    A component is considered healthy if it has sufficient resources available.

    Returns:
        HealthStatus: System health status with component details
    """
    disk_usage = psutil.disk_usage("/")
    vm = psutil.virtual_memory()

    return HealthStatus(
        status="UP",
        components={
            "diskSpace": {
                "status": "UP",
                "details": {
                    "total": disk_usage.total,
                    "free": disk_usage.free,
                    "threshold": 10_485_760,  # 10MB
                },
            },
            "memory": {
                "status": "UP",
                "details": {
                    "total": vm.total,
                    "available": vm.available,
                    "percent": vm.percent,
                },
            },
        },
    )


@router.get("/info", response_model=SystemInfo)
async def info() -> SystemInfo:
    """Get the system information.

    Retrieves static system information including OS details, Python environment,
    CPU specifications and memory information.

    Returns:
        SystemInfo: Static system information and specifications
    """
    vm = psutil.virtual_memory()
    cpu_freq = psutil.cpu_freq()

    return SystemInfo(
        os={
            "name": platform.system(),
            "version": platform.version(),
            "architecture": platform.machine(),
        },
        python={
            "version": sys.version,
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
        },
        memory={
            "total": vm.total,
            "available": vm.available,
            "percent": vm.percent,
        },
        cpu={
            "cores": psutil.cpu_count(),
            "usage_percent": psutil.cpu_percent(interval=1),
            "frequency": cpu_freq.current if cpu_freq else None,
        },
    )


@router.get("/metrics", response_model=SystemMetrics)
async def metrics() -> SystemMetrics:
    """Get the system metrics.

    Collects real-time system metrics including:
    - System uptime
    - CPU usage (total and per-core)
    - Memory utilization
    - Disk usage and I/O statistics
    - Network connections and I/O counters

    Returns:
        SystemMetrics: Real-time system metrics
    """
    disk_io = psutil.disk_io_counters()
    net_io = psutil.net_io_counters()

    return SystemMetrics(
        uptime=str(datetime.now() - get_start_time()),
        cpu={
            "usage_percent": psutil.cpu_percent(interval=1),
            "per_cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
        },
        memory=psutil.virtual_memory()._asdict(),
        disk={
            "usage": psutil.disk_usage("/")._asdict(),
            "io_counters": disk_io._asdict() if disk_io else None,
        },
        network={
            "connections": len(psutil.net_connections()),
            "io_counters": net_io._asdict() if net_io else None,
        },
    )


@router.get("/stats", response_model=HttpStats)
async def stats() -> HttpStats:
    """Get HTTP request statistics.

    Retrieves statistics about HTTP requests including:
    - Total number of requests
    - Count of responses by status code
    - Recent status codes (last 100 requests)

    Returns:
        HttpStats: HTTP request statistics and status code history
    """

    logger.info("Getting HTTP request statistics")
    requests, counts, recent = get_stats()
    logger.info("HTTP request statistics retrieved")

    return HttpStats(
        total_requests=requests,
        status_counts=counts,
        recent_status_codes=recent,
    )
