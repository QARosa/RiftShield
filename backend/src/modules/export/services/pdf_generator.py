from __future__ import annotations

import base64
import io
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

BR_TIMEZONE = timezone(timedelta(hours=-3))


def _now_br() -> datetime:
    return datetime.now(timezone.utc).astimezone(BR_TIMEZONE)


TEMPLATE_PATH = __file__.replace("pdf_generator.py", "") + "../templates/report_pdf.html"


def _labels(lang: str) -> dict:
    is_en = lang.startswith("en")
    return {
        "lang": "en" if is_en else "pt-BR",
        "resumo": "Summary" if is_en else "Resumo Geral",
        "resumo_desc": "Overview of exported RiftShield data." if is_en else "Visão geral dos dados exportados do RiftShield.",
        "analises": "Analyses Performed" if is_en else "Análises Realizadas",
        "relatorios_stride": "STRIDE Reports" if is_en else "Relatórios STRIDE",
        "imagens_dataset": "Images in Dataset" if is_en else "Imagens no Dataset",
        "treinamentos": "Trainings" if is_en else "Treinamentos",
        "vuln_base": "Vulnerabilities in KB" if is_en else "Vulnerabilidades na Base",
        "cm_base": "Countermeasures in KB" if is_en else "Contramedidas na Base",
        "analise_diagramas": "Diagram Analysis" if is_en else "Análise de Diagramas",
        "status_analises": "Analysis Status" if is_en else "Status das Análises",
        "quantidade": "Quantity" if is_en else "Quantidade",
        "concluidas": "Completed" if is_en else "Concluídas",
        "com_fallback": "With AI Fallback" if is_en else "Com Fallback IA",
        "arquivo": "File" if is_en else "Arquivo",
        "status": "Status" if is_en else "Status",
        "componentes": "Components" if is_en else "Componentes",
        "tempo": "Time" if is_en else "Tempo",
        "mostrando": lambda n, total: f"Showing up to {n} of {total} analyses." if is_en else f"Mostrando até {n} de {total} análises.",
        "total": lambda n: f"Total of {n} analyses performed." if is_en else f"Total de {n} análises realizadas.",
        "distribuicao_stride": "STRIDE Threat Distribution" if is_en else "Distribuição de Ameaças STRIDE",
        "ocorrencias": "Occurrences" if is_en else "Ocorrências",
        "relatorios": "STRIDE Reports" if is_en else "Relatórios STRIDE",
        "total_relatorios": "Total Reports" if is_en else "Total de Relatórios",
        "risco_medio": "Average Risk" if is_en else "Risco Médio",
        "id": "ID" if is_en else "ID",
        "risco": "Risk" if is_en else "Risco",
        "ameacas": "Threats" if is_en else "Ameaças",
        "mostrando_relatorios": lambda n, total: f"Showing up to {n} of {total} reports." if is_en else f"Mostrando até {n} de {total} relatórios.",
        "total_relatorios_desc": lambda n: f"Total of {n} threat modeling reports." if is_en else f"Total de {n} relatórios de modelagem de ameaças.",
        "dataset_title": "Dataset" if is_en else "Dataset",
        "dataset_desc": lambda n: f"Total of {n} images in training dataset." if is_en else f"Total de {n} imagens no dataset para treinamento.",
        "treino": "Training" if is_en else "Treino",
        "validacao": "Validation" if is_en else "Validação",
        "teste": "Test" if is_en else "Teste",
        "split_dataset": "Dataset Split" if is_en else "Split do Dataset",
        "split": "Split" if is_en else "Split",
        "origem": "Source" if is_en else "Origem",
        "labels": "Labels" if is_en else "Labels",
        "mostrando_dataset": lambda n, total: f"Showing up to {n} of {total} entries." if is_en else f"Mostrando até {n} de {total} entradas.",
        "treinamento_modelos": "Model Training" if is_en else "Treinamento de Modelos",
        "treinamento_desc": lambda n: f"Total of {n} training/fine-tune sessions." if is_en else f"Total de {n} sessões de treinamento/fine-tune.",
        "concluidos": "Completed" if is_en else "Concluídos",
        "falhos": "Failed" if is_en else "Falhos",
        "performance_modelos": "Model Performance" if is_en else "Performance dos Modelos",
        "modelo": "Model" if is_en else "Modelo",
        "epocas": "Epochs" if is_en else "Épocas",
        "data": "Date" if is_en else "Data",
        "mostrando_treinamento": lambda n, total: f"Showing up to {n} of {total} trainings." if is_en else f"Mostrando até {n} de {total} treinamentos.",
        "vuln_title": "Vulnerability Database" if is_en else "Base de Vulnerabilidades",
        "vuln_desc": lambda n: f"Total of {n} vulnerabilities cataloged in the knowledge base." if is_en else f"Total de {n} vulnerabilidades catalogadas na base de conhecimento.",
        "total_vuln": "Total" if is_en else "Total",
        "criticas": "Critical" if is_en else "Críticas",
        "altas": "High" if is_en else "Altas",
        "severidade": "Vulnerability Severity" if is_en else "Severidade das Vulnerabilidades",
        "baixo": "Low" if is_en else "Baixo",
        "medio": "Medium" if is_en else "Médio",
        "alto": "High" if is_en else "Alto",
        "critico": "Critical" if is_en else "Crítico",
        "cve": "CVE" if is_en else "CVE",
        "titulo": "Title" if is_en else "Título",
        "cvss": "CVSS" if is_en else "CVSS",
        "tags": "Tags" if is_en else "Tags",
        "mostrando_vuln": lambda n, total: f"Showing up to {n} of {total} vulnerabilities." if is_en else f"Mostrando até {n} de {total} vulnerabilidades.",
        "cm_title": "Countermeasure Database" if is_en else "Base de Contramedidas",
        "cm_desc": lambda n: f"Total of {n} countermeasures available." if is_en else f"Total de {n} contramedidas disponíveis.",
        "criticas_cm": "Critical" if is_en else "Críticas",
        "altas_cm": "High" if is_en else "Altas",
        "contramedida": "Countermeasure" if is_en else "Contramedida",
        "prioridade": "Priority" if is_en else "Prioridade",
        "cwes": "CWEs" if is_en else "CWEs",
        "mostrando_cm": lambda n, total: f"Showing up to {n} of {total} countermeasures." if is_en else f"Mostrando até {n} de {total} contramedidas.",
        "perfil": "User Profile" if is_en else "Perfil do Usuário",
        "perfil_desc": "User registration information." if is_en else "Informações cadastrais do usuário.",
        "campo": "Field" if is_en else "Campo",
        "valor": "Value" if is_en else "Valor",
        "nome": "Name" if is_en else "Nome",
        "email": "Email" if is_en else "Email",
        "profissao": "Profession" if is_en else "Profissão",
        "senioridade": "Seniority" if is_en else "Senioridade",
        "idioma": "Language" if is_en else "Idioma",
        "dias_ativo": "Active Days" if is_en else "Dias Ativo",
        "config": "Settings" if is_en else "Configurações",
        "config_desc": "Hermes assistant preferences." if is_en else "Preferências do assistente Hermes.",
        "configuracao": "Setting" if is_en else "Configuração",
        "hermes_ativo": "Hermes Active" if is_en else "Hermes Ativo",
        "sim": "Yes" if is_en else "Sim",
        "nao": "No" if is_en else "Não",
        "provedor_ia": "AI Provider" if is_en else "Provedor IA",
        "fallback_diagramas": "Diagram Fallback" if is_en else "Fallback Diagramas",
        "map_epochs": "mAP@0.5 / Epochs" if is_en else "mAP@0.5 / Épocas",
        "nenhuma_ameaca": "No threats identified" if is_en else "Nenhuma ameaça identificada",
        "spoofing": "Spoofing",
        "tampering": "Tampering",
        "repudiation": "Repudiation" if is_en else "Repudiação",
        "information_disclosure": "Info Disclosure" if is_en else "Exposição de Info",
        "denial_of_service": "DoS",
        "elevation_of_privilege": "Privilege Escalation" if is_en else "Elevação de Privilégio",
    }


