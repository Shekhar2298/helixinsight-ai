from __future__ import annotations
import json
import httpx
from .config import settings

SYSTEM_RULES = """You are generating a research bioinformatics summary. Use ONLY the supplied evidence.
Do not diagnose disease, recommend treatment, or turn exploratory associations into clinical claims.
Every factual biological statement must include an evidence marker such as [1]. If evidence is insufficient, say so."""


def deterministic_report(title: str, analysis: dict, evidence: list[dict]) -> dict:
    refs = []
    for i, item in enumerate(evidence, 1):
        refs.append({"index": i, "name": item.get("name", "Evidence"), "url": item.get("url")})
    body = [f"# {title}", "", "## Analysis summary", "```json", json.dumps(analysis, indent=2), "```", ""]
    if refs:
        body += ["## Evidence"] + [f"[{r['index']}] {r['name']}: {r['url']}" for r in refs]
    body += ["", "## Interpretation", "Results are exploratory research outputs and require independent biological and statistical validation."]
    return {"report_markdown": "\n".join(body), "references": refs, "generator": "deterministic"}


async def grounded_report(title: str, analysis: dict, evidence: list[dict]) -> dict:
    if not (settings.llm_base_url and settings.llm_api_key and settings.llm_model):
        return deterministic_report(title, analysis, evidence)

    refs = [{"index": i + 1, **e} for i, e in enumerate(evidence)]
    prompt = {"title": title, "analysis": analysis, "evidence": refs}
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": json.dumps(prompt)},
        ],
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(f"{settings.llm_base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    return {"report_markdown": content, "references": refs, "generator": settings.llm_model}
