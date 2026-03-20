"""简易任务队列（内存版）。

说明：
- 当前版本用于本地开发，进程重启会丢失任务状态。
- 后续可替换为 Celery/RQ/Redis 持久化队列。
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
import threading
import uuid
from typing import Any, Callable


@dataclass(slots=True)
class TaskState:
    id: str
    task_type: str
    status: str
    payload: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    error_text: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class TaskQueue:
    """线程池驱动的轻量任务队列。"""

    def __init__(self, max_workers: int = 4) -> None:
        self._pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="goods-task")
        self._tasks: dict[str, TaskState] = {}
        self._lock = threading.Lock()

    def submit(
        self,
        task_type: str,
        payload: dict[str, Any],
        fn: Callable[..., dict[str, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """提交任务并返回 task_id。"""
        task_id = uuid.uuid4().hex
        state = TaskState(id=task_id, task_type=task_type, status="PENDING", payload=payload)
        with self._lock:
            self._tasks[task_id] = state

        # 异步执行任务，并在回调中更新状态。
        future = self._pool.submit(self._run_task, task_id, fn, *args, **kwargs)
        future.add_done_callback(lambda f: self._on_done(task_id, f))
        return task_id

    def _run_task(
        self,
        task_id: str,
        fn: Callable[..., dict[str, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self._update(task_id, status="RUNNING")
        return fn(*args, **kwargs)

    def _on_done(self, task_id: str, future: Future) -> None:
        try:
            result = future.result()
            self._update(task_id, status="SUCCESS", result=result)
        except Exception as exc:
            self._update(task_id, status="FAILED", error_text=str(exc))

    def _update(self, task_id: str, **updates: Any) -> None:
        with self._lock:
            state = self._tasks[task_id]
            for key, value in updates.items():
                setattr(state, key, value)
            state.updated_at = datetime.now().isoformat(timespec="seconds")

    def get(self, task_id: str) -> TaskState | None:
        with self._lock:
            return self._tasks.get(task_id)

    def to_dict(self, task_id: str) -> dict[str, Any] | None:
        state = self.get(task_id)
        if state is None:
            return None
        return {
            "id": state.id,
            "task_type": state.task_type,
            "status": state.status,
            "payload": state.payload,
            "result": state.result,
            "error_text": state.error_text,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
        }


task_queue = TaskQueue()
