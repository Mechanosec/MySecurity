from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, RichLog, Static

from session import Session, SessionManager


class C2App(App):
    # Catppuccin Macchiato
    CSS = """
    Screen {
        layout: vertical;
        background: #24273a;
    }
    Header {
        background: #1e2030;
        color: #c6a0f6;
    }
    #main {
        layout: horizontal;
        height: 1fr;
    }
    #left {
        width: 32;
        border: solid #494d64;
        background: #1e2030;
    }
    #panel-title {
        background: #363a4f;
        color: #c6a0f6;
        text-style: bold;
        padding: 0 1;
        height: 1;
    }
    #session-list {
        height: 1fr;
    }
    ListItem {
        color: #cad3f5;
        padding: 0 1;
    }
    ListItem.--highlight {
        background: #363a4f;
        color: #c6a0f6;
    }
    #right {
        width: 1fr;
        border: solid #494d64;
        background: #181926;
    }
    #shell-title {
        background: #363a4f;
        color: #8aadf4;
        text-style: bold;
        padding: 0 1;
        height: 1;
    }
    #shell {
        height: 1fr;
        padding: 0 1;
    }
    #cmd-input {
        height: 3;
        border: solid #494d64;
        background: #1e2030;
        color: #a6da95;
    }
    Input {
        background: #1e2030;
        color: #a6da95;
        border: none;
    }
    Footer {
        background: #1e2030;
        color: #b8c0e0;
    }
    """

    BINDINGS = [
        Binding("tab", "next_session", "Next session", show=True),
        Binding("ctrl+c", "quit", "Quit", show=True),
    ]

    active_session_id: reactive[int | None] = reactive(None)

    def __init__(self, session_manager: SessionManager) -> None:
        super().__init__()
        self.session_manager = session_manager

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield Static(" SESSIONS", id="panel-title")
                yield ListView(id="session-list")
            with Vertical(id="right"):
                yield Static(" No active session", id="shell-title")
                yield RichLog(id="shell", highlight=True, markup=True, wrap=True)
        yield Input(placeholder=" $ type command and press Enter…", id="cmd-input")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "FakeClicker C2"
        self.sub_title = "waiting for connections…"
        self.query_one("#cmd-input", Input).focus()

    def on_session_connect(self, session: Session) -> None:
        lv = self.query_one("#session-list", ListView)
        label = f"[{session.id}] {session.device_info[:22]}"
        lv.append(ListItem(Label(label), id=f"sid-{session.id}"))
        self.sub_title = f"{self.session_manager.count()} connected"
        if self.active_session_id is None:
            self.active_session_id = session.id
            self._update_shell_title()

    def on_session_output(self, session_id: int, line: str) -> None:
        session = self.session_manager.get(session_id)
        if session:
            session.log.append(line)
        if self.active_session_id == session_id:
            self.query_one("#shell", RichLog).write(line)

    def on_session_disconnect(self, session_id: int) -> None:
        try:
            self.query_one(f"#sid-{session_id}", ListItem).remove()
        except Exception:
            pass
        self.sub_title = f"{self.session_manager.count()} connected"
        if self.active_session_id == session_id:
            sessions = self.session_manager.all()
            self.active_session_id = sessions[0].id if sessions else None
            self._refresh_shell()
            self._update_shell_title()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        event.input.value = ""
        if not cmd or self.active_session_id is None:
            return
        session = self.session_manager.get(self.active_session_id)
        if session and session.alive:
            session.cmd_queue.put(cmd)
            self.query_one("#shell", RichLog).write(f"[bold #8aadf4]$ {cmd}[/bold #8aadf4]")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        raw_id = event.item.id
        if raw_id and raw_id.startswith("sid-"):
            self.active_session_id = int(raw_id.split("-")[1])
            self._refresh_shell()
            self._update_shell_title()

    def action_next_session(self) -> None:
        sessions = self.session_manager.all()
        if not sessions:
            return
        ids = [s.id for s in sessions]
        if self.active_session_id not in ids:
            self.active_session_id = ids[0]
        else:
            idx = (ids.index(self.active_session_id) + 1) % len(ids)
            self.active_session_id = ids[idx]
        self._refresh_shell()
        self._update_shell_title()

    def _refresh_shell(self) -> None:
        log = self.query_one("#shell", RichLog)
        log.clear()
        if self.active_session_id is None:
            return
        session = self.session_manager.get(self.active_session_id)
        if session:
            for line in session.log:
                log.write(line)

    def _update_shell_title(self) -> None:
        title = self.query_one("#shell-title", Static)
        if self.active_session_id is None:
            title.update(" No active session")
            return
        session = self.session_manager.get(self.active_session_id)
        if session:
            title.update(f" [{session.id}] {session.device_info}")
        else:
            title.update(" No active session")
