"""Simulation Runner Service - Manages per-task simulation lifecycle timers"""
import asyncio
import os
from pathlib import Path
from typing import Dict, Optional

from src.config import get_settings
from src.database.db import get_session
from src.database.task_repository import TaskRepository
from src.utils.logger import get_system_logger

# Simulation duration in seconds (5 minutes)
SIMULATION_DURATION_SEC = 5 * 60

# Result file size in bytes (500 KB)
RESULT_FILE_SIZE = 500 * 1024

# Result filename suffix: {task_id}result.stp
RESULT_FILENAME_SUFFIX = "result.stp"


class SimulationRunner:
    """
    Manages background simulation timers for running tasks.

    Lifecycle:
      start_simulation(task_id)  → schedules a timer for SIMULATION_DURATION_SEC
      cancel_simulation(task_id) → cancels the timer (stop / delete)
      Timer fires               → creates result file + marks task finished
    """

    def __init__(self):
        # task_id → asyncio.Task
        self._timers: Dict[str, asyncio.Task] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_simulation(self, task_id: str) -> None:
        """Schedule a simulation timer for the given task."""
        # Cancel any existing timer for this task (safety guard)
        self._cancel(task_id)

        loop = asyncio.get_event_loop()
        timer_task = loop.create_task(self._run_timer(task_id))
        self._timers[task_id] = timer_task
        logger = get_system_logger()
        logger.info(
            f"[SimulationRunner] Timer started for task {task_id}, "
            f"will finish in {SIMULATION_DURATION_SEC}s"
        )

    def cancel_simulation(self, task_id: str) -> bool:
        """
        Cancel the simulation timer for the given task.
        Returns True if a timer was found and cancelled, False otherwise.
        """
        if task_id not in self._timers:
            return False
        self._cancel(task_id)
        logger = get_system_logger()
        logger.info(f"[SimulationRunner] Timer cancelled for task {task_id}")
        return True

    def is_running(self, task_id: str) -> bool:
        """Return True if a timer is currently active for this task."""
        task = self._timers.get(task_id)
        return task is not None and not task.done()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cancel(self, task_id: str) -> None:
        """Cancel and remove timer entry for task_id."""
        task = self._timers.pop(task_id, None)
        if task and not task.done():
            task.cancel()

    async def _run_timer(self, task_id: str) -> None:
        """Timer coroutine: wait → create result file → mark finished."""
        logger = get_system_logger()
        try:
            await asyncio.sleep(SIMULATION_DURATION_SEC)

            # Timer completed naturally – create result and update status
            logger.info(
                f"[SimulationRunner] Timer fired for task {task_id}, "
                "creating result file and marking finished"
            )
            self._create_result_file(task_id)
            self._mark_finished(task_id)

        except asyncio.CancelledError:
            # Timer was cancelled by stop/delete – do nothing
            logger.info(
                f"[SimulationRunner] Timer cancelled for task {task_id} "
                "(no result file created)"
            )
        finally:
            # Clean up entry regardless of outcome
            self._timers.pop(task_id, None)

    def _create_result_file(self, task_id: str) -> None:
        """Create the result/{task_id}result.stp file (500 KB) under the task directory."""
        settings = get_settings()
        task_dir = Path(settings.storage.base_path) / task_id
        result_dir = task_dir / "result"
        result_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{task_id}{RESULT_FILENAME_SUFFIX}"
        result_path = result_dir / filename
        # Write 500 KB of zero bytes as a placeholder simulation result
        result_path.write_bytes(b"\x00" * RESULT_FILE_SIZE)

        logger = get_system_logger()
        logger.info(
            f"[SimulationRunner] Created result file: {result_path} "
            f"({RESULT_FILE_SIZE // 1024} KB)"
        )

    def _mark_finished(self, task_id: str) -> None:
        """Update task status to 'finished' in a fresh DB session."""
        db = get_session()
        try:
            repo = TaskRepository(db)
            task = repo.get_task(task_id)
            if task and task.status == "running":
                repo.update_status(task_id, "finished")
                logger = get_system_logger()
                logger.info(
                    f"[SimulationRunner] Task {task_id} status → finished"
                )
        except Exception as e:
            logger = get_system_logger()
            logger.error(
                f"[SimulationRunner] Failed to update status for {task_id}: {e}"
            )
        finally:
            db.close()


# ------------------------------------------------------------------
# Global singleton
# ------------------------------------------------------------------

_runner: Optional[SimulationRunner] = None


def get_simulation_runner() -> SimulationRunner:
    """Return the global SimulationRunner singleton."""
    global _runner
    if _runner is None:
        _runner = SimulationRunner()
    return _runner
