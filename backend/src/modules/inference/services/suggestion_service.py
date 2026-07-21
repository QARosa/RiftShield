# -\*- coding: utf-8 -\*-\nfrom __future__ import annotations

import base64
import json

from langchain_core.messages import HumanMessage, SystemMessage

from modules.hermes.models.llm_config import HermesConfig

SUGGEST_PROMPT = """Você é o Hermes, Arquiteto de Sistemas Sênior especializado em segurança.

Você recebeu duas imagens de arquiteturas de sistema:
- Arquitetura A (atual)
- Arquitetura B (proposta)

Analise ambas e sugira uma ARQUITETURA C (mesclagem otimizada) que combine o melhor das duas com foco em segurança.

Responda APENAS com um JSON válido no formato abaixo, sem texto adicional:

{
  "nome": "Nome sugestivo para a arquitetura mesclada",
  "descricao": "Descrição textual de 2-3 parágrafos explicando a arquitetura proposta, quais componentes foram mantidos de cada versão e por quê, e como a segurança foi melhorada.",
  "componentes": [
    {"label": "server", "justificativa": "Mantido da A com hardening adicional"},
    {"label": "api_gateway", "justificativa": "Adicionado da B para centralizar autenticação"},
    {"label": "database", "justificativa": "Mantido com criptografia em repouso"},
    {"label": "waf", "justificativa": "Novo componente para proteção contra SQL Injection e XSS"},
    {"label": "redis_cache", "justificativa": "Adicionado para mitigar DoS (cache de respostas)"}
  ],
  "beneficios_seguranca": [
    "Redução de ataques de injeção via WAF",
    "Autenticação centralizada reduz superfície de ataque",
    "Cache distribiuído mitiga ataques de negação de serviço"
  ],
  "stride_expected": {
    "spoofing": 1,
    "tampering": 1,
    "repudiation": 0,
    "information_disclosure": 1,
    "denial_of_service": 1,
    "elevation_of_privilege": 0
  }
}

Use labels de componentes válidos: user, server, database, api, load_balancer, firewall, message_queue, cache, cdn, dns, microservice, gateway, storage, container, identity_provider, waf, api_gateway, redis_cache, cdn_cache, auth_service, monitoring, logging.
"""


def _build_llm(config: dict):
    provider = config.get("provider", "google")
    key_google = config.get("google_api_key", "")
    key_openai = config.get("openai_api_key", "")
    key_deepseek = config.get("deepseek_api_key", "")

    if provider == "google" and key_google:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=key_google, temperature=0.2)
    if provider == "openai" and key_openai:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", api_key=key_openai, temperature=0.2)
    if provider == "deepseek" and key_deepseek:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="deepseek-chat", api_key=key_deepseek, base_url="https://api.deepseek.com/v1", temperature=0.2)
    return None


async def suggest_architecture(
    image_a_bytes: bytes,
    image_b_bytes: bytes,
    filename_a: str,
    filename_b: str,
    user_id: str,
) -> dict:
    config_data = await HermesConfig.find_one(HermesConfig.user_id == user_id)
    if not config_data:
        return {"error": "Hermes não configurado. Configure uma API key primeiro."}

    config = {
        "provider": config_data.provider,
        "google_api_key": config_data.google_api_key,
        "openai_api_key": config_data.openai_api_key,
        "deepseek_api_key": config_data.deepseek_api_key,
    }
    llm = _build_llm(config)
    if llm is None:
        return {"error": "Nenhum provedor de IA configurado."}

    provider = config.get("provider", "")

    if provider == "deepseek":
        b64_a = base64.b64encode(image_a_bytes).decode("utf-8")
        b64_b = base64.b64encode(image_b_bytes).decode("utf-8")
        msg = HumanMessage(content=
            f"Arquitetura A ({filename_a}) e Arquitetura B ({filename_b}) são diagramas de arquitetura de sistema.\n"
            f"Descreva as duas arquiteturas (imagens em base64):\n"
            f"A: data:image/png;base64,{b64_a[:200]}...\n"
            f"B: data:image/png;base64,{b64_b[:200]}...\n\n"
            f"Baseado na descrição, sugira uma Arquitetura C mesclada e otimizada."
        )
    else:
        b64_a = base64.b64encode(image_a_bytes).decode("utf-8")
        b64_b = base64.b64encode(image_b_bytes).decode("utf-8")
        msg = HumanMessage(content=[
            {"type": "text", "text": f"Arquitetura A ({filename_a}):"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_a}"}},
            {"type": "text", "text": f"Arquitetura B ({filename_b}):"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_b}"}},
        ])

    try:
        response = llm.invoke([SystemMessage(content=SUGGEST_PROMPT), msg])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("\n", 1)[0]
        suggestion = json.loads(raw)

        from modules.hermes.models.chat_model import HermesMessage
        await HermesMessage(
            user_id=user_id,
            role="user",
            content=f"✨ Sugestão de Arquitetura gerada: {suggestion.get('nome', 'Arquitetura C')} — {len(suggestion.get('componentes', []))} componentes, {len(suggestion.get('beneficios_seguranca', []))} benefícios de segurança.",
            has_attachment=False,
        ).insert()

        return suggestion
    except Exception as e:
        return {"error": f"Erro ao gerar sugestão: {str(e)}"}