def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _chart_inferences(items: List[Dict], L: dict) -> Optional[str]:
    if not items:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    statuses = {}
    for i in items:
        s = i.get("status", "unknown")
        statuses[s] = statuses.get(s, 0) + 1

    fig, ax = plt.subplots(figsize=(5, 2.5))
    colors = {"completed": "#16a34a", "failed": "#dc2626", "processing": "#2563eb", "pending": "#ca8a04"}
    bars = ax.bar(statuses.keys(), statuses.values(), color=[colors.get(k, "#888") for k in statuses.keys()])
    ax.set_title(L["status_analises"], fontsize=11, color="#333")
    ax.set_ylabel(L["quantidade"], fontsize=9)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, str(int(bar.get_height())), ha="center", fontsize=9)
    plt.tight_layout()
    b64 = _fig_to_b64(fig)
    plt.close()
    return b64


def _chart_threats(items: List[Dict], L: dict) -> Optional[str]:
    if not items:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    stride_totals = {"spoofing": 0, "tampering": 0, "repudiation": 0,
                     "information_disclosure": 0, "denial_of_service": 0, "elevation_of_privilege": 0}
    for r in items:
        ss = r.get("stride_summary", {})
        for k in stride_totals:
            stride_totals[k] += ss.get(k, 0)

    labels_map = {k: L[k] for k in stride_totals}
    cats = list(stride_totals.keys())
    vals = list(stride_totals.values())
    lbls = [labels_map.get(c, c) for c in cats]
    colors_ride = ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#8b5cf6", "#ec4899"]

    fig, ax = plt.subplots(figsize=(5.5, 2.8))
    bars = ax.bar(lbls, vals, color=colors_ride)
    ax.set_title(L["distribuicao_stride"], fontsize=11, color="#333")
    ax.set_ylabel(L["ocorrencias"], fontsize=9)
    for bar in bars:
        if bar.get_height() > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, str(int(bar.get_height())), ha="center", fontsize=8)
    plt.tight_layout()
    b64 = _fig_to_b64(fig)
    plt.close()
    return b64


