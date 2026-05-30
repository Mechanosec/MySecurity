import threading
import unittest
from unittest.mock import MagicMock
from session import Session, SessionManager


class TestSession(unittest.TestCase):

    def _make_session(self, sid=1):
        sock = MagicMock()
        return Session(id=sid, sock=sock, addr=("192.168.1.5", 12345))

    def test_defaults(self):
        s = self._make_session()
        self.assertEqual(s.device_info, "Unknown")
        self.assertTrue(s.alive)
        self.assertEqual(s.log, [])
        self.assertTrue(s.cmd_queue.empty())

    def test_cmd_queue_put_get(self):
        s = self._make_session()
        s.cmd_queue.put("whoami")
        self.assertEqual(s.cmd_queue.get_nowait(), "whoami")

    def test_log_append(self):
        s = self._make_session()
        s.log.append("hello")
        s.log.append("world")
        self.assertEqual(s.log, ["hello", "world"])


class TestSessionManager(unittest.TestCase):

    def test_add_returns_session_with_incrementing_id(self):
        mgr = SessionManager()
        sock1, sock2 = MagicMock(), MagicMock()
        s1 = mgr.add(sock1, ("1.1.1.1", 1))
        s2 = mgr.add(sock2, ("1.1.1.2", 2))
        self.assertEqual(s1.id, 1)
        self.assertEqual(s2.id, 2)

    def test_count(self):
        mgr = SessionManager()
        self.assertEqual(mgr.count(), 0)
        mgr.add(MagicMock(), ("1.1.1.1", 1))
        self.assertEqual(mgr.count(), 1)

    def test_remove(self):
        mgr = SessionManager()
        s = mgr.add(MagicMock(), ("1.1.1.1", 1))
        mgr.remove(s.id)
        self.assertEqual(mgr.count(), 0)
        self.assertIsNone(mgr.get(s.id))

    def test_remove_nonexistent_is_noop(self):
        mgr = SessionManager()
        mgr.remove(999)

    def test_get_returns_session(self):
        mgr = SessionManager()
        s = mgr.add(MagicMock(), ("1.1.1.1", 1))
        self.assertIs(mgr.get(s.id), s)

    def test_get_missing_returns_none(self):
        mgr = SessionManager()
        self.assertIsNone(mgr.get(99))

    def test_all_returns_list(self):
        mgr = SessionManager()
        mgr.add(MagicMock(), ("1.1.1.1", 1))
        mgr.add(MagicMock(), ("1.1.1.2", 2))
        self.assertEqual(len(mgr.all()), 2)

    def test_thread_safety(self):
        mgr = SessionManager()
        errors = []

        def worker():
            try:
                for _ in range(50):
                    s = mgr.add(MagicMock(), ("1.1.1.1", 1))
                    mgr.remove(s.id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
