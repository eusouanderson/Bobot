from __future__ import annotations

from bobot.utils.validation import sanitize_prompt


def _wants_detail(text: str) -> bool:
    keywords = [
        "detalhe",
        "detalhado",
        "encorpado",
        "completo",
        "passo a passo",
        "explica",
    ]
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def build_ask_prompt(question: str) -> str:
    clean = sanitize_prompt(question)
    detail = _wants_detail(clean)
    style = (
        "Responda de forma breve e objetiva em até 5 linhas. "
        "Só detalhe mais se o usuário pedir."
        if not detail
        else "Responda de forma detalhada, com passos e exemplos."
    )
    return (
        f"Você é um assistente técnico de programação. {style}\n\n"
        f"Pergunta: {clean}"
    )


def build_code_prompt(language: str, topic: str) -> str:
    clean_topic = sanitize_prompt(topic)
    clean_lang = sanitize_prompt(language)
    detail = _wants_detail(clean_topic)
    style = (
        "Gere um exemplo curto e funcional. Use comentários mínimos."
        if not detail
        else "Gere um exemplo completo e comentado, com boas práticas."
    )
    return (
        f"{style}\n\n"
        f"Linguagem: {clean_lang}\n"
        f"Tema: {clean_topic}"
    )


def build_debug_prompt(error_text: str) -> str:
    clean = sanitize_prompt(error_text)
    detail = _wants_detail(clean)
    style = (
        "Explique causa provável e solução em poucos passos."
        if not detail
        else "Explique causas, hipóteses e passos detalhados."
    )
    return (
        f"Analise o erro a seguir. {style}\n\n"
        f"Erro: {clean}"
    )


def build_docs_prompt(tech: str) -> str:
    clean = sanitize_prompt(tech)
    detail = _wants_detail(clean)
    style = (
        "Indique a documentação oficial e 3 tópicos-chave."
        if not detail
        else "Indique documentação oficial e explique os conceitos principais."
    )
    return (
        f"{style}\n\n"
        f"Tecnologia: {clean}"
    )
