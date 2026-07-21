from __future__ import annotations

from typing import Dict, Optional

from modules.inference.models.inference_model import InferenceResult
from modules.inference.models.threat_model import ThreatReport


async def get_dashboard_stats(user_id: Optional[str] = None) -> dict:
    query = {}
    if user_id:
        query["user_id"] = user_id

    total_analyses = await InferenceResult.find(query).count()
    total_threats = await ThreatReport.find(query).count()

    completed = await InferenceResult.find({**query, "status": "completed"}).count()
    failed = await InferenceResult.find({**query, "status": "failed"}).count()

    recent_items = (
        await InferenceResult.find(query)
        .sort(-InferenceResult.created_at)
        .limit(5)
        .to_list()
    )

    threat_query = {}
    if user_id:
        threat_query["user_id"] = user_id
    threat_reports = await ThreatReport.find(threat_query).to_list()

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    total_components = 0
    component_freq: Dict[str, int] = {}

    for tr in threat_reports:
        for ca in tr.component_analyses:
            total_components += 1
            label = ca.component_label
            component_freq[label] = component_freq.get(label, 0) + 1
            for t in ca.stride_threats:
                rl = t.risk_level
                if rl == "critical":
                    critical_count += 1
                elif rl == "high":
                    high_count += 1
                elif rl == "medium":
                    medium_count += 1
                elif rl == "low":
                    low_count += 1

    stride_distribution: Dict[str, int] = {}
    for tr in threat_reports:
        for cat, count in tr.stride_summary.items():
            stride_distribution[cat] = stride_distribution.get(cat, 0) + count

    sorted_components = sorted(component_freq.items(), key=lambda x: -x[1])[:10]

    recent = []
    for inf in recent_items:
        recent.append({
            "id": str(inf.id),
            "filename": inf.filename,
            "status": inf.status,
            "components_count": len(inf.components),
            "created_at": inf.created_at.isoformat() if inf.created_at else None,
        })

    return {
        "total_analyses": total_analyses,
        "total_threats": total_threats,
        "completed_analyses": completed,
        "failed_analyses": failed,
        "total_components_analyzed": total_components,
        "threats_by_risk": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
        },
        "stride_distribution": stride_distribution,
        "top_components": [{"label": k, "count": v} for k, v in sorted_components],
        "recent_analyses": recent,
    }
