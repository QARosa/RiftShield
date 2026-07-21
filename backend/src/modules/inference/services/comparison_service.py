# -\*- coding: utf-8 -\*-\nfrom __future__ import annotations


from modules.inference.models.inference_model import InferenceResult
from modules.inference.models.threat_model import ThreatReport


async def compare_architectures(
    inference_a: InferenceResult,
    inference_b: InferenceResult,
    threat_a: ThreatReport,
    threat_b: ThreatReport,
) -> dict:
    comps_a = {c.label for c in (inference_a.components or [])}
    comps_b = {c.label for c in (inference_b.components or [])}

    added = list(comps_b - comps_a)
    removed = list(comps_a - comps_b)
    common = list(comps_a & comps_b)

    stride_a = threat_a.stride_summary or {}
    stride_b = threat_b.stride_summary or {}

    delta = {}
    for cat in ["spoofing", "tampering", "repudiation", "information_disclosure", "denial_of_service", "elevation_of_privilege"]:
        va = stride_a.get(cat, 0)
        vb = stride_b.get(cat, 0)
        delta[cat] = vb - va

    total_a = sum(stride_a.values())
    total_b = sum(stride_b.values())
    risk_diff = round((threat_b.overall_risk_score or 0) - (threat_a.overall_risk_score or 0), 2)

    vulns_a = {}
    for ca in (threat_a.component_analyses or []):
        for v in (ca.vulnerabilities or []):
            vulns_a[v.cve_id] = v.title
    vulns_b = {}
    for ca in (threat_b.component_analyses or []):
        for v in (ca.vulnerabilities or []):
            vulns_b[v.cve_id] = v.title

    mitigated = [{"cve": cve, "title": title} for cve, title in vulns_a.items() if cve not in vulns_b]
    new_threats_vulns = [{"cve": cve, "title": title} for cve, title in vulns_b.items() if cve not in vulns_a]

    verdict = "ARQUITETURA_B_RECOMENDADA" if risk_diff < 0 else "ARQUITETURA_A_RECOMENDADA" if risk_diff > 0 else "EQUIVALENTES"
    if total_b < total_a:
        verdict = "ARQUITETURA_B_RECOMENDADA"
    elif total_a < total_b:
        verdict = "ARQUITETURA_A_RECOMENDADA"

    return {
        "architecture_a": {
            "id": str(inference_a.id),
            "filename": inference_a.filename,
            "components": comps_a,
            "total_threats": total_a,
            "risk_score": threat_a.overall_risk_score,
            "stride_summary": stride_a,
        },
        "architecture_b": {
            "id": str(inference_b.id),
            "filename": inference_b.filename,
            "components": comps_b,
            "total_threats": total_b,
            "risk_score": threat_b.overall_risk_score,
            "stride_summary": stride_b,
        },
        "diff": {
            "components_added": added,
            "components_removed": removed,
            "components_common": common,
            "stride_delta": delta,
            "risk_delta": risk_diff,
            "vulnerabilities_mitigated": mitigated,
            "vulnerabilities_new": new_threats_vulns,
        },
        "verdict": verdict,
        "summary_text": _build_summary(verdict, risk_diff, len(added), len(removed), len(mitigated), len(new_threats_vulns)),
    }


def _build_summary(verdict: str, risk_diff: float, added: int, removed: int, mitigated: int, new_vulns: int) -> str:
    if verdict == "ARQUITETURA_B_RECOMENDADA":
        parts = ["A Arquitetura B é a recomendada."]
        if risk_diff < 0:
            parts.append(f"Redução de risco de {abs(risk_diff)} pontos.")
        if mitigated > 0:
            parts.append(f"{mitigated} vulnerabilidade(s) mitigada(s).")
        if removed > 0:
            parts.append(f"{removed} componente(s) de risco removido(s).")
        if added > 0:
            parts.append(f"{added} novo(s) componente(s) adicionado(s).")
        if new_vulns > 0:
            parts.append(f"Atenção: {new_vulns} nova(s) vulnerabilidade(s) introduzida(s).")
        return " ".join(parts)
    elif verdict == "ARQUITETURA_A_RECOMENDADA":
        parts = ["A Arquitetura A é a recomendada."]
        if risk_diff > 0:
            parts.append(f"Redução de risco de {risk_diff} pontos em relação à B.")
        if mitigated > 0:
            parts.append(f"{mitigated} vulnerabilidade(s) mitigada(s) na A.")
        return " ".join(parts)
    return "As duas arquiteturas são equivalentes em termos de segurança."
