import queue as _queue
import socket
import threading
from session import Session, SessionManager


class TCPServer:
    def __init__(self, host: str, port: int, session_manager: SessionManager, app=None):
        self.host = host
        self.port = port
        self.session_manager = session_manager
        self.app = app
        self._running = False

    def start(self) -> None:
        self._running = True
        t = threading.Thread(target=self._accept_loop, daemon=True, name="tcp-accept")
        t.start()

    def stop(self) -> None:
        self._running = False

    def _accept_loop(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((self.host, self.port))
            srv.listen(20)
            srv.settimeout(1.0)
            while self._running:
                try:
                    conn, addr = srv.accept()
                    session = self.session_manager.add(conn, addr)
                    t = threading.Thread(
                        target=self._handle_session,
                        args=(session,),
                        daemon=True,
                        name=f"session-{session.id}",
                    )
                    t.start()
                except socket.timeout:
                    continue

    def _handle_session(self, session: Session) -> None:
        try:
            # makefile requires blocking socket (no timeout)
            session.sock.settimeout(None)
            reader = session.sock.makefile("r", encoding="utf-8", errors="replace")

            banner = reader.readline().strip()
            if not banner:
                return
            _ = reader.readline()  # "[*] shell ready"
            session.device_info = banner.replace("[*] ", "")

            if self.app:
                self.app.call_from_thread(self.app.on_session_connect, session)

            # Separate thread writes commands so reader can block freely
            def _write_loop() -> None:
                try:
                    writer = session.sock.makefile("w", encoding="utf-8", buffering=1)
                    while session.alive:
                        try:
                            cmd = session.cmd_queue.get(timeout=0.3)
                            writer.write(cmd + "\n")
                            writer.flush()
                        except _queue.Empty:
                            continue
                except Exception:
                    pass

            threading.Thread(target=_write_loop, daemon=True, name=f"writer-{session.id}").start()

            # Blocking read — exits when socket closes
            for raw in reader:
                if not session.alive:
                    break
                line = raw.rstrip("\n")
                if line == "---":
                    continue
                if self.app:
                    self.app.call_from_thread(self.app.on_session_output, session.id, line)
                else:
                    session.log.append(line)

        except Exception:
            pass
        finally:
            session.alive = False
            self.session_manager.remove(session.id)
            if self.app:
                self.app.call_from_thread(self.app.on_session_disconnect, session.id)
            try:
                session.sock.close()
            except Exception:
                pass
