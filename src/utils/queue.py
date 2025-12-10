from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional


class JobStatus:
    PENDING = "pending"
    SYNTHESIZING = "synthesizing"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class AudioJob:
    job_id: str
    chat_id: int
    order: int
    payload: object
    status: str = JobStatus.PENDING
    error: Optional[str] = None


@dataclass
class QueueState:
    counter: int = 0
    items: Deque[AudioJob] = field(default_factory=deque)


class InMemoryQueue:
    def __init__(self) -> None:
        self._queues: Dict[int, QueueState] = {}

    def enqueue(self, chat_id: int, job_id: str, payload: object) -> AudioJob:
        state = self._queues.setdefault(chat_id, QueueState())
        state.counter += 1
        job = AudioJob(job_id=job_id, chat_id=chat_id, order=state.counter, payload=payload)
        state.items.append(job)
        return job

    def next_job(self, chat_id: int) -> Optional[AudioJob]:
        state = self._queues.get(chat_id)
        if not state or not state.items:
            return None
        return state.items[0]

    def pop_job(self, chat_id: int) -> Optional[AudioJob]:
        state = self._queues.get(chat_id)
        if not state or not state.items:
            return None
        return state.items.popleft()

    def update_status(self, job: AudioJob, status: str, error: Optional[str] = None) -> None:
        job.status = status
        job.error = error

    def is_empty(self, chat_id: int) -> bool:
        state = self._queues.get(chat_id)
        return not state or not state.items



