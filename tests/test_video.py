"""Unit tests for Video Guide Engine, models, timestamp math, and catalog search."""

from pathlib import Path

from cmeplus.video.manager import VideoGuideEngine
from cmeplus.video.models import VideoGuideItem


def test_video_guide_item_formatting():
    item = VideoGuideItem(
        key="smb",
        title="SMB Guide",
        url="https://youtube.com/watch?v=TEST_ID",
        start=143,
        description="SMB Fundamentals",
    )
    assert item.formatted_timestamp == "02:23"
    assert "t=143s" in item.timestamped_url
    assert item.timestamped_url.startswith("https://youtube.com/watch?")


def test_video_guide_item_hour_timestamp():
    item = VideoGuideItem(
        key="full",
        title="Full Course",
        url="https://youtube.com/watch?v=TEST_ID",
        start=3665,
    )
    # 3665s = 1 hour, 1 minute, 5 seconds
    assert item.formatted_timestamp == "01:01:05"
    assert "t=3665s" in item.timestamped_url


def test_video_engine_default_catalog():
    engine = VideoGuideEngine()
    items = engine.list_all()
    assert len(items) >= 4

    smb_item = engine.get("smb")
    assert smb_item is not None
    assert smb_item.key == "smb"
    assert smb_item.start == 143

    ldap_item = engine.get("ldap")
    assert ldap_item is not None
    assert ldap_item.start == 375


def test_video_engine_search():
    engine = VideoGuideEngine()
    results = engine.search("Active Directory")
    assert len(results) >= 1
    assert any(r.key == "ldap" for r in results)

    results_smb = engine.search("shares")
    assert len(results_smb) >= 1
    assert any(r.key == "smb" for r in results_smb)


def test_video_engine_custom_catalog(tmp_path: Path):
    custom_yaml = tmp_path / "custom_videos.yaml"
    custom_yaml.write_text(
        """
        kerberos:
          title: "Kerberos Roasting Guide"
          url: "https://youtube.com/watch?v=CUSTOM"
          start: 95
          description: "SPN enumeration and TGS request"
          tags: ["kerberos", "ad"]
        """,
        encoding="utf-8",
    )

    engine = VideoGuideEngine(custom_catalog_path=custom_yaml)
    assert len(engine.list_all()) == 1
    item = engine.get("kerberos")
    assert item is not None
    assert item.title == "Kerberos Roasting Guide"
    assert item.formatted_timestamp == "01:35"
