"""Unit tests for Video Guide Engine, models, timestamp math, and catalog search."""

from pathlib import Path

from cmeplus.video.manager import VideoGuideEngine
from cmeplus.video.models import VideoGuideItem


def test_video_guide_item_formatting():
    item = VideoGuideItem(
        key="smb",
        title="SMB Guide",
        url="https://youtube.com/watch?v=TEST_ID",
        start_seconds=143,
        status="coming_soon",
        description="SMB Fundamentals",
    )
    assert item.formatted_timestamp == "02:23"
    assert "t=143s" in item.timestamped_url
    assert item.timestamped_url.startswith("https://youtube.com/watch?")
    assert item.is_coming_soon is True
    assert item.is_published is False


def test_video_guide_item_various_timestamps():
    # 0 seconds
    item_0 = VideoGuideItem(key="intro", title="Intro", url="https://youtube.com/watch?v=TEST", start_seconds=0)
    assert item_0.formatted_timestamp == "00:00"
    assert item_0.timestamped_url == "https://youtube.com/watch?v=TEST"

    # 375 seconds -> 06:15
    item_ldap = VideoGuideItem(key="ldap", title="LDAP", url="https://youtube.com/watch?v=TEST", start_seconds=375)
    assert item_ldap.formatted_timestamp == "06:15"
    assert "t=375s" in item_ldap.timestamped_url

    # 642 seconds -> 10:42
    item_winrm = VideoGuideItem(key="winrm", title="WinRM", url="https://youtube.com/watch?v=TEST", start_seconds=642)
    assert item_winrm.formatted_timestamp == "10:42"
    assert "t=642s" in item_winrm.timestamped_url

    # 860 seconds -> 14:20
    item_ssh = VideoGuideItem(key="ssh", title="SSH", url="https://youtube.com/watch?v=TEST", start_seconds=860)
    assert item_ssh.formatted_timestamp == "14:20"
    assert "t=860s" in item_ssh.timestamped_url

    # 1110 seconds -> 18:30
    item_wiz = VideoGuideItem(key="wiz", title="Wizard", url="https://youtube.com/watch?v=TEST", start_seconds=1110)
    assert item_wiz.formatted_timestamp == "18:30"
    assert "t=1110s" in item_wiz.timestamped_url

    # 1275 seconds -> 21:15
    item_rep = VideoGuideItem(key="rep", title="Report", url="https://youtube.com/watch?v=TEST", start_seconds=1275)
    assert item_rep.formatted_timestamp == "21:15"
    assert "t=1275s" in item_rep.timestamped_url


def test_video_guide_item_hour_timestamp():
    item = VideoGuideItem(
        key="full",
        title="Full Course",
        url="https://youtube.com/watch?v=TEST_ID",
        start_seconds=3665,
    )
    # 3665s = 1 hour, 1 minute, 5 seconds
    assert item.formatted_timestamp == "01:01:05"
    assert "t=3665s" in item.timestamped_url


def test_video_guide_item_published_status():
    item = VideoGuideItem(
        key="smb",
        title="SMB Guide",
        url="https://youtube.com/watch?v=TEST_ID",
        start_seconds=143,
        status="published",
    )
    assert item.is_coming_soon is False
    assert item.is_published is True


def test_video_engine_default_catalog():
    engine = VideoGuideEngine()
    items = engine.list_all()
    assert len(items) >= 9
    # Must contain all required topics
    required_topics = [
        "introduction",
        "installation",
        "smb",
        "ldap",
        "winrm",
        "ssh",
        "modules",
        "wizard",
        "reporting",
    ]
    for topic in required_topics:
        item = engine.get(topic)
        assert item is not None, f"Topic '{topic}' missing from catalog"
        assert item.status == "coming_soon"
        assert isinstance(item.start_seconds, int)

    smb_item = engine.get("smb")
    assert smb_item.start_seconds == 143
    assert smb_item.formatted_timestamp == "02:23"

    ldap_item = engine.get("ldap")
    assert ldap_item.start_seconds == 375
    assert ldap_item.formatted_timestamp == "06:15"

    winrm_item = engine.get("winrm")
    assert winrm_item.start_seconds == 642
    assert winrm_item.formatted_timestamp == "10:42"


def test_video_engine_aliases():
    engine = VideoGuideEngine()
    assert engine.get("intro") is not None
    assert engine.get("intro").key == "introduction"

    assert engine.get("install") is not None
    assert engine.get("install").key == "installation"

    assert engine.get("report") is not None
    assert engine.get("report").key == "reporting"

    assert engine.get("all") is not None
    assert engine.get("all").key == "full-tutorial"


def test_video_engine_search():
    engine = VideoGuideEngine()
    results = engine.search("Active Directory")
    assert len(results) >= 1
    assert any(r.key == "ldap" for r in results)

    results_smb = engine.search("shares")
    assert len(results_smb) >= 1
    assert any(r.key == "smb" for r in results_smb)

    results_kali = engine.search("kali")
    assert len(results_kali) >= 1
    assert any(r.key == "installation" for r in results_kali)


def test_video_engine_custom_catalog(tmp_path: Path):
    custom_yaml = tmp_path / "custom_videos.yaml"
    custom_yaml.write_text(
        """
        kerberos:
          title: "Kerberos Roasting Guide"
          status: "published"
          url: "https://youtube.com/watch?v=CUSTOM"
          start_seconds: 95
          description: "SPN enumeration and TGS request"
          keywords: ["kerberos", "ad"]
        """,
        encoding="utf-8",
    )

    engine = VideoGuideEngine(custom_catalog_path=custom_yaml)
    assert len(engine.list_all()) == 1
    item = engine.get("kerberos")
    assert item is not None
    assert item.title == "Kerberos Roasting Guide"
    assert item.formatted_timestamp == "01:35"
    assert item.is_published is True
    assert item.is_coming_soon is False
