"""Algorithm Layer Client"""
import httpx
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from dataclasses import dataclass

from src.config import get_settings


@dataclass
class AlgorithmStatus:
    """Algorithm layer status response"""
    status: str
    cycle: int = 0
    error_info: Optional[str] = None


class AlgorithmConnectionError(Exception):
    """Exception for algorithm layer connection errors"""
    pass


class AlgorithmLayerBase(ABC):
    """Abstract base class for algorithm layer client"""
    
    @abstractmethod
    async def start_simulation(self, task_id: str, simulate_type: str, config_path: str) -> bool:
        """Start a simulation task"""
        pass
    
    @abstractmethod
    async def stop_simulation(self, task_id: str) -> bool:
        """Stop a simulation task"""
        pass
    
    @abstractmethod
    async def get_status(self, task_id: str) -> AlgorithmStatus:
        """Get simulation status"""
        pass
    
    @abstractmethod
    async def health_ping(self) -> bool:
        """Check algorithm layer health"""
        pass


class HttpAlgorithmClient(AlgorithmLayerBase):
    """HTTP client for algorithm layer"""
    
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.algorithm.base_url
        self.timeout = settings.algorithm.timeout_sec
        self.max_retries = 3
    
    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{path}"
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except httpx.TimeoutException:
                if attempt == self.max_retries - 1:
                    raise AlgorithmConnectionError(f"Request timeout: {url}")
            except httpx.ConnectError:
                if attempt == self.max_retries - 1:
                    raise AlgorithmConnectionError(f"Connection failed: {url}")
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise AlgorithmConnectionError(f"Request error: {str(e)}")
        
        raise AlgorithmConnectionError("Max retries exceeded")
    
    async def start_simulation(self, task_id: str, simulate_type: str, config_path: str) -> bool:
        """Start a simulation task"""
        try:
            result = await self._request("POST", "/simulation/start", json={
                "task_id": task_id,
                "simulate_type": simulate_type,
                "config_path": config_path
            })
            return result.get("success", False)
        except AlgorithmConnectionError:
            return False
    
    async def stop_simulation(self, task_id: str) -> bool:
        """Stop a simulation task"""
        try:
            result = await self._request("POST", "/simulation/stop", json={
                "task_id": task_id
            })
            return result.get("success", False)
        except AlgorithmConnectionError:
            return False
    
    async def get_status(self, task_id: str) -> AlgorithmStatus:
        """Get simulation status"""
        try:
            result = await self._request("GET", f"/simulation/status/{task_id}")
            return AlgorithmStatus(
                status=result.get("status", "unknown"),
                cycle=result.get("cycle", 0),
                error_info=result.get("error_info")
            )
        except AlgorithmConnectionError:
            return AlgorithmStatus(status="unknown")
    
    async def health_ping(self) -> bool:
        """Check algorithm layer health"""
        try:
            result = await self._request("GET", "/health")
            return result.get("status") == "OK"
        except AlgorithmConnectionError:
            return False


class MockAlgorithmClient(AlgorithmLayerBase):
    """Mock client for testing without real algorithm layer"""
    
    def __init__(self):
        # In-memory task status storage for mock
        self._task_status: Dict[str, AlgorithmStatus] = {}
    
    async def start_simulation(self, task_id: str, simulate_type: str, config_path: str) -> bool:
        """Start a simulation task (mock)"""
        self._task_status[task_id] = AlgorithmStatus(status="running", cycle=0)
        return True
    
    async def stop_simulation(self, task_id: str) -> bool:
        """Stop a simulation task (mock)"""
        if task_id in self._task_status:
            self._task_status[task_id] = AlgorithmStatus(status="stop")
        return True
    
    async def get_status(self, task_id: str) -> AlgorithmStatus:
        """Get simulation status (mock)"""
        return self._task_status.get(task_id, AlgorithmStatus(status="not_exist"))
    
    async def health_ping(self) -> bool:
        """Check algorithm layer health (mock)"""
        return True
    
    def set_task_finished(self, task_id: str):
        """Helper to mark task as finished (for testing)"""
        self._task_status[task_id] = AlgorithmStatus(status="finished")
    
    def set_task_failed(self, task_id: str, error_info: str):
        """Helper to mark task as failed (for testing)"""
        self._task_status[task_id] = AlgorithmStatus(status="failed", error_info=error_info)


def get_algorithm_client() -> AlgorithmLayerBase:
    """Get algorithm layer client based on configuration"""
    settings = get_settings()
    
    if settings.algorithm.mock_mode:
        return MockAlgorithmClient()
    else:
        return HttpAlgorithmClient()


# Global client instance (singleton)
_algorithm_client: Optional[AlgorithmLayerBase] = None


def get_client() -> AlgorithmLayerBase:
    """Get global algorithm client instance"""
    global _algorithm_client
    if _algorithm_client is None:
        _algorithm_client = get_algorithm_client()
    return _algorithm_client
