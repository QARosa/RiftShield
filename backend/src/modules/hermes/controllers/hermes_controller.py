from __future__ import annotations

import base64
import os
import uuid
from typing import Any, cast

from langchain_core.messages import HumanMessage, AIMessage

from modules.hermes.agents.graph import hermes_graph
from modules.hermes.models.chat_model import HermesMessage
from modules.hermes.models.llm_config import HermesConfig

TEMP_DIR = os.path.join(os.getcwd(), "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)


async def _get_past_messages(user_id: str, limit: int = 8):
    msgs = (
        await HermesMessage.find(HermesMessage.user_id == user_id)
        .sort(-HermesMessage.created_at)
        .limit(limit)
        .to_list()
    )
    msgs.reverse()
    return msgs


async def _get_llm_config(user_id: str) -> dict:
    config = await HermesConfig.find_one(HermesConfig.user_id == user_id)
    if not config:
        return {}
    from modules.auth.models.user_model import User
    user_lang = "pt-BR"
    try:
        user = await User.get(user_id)
        if user and user.language:
            user_lang = user.language
    except:
        pass
    return {
        "provider": config.provider,
        "google_api_key": config.google_api_key,
        "openai_api_key": config.openai_api_key,
        "deepseek_api_key": config.deepseek_api_key,
        "google_model": config.google_model,
        "openai_model": config.openai_model,
        "deepseek_model": config.deepseek_model,
        "language": user_lang,
    }


async def chat(message: str, attachment_b64: str | None, user_id: str) -> dict:
    llm_config = await _get_llm_config(user_id)
    if not llm_config or not any([
        llm_config.get("google_api_key"),
        llm_config.get("openai_api_key"),
        llm_config.get("deepseek_api_key"),
    ]):
        return {
            "response": (
                "Hermes não está configurado. Vá em **Configurações → Assistente Hermes** "
                "e adicione uma chave de API (Google Gemini, OpenAI ou DeepSeek) para ativar o assistente."
            ),
            "msg_id": "",
        }

    provider = llm_config.get("provider", "")
    if attachment_b64 and provider == "deepseek":
        return {
            "response": (
                "O **DeepSeek** não suporta análise de imagens. "
                "Para analisar diagramas com imagens, configure o **Google Gemini** ou **OpenAI** como provedor principal, "
                "ou ative o fallback entre provedores nas Configurações."
            ),
            "msg_id": "",
        }

    past = await _get_past_messages(user_id)
    langchain_history = []
    for m in past:
        if m.role == "user":
            langchain_history.append(HumanMessage(content=m.content))
        else:
            langchain_history.append(AIMessage(content=m.content))

    await HermesMessage(
        user_id=user_id,
        role="user",
        content=message,
        has_attachment=bool(attachment_b64),
    ).insert()

    agent_input = message
    if attachment_b64:
        try:
            if "," in attachment_b64:
                base64_data = attachment_b64.split(",")[1]
            else:
                base64_data = attachment_b64
            temp_path = os.path.join(TEMP_DIR, f"hermes_{uuid.uuid4().hex}.png")
            with open(temp_path, "wb") as fh:
                fh.write(base64.b64decode(base64_data))
            agent_input += f"\n\n[IMAGE_PATH]: {temp_path}"
        except Exception as e:
            print(f"Hermes attachment error: {e}")

    messages_to_send = langchain_history + [HumanMessage(content=agent_input)]
    inputs = cast(Any, {
        "messages": messages_to_send,
        "context": {"llm_config": llm_config},
    })
    final_state = hermes_graph.invoke(inputs, config={"recursion_limit": 10})

    raw = final_state["messages"][-1].content
    if isinstance(raw, list):
        ai_response = "\n".join(
            item.get("text", "") for item in raw if isinstance(item, dict) and "text" in item
        )
    else:
        ai_response = str(raw)

    msg = await HermesMessage(
        user_id=user_id,
        role="agent",
        content=ai_response,
    ).insert()

    return {"response": ai_response, "msg_id": str(msg.id)}


async def save_config(user_id: str, data: dict) -> dict:
    config = await HermesConfig.find_one(HermesConfig.user_id == user_id)
    if config:
        for key in ("enabled", "provider", "google_api_key", "openai_api_key",
                     "deepseek_api_key", "google_model", "openai_model", "deepseek_model", "diag_fallback", "fallback_enabled"):
            if key in data:
                setattr(config, key, data[key])
        await config.save()
    else:
        config = HermesConfig(user_id=user_id, **data)
        await config.insert()
    return {"saved": True}


async def get_config(user_id: str) -> dict:
    config = await HermesConfig.find_one(HermesConfig.user_id == user_id)
    if not config:
        return {
            "enabled": True,
            "provider": "google",
            "google_api_key": "",
            "openai_api_key": "",
            "deepseek_api_key": "",
            "google_model": "gemini-2.5-flash-lite",
            "openai_model": "gpt-4o-mini",
            "deepseek_model": "deepseek-chat",
            "diag_fallback": "yolo",
            "fallback_enabled": True,
        }
    return {
        "enabled": config.enabled,
        "provider": config.provider,
        "google_api_key": config.google_api_key or "",
        "openai_api_key": config.openai_api_key or "",
        "deepseek_api_key": config.deepseek_api_key or "",
        "google_model": config.google_model,
        "openai_model": config.openai_model,
        "deepseek_model": config.deepseek_model,
        "diag_fallback": config.diag_fallback,
        "fallback_enabled": config.fallback_enabled,
    }


async def get_history(user_id: str) -> list:
    msgs = (
        await HermesMessage.find(HermesMessage.user_id == user_id)
        .sort(-HermesMessage.created_at)
        .limit(50)
        .to_list()
    )
    msgs.reverse()
    from datetime import timezone, timedelta
    br_tz = timezone(timedelta(hours=-3))
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "has_attachment": m.has_attachment,
            "created_at": m.created_at.astimezone(br_tz).isoformat() if m.created_at else None,
        }
        for m in msgs
    ]


async def log_event(message: str, user_id: str) -> dict:
    await HermesMessage(
        user_id=user_id,
        role="user",
        content=f"⚙️ {message}",
        has_attachment=False,
    ).insert()
    return {"logged": True}


async def delete_message(msg_id: str, user_id: str) -> bool:
    msg = await HermesMessage.get(msg_id)
    if not msg or msg.user_id != user_id:
        return False
    await msg.delete()
    return True
