"""Unit tests for Target Engine parsing, CIDR expansion, range calculation, validation, and files."""

from pathlib import Path

from cmeplus.core.targets import TargetEngine, TargetKind


def test_single_ipv4_parsing():
    target_set = TargetEngine.parse("192.168.1.10")
    assert len(target_set) == 1
    target = target_set.targets[0]
    assert target.host == "192.168.1.10"
    assert target.kind == TargetKind.IPV4
    assert target.port is None
    assert target.endpoint == "192.168.1.10"


def test_single_ipv4_with_port():
    target_set = TargetEngine.parse("192.168.1.10:445")
    assert len(target_set) == 1
    target = target_set.targets[0]
    assert target.host == "192.168.1.10"
    assert target.port == 445
    assert target.endpoint == "192.168.1.10:445"


def test_comma_separated_targets():
    target_set = TargetEngine.parse("192.168.1.10,192.168.1.11,192.168.1.12")
    assert len(target_set) == 3
    endpoints = [t.endpoint for t in target_set]
    assert endpoints == ["192.168.1.10", "192.168.1.11", "192.168.1.12"]


def test_duplicate_targets_deduplicated():
    target_set = TargetEngine.parse("192.168.1.10,192.168.1.10,192.168.1.11,192.168.1.10")
    assert len(target_set) == 2
    endpoints = [t.endpoint for t in target_set]
    assert endpoints == ["192.168.1.10", "192.168.1.11"]


def test_cidr_expansion():
    target_set = TargetEngine.parse("10.0.0.0/29")
    # /29 has 6 usable host addresses: 10.0.0.1 to 10.0.0.6
    assert len(target_set) == 6
    assert target_set.targets[0].host == "10.0.0.1"
    assert target_set.targets[-1].host == "10.0.0.6"
    assert all(t.kind == TargetKind.CIDR for t in target_set)


def test_octet_range_parsing():
    target_set = TargetEngine.parse("192.168.1.10-15")
    assert len(target_set) == 6
    hosts = [t.host for t in target_set]
    assert hosts == [
        "192.168.1.10",
        "192.168.1.11",
        "192.168.1.12",
        "192.168.1.13",
        "192.168.1.14",
        "192.168.1.15",
    ]


def test_full_ip_range_parsing():
    target_set = TargetEngine.parse("10.10.10.1-10.10.10.4")
    assert len(target_set) == 4
    assert [t.host for t in target_set] == [
        "10.10.10.1",
        "10.10.10.2",
        "10.10.10.3",
        "10.10.10.4",
    ]


def test_hostname_parsing():
    target_set = TargetEngine.parse("dc01.corp.local")
    assert len(target_set) == 1
    assert target_set.targets[0].host == "dc01.corp.local"
    assert target_set.targets[0].kind == TargetKind.HOSTNAME


def test_target_file_parsing(tmp_path: Path):
    file_path = tmp_path / "test_targets.txt"
    file_path.write_text(
        """
        # Leading comment
        192.168.1.10
        192.168.1.11 # Inline comment

        # Blank lines above and below
        192.168.1.10 # Duplicate entry
        dc01.lab.local
        """,
        encoding="utf-8",
    )

    target_set = TargetEngine.parse(f"@{file_path}")
    assert len(target_set) == 3
    endpoints = [t.endpoint for t in target_set]
    assert endpoints == ["192.168.1.10", "192.168.1.11", "dc01.lab.local"]
    assert len(target_set.issues) == 0


def test_target_file_with_invalid_entries(tmp_path: Path):
    file_path = tmp_path / "bad_targets.txt"
    file_path.write_text(
        """
        192.168.1.10
        this..is..not..valid!!
        192.168.1.20
        """,
        encoding="utf-8",
    )

    target_set = TargetEngine.parse(f"@{file_path}")
    assert len(target_set) == 2
    assert len(target_set.issues) == 1
    assert "this..is..not..valid!!" in target_set.issues[0].raw
    assert target_set.issues[0].line_number == 3


def test_missing_target_file():
    target_set = TargetEngine.parse("@/non/existent/path/targets.txt")
    assert len(target_set) == 0
    assert len(target_set.issues) == 1
    assert "Target file not found" in target_set.issues[0].reason


def test_target_argument_injection_rejected():
    target_set = TargetEngine.parse("--script=smb-vuln*")
    assert len(target_set) == 0
    assert len(target_set.issues) == 1
    assert "cannot start with a hyphen" in target_set.issues[0].reason

    target_set_flag = TargetEngine.parse("-u")
    assert len(target_set_flag) == 0
    assert len(target_set_flag.issues) == 1
    assert "cannot start with a hyphen" in target_set_flag.issues[0].reason


def test_target_control_characters_rejected():
    target_set = TargetEngine.parse("192.168.1.1\x00extra")
    assert len(target_set) == 0
    assert len(target_set.issues) == 1
    assert "illegal control or null characters" in target_set.issues[0].reason