def _chart_dataset(items: List[Dict], L: dict) -> Optional[str]:
    if not items:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    splits = {}
    for e in items:
        s = e.get("split", "unknown")
        splits[s] = splits.get(s, 0) + 1

    fig, ax = plt.subplots(figsize=(3.5, 3))
    colors_pie = {"train": "#16a34a", "val": "#2563eb", "test": "#8b5cf6"}
    wedges, texts, autotexts = ax.pie(
        splits.values(), labels=splits.keys(), autopct="%1.0f%%",
        colors=[colors_pie.get(k, "#888") for k in splits.keys()],
        startangle=90
    )
    ax.set_title(L["split_dataset"], fontsize=11, color="#333")
    plt.tight_layout()
    b64 = _fig_to_b64(fig)
    plt.close()
    return b64


def _chart_vulnerabilities(items: List[Dict], L: dict) -> Optional[str]:
    if not items:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scores = [v.get("cvss_score", 0) or 0 for v in items]
    labels_bins = [L["baixo"], L["medio"], L["alto"], L["critico"]]
    counts = [0] * 4
    for s in scores:
        if s >= 9:
            counts[3] += 1
        elif s >= 7:
            counts[2] += 1
        elif s >= 4:
            counts[1] += 1
        else:
            counts[0] += 1

    fig, ax = plt.subplots(figsize=(4, 2.5))
    colors_cvss = ["#16a34a", "#ca8a04", "#ea580c", "#dc2626"]
    bars = ax.bar(labels_bins, counts, color=colors_cvss)
    ax.set_title(L["severidade"], fontsize=11, color="#333")
    ax.set_ylabel(L["quantidade"], fontsize=9)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, str(int(bar.get_height())), ha="center", fontsize=9)
    plt.tight_layout()
    b64 = _fig_to_b64(fig)
    plt.close()
    return b64


def _chart_training(items: List[Dict], L: dict) -> Optional[str]:
    completed = [t for t in items if t.get("status") == "completed"]
    if not completed:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = [t.get("model_type", "model") for t in completed]
    accs = []
    for t in completed:
        m = t.get("metrics", {})
        accs.append(m.get("mAP50", m.get("fine_tune_epochs", 0)) or 0)

    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.bar(names, accs, color="#e65c00")
    ax.set_title(L["performance_modelos"], fontsize=11, color="#333")
    ax.set_ylabel(L["map_epochs"], fontsize=9)
    plt.tight_layout()
    b64 = _fig_to_b64(fig)
    plt.close()
    return b64


