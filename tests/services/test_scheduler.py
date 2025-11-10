from unittest.mock import MagicMock
from app.services.scheduler.scheduler import IntervalScheduler


def test_add_and_list_jobs():
    db = MagicMock()
    s = IntervalScheduler(db=db)
    s.add_job("sync", lambda: None, interval_seconds=60)
    assert "sync" in s.list_jobs()


def test_remove_job():
    db = MagicMock()
    s = IntervalScheduler(db=db)
    s.add_job("sync", lambda: None, interval_seconds=60)
    s.remove_job("sync")
    assert "sync" not in s.list_jobs()


def test_job_executes_and_db_accessed():
    db = MagicMock()
    called = []

    def my_job():
        db.query("SELECT 1")
        called.append(1)

    s = IntervalScheduler(db=db)
    s.add_job("work", my_job, interval_seconds=0)

    import time
    s.start()
    time.sleep(0.1)
    s.stop()

    assert len(called) > 0
    db.query.assert_called()
