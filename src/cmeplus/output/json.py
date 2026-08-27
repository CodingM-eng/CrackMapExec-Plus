"""JSON Output Formatter: Machine-readable result export."""

from __future__ import annotations

import json
from typing import Any

from cmeplus.core.results import Result, ResultSet


def format_json_results(result_sets: list[ResultSet] | ResultSet | Result, indent: int = 2) -> str:
    """Serialize ResultSet or Result instances into a formatted JSON string."""
    if isinstance(result_sets, ResultSet):
        data = result_sets.to_dict()
    elif isinstance(result_sets, Result):
        data = result_sets.to_dict()
    elif isinstance(result_sets, list):
        data: dict[str, Any] = {
            "total_jobs": len(result_sets),
            "jobs": [rs.to_dict() if hasattr(rs, "to_dict") else rs for rs in result_sets],
        }
    else:
        data = {"result": str(result_sets)}
    return json.dumps(data, indent=indent)