def _stride_summary_text(stride: Dict[str, int], L: dict) -> str:
    parts = []
    labels = {k: L[k] for k in ["spoofing", "tampering", "repudiation", "information_disclosure", "denial_of_service", "elevation_of_privilege"]}
    for k, v in stride.items():
        if v > 0:
            parts.append(f"{labels.get(k, k)}: {v}")
    return ", ".join(parts) if parts else L["nenhuma_ameaca"]


def build_pdf_sections(
    inferences: List[Dict],
    threats: List[Dict],
    dataset: List[Dict],
    training_logs: List[Dict],
    vulnerabilities: List[Dict],
    countermeasures: List[Dict],
    profile: Optional[Dict] = None,
    settings: Optional[Dict] = None,
    lang: str = "pt-BR",
) -> List[Dict]:
    L = _labels(lang)
    sections = []

    stats = [
        {"value": len(inferences), "label": L["analises"]},
        {"value": len(threats), "label": L["relatorios_stride"]},
        {"value": len(dataset), "label": L["imagens_dataset"]},
        {"value": len(training_logs), "label": L["treinamentos"]},
        {"value": len(vulnerabilities), "label": L["vuln_base"]},
        {"value": len(countermeasures), "label": L["cm_base"]},
    ]
    sections.append({
        "title": L["resumo"],
        "description": L["resumo_desc"],
        "stats": stats,
    })

    chart_inf = _chart_inferences(inferences, L)
    inf_table = []
    for i in inferences[:20]:
        comps = ", ".join(c.get("label", "?") for c in (i.get("components") or [])[:3])
        inf_table.append([i.get("filename", "-")[:30], i.get("status", "-"), comps or "-",
                          f'{i.get("processing_time_ms", 0):.0f}ms' if i.get("processing_time_ms") else "-"])
    sections.append({
        "title": L["analise_diagramas"],
        "description": L["total"](len(inferences)),
        "stats": [
            {"value": len([i for i in inferences if i.get("status") == "completed"]), "label": L["concluidas"]},
            {"value": len([i for i in inferences if i.get("fallback_used")]), "label": L["com_fallback"]},
        ],
        "chart": chart_inf,
        "table_headers": [L["arquivo"], L["status"], L["componentes"], L["tempo"]],
        "table_rows": inf_table,
        "table_note": L["mostrando"](20, len(inferences)) if len(inferences) > 20 else None,
    })

    chart_thr = _chart_threats(threats, L)
    thr_table = []
    for r in threats[:20]:
        risk = r.get("overall_risk_score", 0) or 0
        risk_str = f'{risk:.1f}/10'
        stride_text = _stride_summary_text(r.get("stride_summary", {}), L)
        thr_table.append([str(r.get("id", "-"))[:12], r.get("status", "-"), risk_str, stride_text])
    sections.append({
        "title": L["relatorios"],
        "description": L["total_relatorios_desc"](len(threats)),
        "stats": [
            {"value": len(threats), "label": L["total_relatorios"]},
            {"value": sum(t.get("overall_risk_score", 0) or 0 for t in threats) / max(len(threats), 1), "label": L["risco_medio"]},
        ],
        "chart": chart_thr,
        "table_headers": [L["id"], L["status"], L["risco"], L["ameacas"]],
        "table_rows": thr_table,
        "table_note": L["mostrando_relatorios"](20, len(threats)) if len(threats) > 20 else None,
    })

    chart_ds = _chart_dataset(dataset, L)
    ds_table = []
    for e in dataset[:20]:
        ds_table.append([e.get("filename", "-")[:30], e.get("split", "-"), e.get("source", "-"),
                         str(len(e.get("labels", [])))])
    sections.append({
        "title": L["dataset_title"],
        "description": L["dataset_desc"](len(dataset)),
        "stats": [
            {"value": len([e for e in dataset if e.get("split") == "train"]), "label": L["treino"]},
            {"value": len([e for e in dataset if e.get("split") == "val"]), "label": L["validacao"]},
            {"value": len([e for e in dataset if e.get("split") == "test"]), "label": L["teste"]},
        ],
        "chart": chart_ds,
        "table_headers": [L["arquivo"], L["split"], L["origem"], L["labels"]],
        "table_rows": ds_table,
        "table_note": L["mostrando_dataset"](20, len(dataset)) if len(dataset) > 20 else None,
    })

    chart_tr = _chart_training(training_logs, L)
    tr_table = []
    for t in training_logs[:20]:
        tr_table.append([t.get("model_type", "-"), t.get("status", "-"),
                         str(t.get("hyperparameters", {}).get("epochs", "-")),
                         t.get("created_at", "-")[:10] if t.get("created_at") else "-"])
    sections.append({
        "title": L["treinamento_modelos"],
        "description": L["treinamento_desc"](len(training_logs)),
        "stats": [
            {"value": len([t for t in training_logs if t.get("status") == "completed"]), "label": L["concluidos"]},
            {"value": len([t for t in training_logs if t.get("status") == "failed"]), "label": L["falhos"]},
        ],
        "chart": chart_tr,
        "table_headers": [L["modelo"], L["status"], L["epocas"], L["data"]],
        "table_rows": tr_table,
        "table_note": L["mostrando_treinamento"](20, len(training_logs)) if len(training_logs) > 20 else None,
    })

    chart_vuln = _chart_vulnerabilities(vulnerabilities, L)
    vuln_table = []
    for v in vulnerabilities[:25]:
        tags = ", ".join((v.get("tags") or [])[:3])
        vuln_table.append([v.get("cve_id", "-"), v.get("title", "-")[:40],
                           f'{v.get("cvss_score", "-")}', tags])
    sections.append({
        "title": L["vuln_title"],
        "description": L["vuln_desc"](len(vulnerabilities)),
        "stats": [
            {"value": len(vulnerabilities), "label": L["total_vuln"]},
            {"value": len([v for v in vulnerabilities if (v.get("cvss_score") or 0) >= 9]), "label": L["criticas"]},
            {"value": len([v for v in vulnerabilities if 7 <= (v.get("cvss_score") or 0) < 9]), "label": L["altas"]},
        ],
        "chart": chart_vuln,
        "table_headers": [L["cve"], L["titulo"], L["cvss"], L["tags"]],
        "table_rows": vuln_table,
        "table_note": L["mostrando_vuln"](25, len(vulnerabilities)) if len(vulnerabilities) > 25 else None,
    })

    cm_table = []
    for c in countermeasures[:20]:
        cm_table.append([c.get("title", "-")[:45], c.get("priority", "-"),
                         ", ".join((c.get("vulnerability_cwe_ids") or [])[:3])])
    sections.append({
        "title": L["cm_title"],
        "description": L["cm_desc"](len(countermeasures)),
        "stats": [
            {"value": len([c for c in countermeasures if c.get("priority") == "critical"]), "label": L["criticas_cm"]},
            {"value": len([c for c in countermeasures if c.get("priority") == "high"]), "label": L["altas_cm"]},
        ],
        "table_headers": [L["contramedida"], L["prioridade"], L["cwes"]],
        "table_rows": cm_table,
        "table_note": L["mostrando_cm"](20, len(countermeasures)) if len(countermeasures) > 20 else None,
    })

    if profile:
        prof_items = [
            [L["nome"], profile.get("name", "-")],
            [L["email"], profile.get("email", "-")],
            [L["profissao"], profile.get("profession", "-") or "-"],
            [L["senioridade"], profile.get("seniority", "-") or "-"],
            [L["idioma"], profile.get("language", "pt-BR")],
            [L["dias_ativo"], str(profile.get("total_days_active", 0))],
        ]
        sections.append({
            "title": L["perfil"],
            "description": L["perfil_desc"],
            "table_headers": [L["campo"], L["valor"]],
            "table_rows": prof_items,
        })

    if settings:
        sett_items = [
            [L["hermes_ativo"], L["sim"] if settings.get("enabled") else L["nao"]],
            [L["provedor_ia"], settings.get("provider", "-")],
            [L["fallback_diagramas"], settings.get("diag_fallback", "yolo")],
        ]
        sections.append({
            "title": L["config"],
            "description": L["config_desc"],
            "table_headers": [L["configuracao"], L["valor"]],
            "table_rows": sett_items,
        })

    return sections


def generate_pdf(sections_data: List[Dict], generation_date: str, profile: Optional[Dict] = None, lang: str = "pt-BR") -> bytes:
    from jinja2 import Template

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template_str = f.read()

    L = _labels(lang)

    template = Template(template_str)
    html = template.render(
        sections=sections_data,
        generation_date=generation_date,
        profile=profile,
        labels=L,
    )

    from weasyprint import HTML
    pdf_bytes = HTML(string=html).write_pdf()
    return pdf_bytes
