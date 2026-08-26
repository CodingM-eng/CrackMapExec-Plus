"""Unit tests for JSON export and HTML security dashboard report generation."""

import json
from pathlib import Path

from cmeplus.core.results import Result, ResultSet, ResultState
from cmeplus.output.html import generate_html_dashboard
from cmeplus.output.json import format_json_results
from cmeplus.reports.generator import ReportGenerator


def test_json_formatting():
    res_set = ResultSet(job_id="job-99", protocol="smb")
    res_set.add(
        Result(
            target="192.168.1.10:445",
            protocol="smb",
            status=ResultState.SUCCESS,
            duration=0.5,
            message="Valid",
        )
    )

    json_str = format_json_results(res_set)
    data = json.loads(json_str)
    assert data["job_id"] == "job-99"
    assert data["protocol"] == "smb"
    assert data["success_count"] == 1
    assert len(data["results"]) == 1


def test_html_dashboard_generation():
    res_set = ResultSet(job_id="job-html", protocol="smb")
    res_set.add(
        Result(
            target="192.168.1.50:445",
            protocol="smb",
            status=ResultState.SUCCESS,
            duration=0.42,
            message="Dialect SMB 3.1.1",
        )
    )

    html_content = generate_html_dashboard(res_set)
    assert "<!DOCTYPE html>" in html_content
    assert "CrackMapExec+" in html_content
    assert "192.168.1.50:445" in html_content
    assert "SMB 3.1.1" in html_content


def test_report_generator(tmp_path: Path):
    res_set = ResultSet(job_id="job-gen", protocol="smb")
    res_set.add(
        Result(
            target="192.168.1.10:445",
            protocol="smb",
            status=ResultState.SUCCESS,
            duration=0.2,
            message="Negotiate probe success",
        )
    )

    gen = ReportGenerator(base_reports_dir=tmp_path)
    bundle_dir = gen.generate(res_set)

    assert bundle_dir.exists()
    assert (bundle_dir / "report.json").exists()
    assert (bundle_dir / "report.html").exists()

    json_data = json.loads((bundle_dir / "report.json").read_text(encoding="utf-8"))
    assert json_data["job_id"] == "job-gen"
