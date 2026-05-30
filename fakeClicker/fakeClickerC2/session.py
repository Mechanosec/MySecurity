import threading
from dataclasses import dataclass, field
from queue import Queue
from socket import socket
from typing import Optional


@dataclass
class Session:
    id: int
    sock: socket
    addr: tuple
    device_info: str = "Unknown"
    cmd_queue: Queue = field(default_factory=Queue)
    log: list = field(default_factory=list)
    alive: bool = True


class SessionManager:
    def __init__(self):
        self._sessions: dict[int, Session] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def add(self, sock: socket, addr: tuple) -> Session:
        with self._lock:
            session = Session(id=self._next_id, sock=sock, addr=addr)
            self._sessions[self._next_id] = session
            self._next_id += 1
            return session

    def remove(self, session_id: int) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def get(self, session_id: int) -> Optional[Session]:
        with self._lock:
            return self._sessions.get(session_id)

    def all(self) -> list[Session]:
        with self._lock:
            return list(self._sessions.values())

    def count(self) -> int:
        with self._lock:
            return len(self._sessions)
