"""JSON Output Formatter: Machine-readable result export."""

from __future__ import annotations

import json

from cmeplus.core.results import ResultSet


def format_json_results(result_sets: list[ResultSet] | ResultSet, indent: int = 2) -> str:
    """Serialize ResultSet instances into a formatted JSON string."""
    if isinstance(result_sets, ResultSet):
        data = result_sets.to_dict()
    else:
        data = {
            "total_jobs": len(result_sets),
            "jobs": [rs.to_dict() for rs in result_sets],
        }
    return json.dumps(data, indent=indent)
