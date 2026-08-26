"""Unit tests for Job, JobQueue, JobPlan, and WorkerPool execution & cancellation."""


from cmeplus.core.jobs import Job, JobCredentials, JobQueue
from cmeplus.core.targets import TargetEngine
from cmeplus.core.workers import WorkerPool
from cmeplus.protocols.manager import ProtocolManager


def test_job_creation():
    target_set = TargetEngine.parse("192.168.1.10,192.168.1.11")
    job = Job(
        protocol="smb",
        targets=target_set,
        credentials=JobCredentials(username="admin", password="password123"),
        modules=["shares"],
    )
    assert job.protocol == "smb"
    assert job.target_count == 2
    assert not job.credentials.is_anonymous()
    assert "shares" in job.modules


def test_job_queue_fifo():
    q = JobQueue()
    t1 = TargetEngine.parse("192.168.1.10")
    t2 = TargetEngine.parse("192.168.1.20")

    j1 = Job(protocol="smb", targets=t1)
    j2 = Job(protocol="ldap", targets=t2)

    q.put(j1)
    q.put(j2)

    assert q.total_jobs == 2
    fetched_1 = q.get()
    assert fetched_1.protocol == "smb"
    fetched_2 = q.get()
    assert fetched_2.protocol == "ldap"
    assert q.empty()


def test_worker_pool_mock_execution():
    proto_mgr = ProtocolManager()
    target_set = TargetEngine.parse("192.168.1.10,192.168.1.11,192.168.1.254")
    job = Job(protocol="mock", targets=target_set, workers=2)

    results_captured = []

    def on_result(res, current, total):
        results_captured.append(res)

    pool = WorkerPool(protocol_manager=proto_mgr, max_workers=2, on_result=on_result)
    result_set = pool.run_job(job)

    assert result_set.total == 3
    assert result_set.success_count == 2
    assert result_set.unavailable_count == 1
    assert len(results_captured) == 3


def test_worker_pool_cancellation():
    proto_mgr = ProtocolManager()
    # 20 targets
    target_set = TargetEngine.parse("10.0.0.1-20")
    job = Job(protocol="mock", targets=target_set, workers=1)

    pool = WorkerPool(protocol_manager=proto_mgr, max_workers=1)
    pool.cancel()
    assert pool.is_cancelled

    result_set = pool.run_job(job)
    assert result_set.total == 20
    # All targets should be marked skipped because pool is cancelled
    assert result_set.skipped_count == 20


def test_worker_pool_unregistered_protocol():
    proto_mgr = ProtocolManager()
    target_set = TargetEngine.parse("192.168.1.10")
    job = Job(protocol="nonexistent_proto", targets=target_set)

    pool = WorkerPool(protocol_manager=proto_mgr)
    result_set = pool.run_job(job)

    assert result_set.total == 1
    assert result_set.error_count == 1
    assert "not registered" in result_set.results[0].message
