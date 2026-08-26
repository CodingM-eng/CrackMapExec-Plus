"""Unit tests for configuration loading and history metadata tracking without secrets."""

from pathlib import Path

from cmeplus.config.loader import ConfigLoader
from cmeplus.core.results import Result, ResultSet, ResultState
from cmeplus.history.manager import HistoryManager


def test_config_loader_defaults():
    config = ConfigLoader.load()
    assert config.workers >= 1
    assert config.timeout > 0
    assert config.theme == "security"


def test_config_loader_custom(tmp_path: Path):
    custom_cfg = tmp_path / "config.yaml"
    custom_cfg.write_text(
        """
        workers: 16
        timeout: 10.0
        theme: "minimal"
        """,
        encoding="utf-8",
    )
    config = ConfigLoader.load(custom_path=custom_cfg)
    assert config.workers == 16
    assert config.timeout == 10.0
    assert config.theme == "minimal"


def test_history_manager_no_secrets(tmp_path: Path):
    db_file = tmp_path / "test_history.db"
    history_mgr = HistoryManager(db_path=db_file)

    res_set = ResultSet(job_id="test-job-01", protocol="smb")
    res_set.add(
        Result(
            target="192.168.1.10:445",
            protocol="smb",
            status=ResultState.SUCCESS,
            duration=1.23,
            message="Authenticated",
        )
    )

    history_mgr.record_job(res_set)
    entries = history_mgr.get_recent(limit=10)

    assert len(entries) == 1
    entry = entries[0]
    assert entry.job_id == "test-job-01"
    assert entry.protocol == "SMB"
    assert entry.targets_count == 1
    assert entry.success_count == 1
    assert entry.status == "SUCCESS"
    assert entry.duration == 1.23
