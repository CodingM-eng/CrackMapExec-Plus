"""Report Generator: Automatic directory creation and generation of JSON and HTML reports."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cmeplus.core.results import ResultSet
from cmeplus.output.html import generate_html_dashboard
from cmeplus.output.json import format_json_results


class ReportGenerator:
    """Creates timestamped report bundles on disk."""

    def __init__(self, base_reports_dir: Path | str = "reports") -> None:
        self.base_dir = Path(base_reports_dir)

    def generate(self, result_sets: list[ResultSet] | ResultSet, report_name: str | None = None) -> Path:
        """Write JSON and HTML report files into a dedicated timestamped folder."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        folder_name = f"scan-{now_str}" if not report_name else f"{report_name}-{now_str}"
        target_dir = self.base_dir / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        json_path = target_dir / "report.json"
        html_path = target_dir / "report.html"

        json_content = format_json_results(result_sets)
        json_path.write_text(json_content, encoding="utf-8")

        html_content = generate_html_dashboard(result_sets)
        html_path.write_text(html_content, encoding="utf-8")

        return target_dir
