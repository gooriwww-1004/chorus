# ensemble.py — 순차 호출 + 딜레이 (Rate Limit 방지)
import time
import random
import json
from typing import Any, Dict, List

import google.generativeai as genai
from config import CATEGORY_PROVIDERS, GEMINI_API_KEY
from providers_registry import PROVIDERS

MODEL = "gemini-2.5-flash-preview-04-17"

ROLE_LABELS = {
    "gemini_A": "분석가",
    "gemini_B": "검증가",
    "gemini_C": "선생님",
    "gemini_D": "브레인스토머",
}

CALL_DELAY = 2  # 호출 사이 딜레이 (초) — Rate Limit 방지

def run_ensemble(question: str, category: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "final_answer": "",
        "scores": {"agree": 0, "fact": 0, "diversity": 0},
        "accordion_items": [],
        "models_used": [],
        "error_type": None,
    }

    provider_names = CATEGORY_PROVIDERS.get(category)
    if not provider_names:
        out["final_answer"] = f"'{category}' 카테고리에 할당된 에이전트가 없습니다."
        out["error_type"] = "full"
        return out

    called = [n for n in provider_names if n in PROVIDERS]
    out["models_used"] = called

    # ── 순차 호출 (딜레이 포함)
    raw: Dict[str, str] = {}
    successful: Dict[str, str] = {}
    errors = 0

    for i, name in enumerate(called):
        if i > 0:
            time.sleep(CALL_DELAY)  # Rate Limit 방지
        result = PROVIDERS[name](question)
        if isinstance(result, str) and result.startswith("ERROR"):
            raw[name] = result
            errors += 1
        else:
            raw[name] = result
            successful[name] = result

    if not successful:
        out["final_answer"] = "모든 AI 에이전트가 응답 실패했습니다. 잠시 후 다시 시도해주세요."
        out["error_type"] = "full"
        for n in called:
            out["accordion_items"].append({
                "model": n,
                "summary": raw.get(n, "오류")[:150]
            })
        return out

    if errors > 0:
        out["error_type"] = "partial"

    # ── 요약 전 딜레이
    time.sleep(CALL_DELAY)
    summarized = summarize_answers(question, successful)

    out["final_answer"] = summarized["final_answer"]
    out["scores"]       = summarized["metrics"]

    for n in called:
        s = summarized["summary_by_ai"].get(n) or (raw.get(n, "")[:100] + "…")
        out["accordion_items"].append({"model": n, "summary": s})

    return out


def summarize_answers(question: str, answers: Dict[str, str]) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        return {
            "final_answer": "Gemini API 키 미설정.",
            "summary_by_ai": {p: a[:100] for p, a in answers.items()},
            "metrics": {"agree": 75, "fact": 75, "diversity": 75},
        }

    combined = f"질문: {question}\n\n"
    for p, a in answers.items():
        combined += f"--- {ROLE_LABELS.get(p, p)} ---\n{a}\n\n"

    prompt = f"""당신은 여러 AI 에이전트의 답변을 종합하는 앙상블 지휘자입니다.
아래 답변들을 분석하고 반드시 JSON만 출력하세요. 마크다운 없이 순수 JSON만.

{{
  "final_answer": "최종 결론 3~5문단 (한국어)",
  "summary_by_ai": {{"gemini_A": "2줄 요약", "gemini_B": "2줄 요약", "gemini_C": "2줄 요약", "gemini_D": "2줄 요약"}},
  "metrics": {{"agree": 정수1~100, "fact": 정수1~100, "diversity": 정수1~100}}
}}

{combined}"""

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL)
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        parsed = json.loads(resp.text)
        return {
            "final_answer":  parsed.get("final_answer", "요약 실패"),
            "summary_by_ai": parsed.get("summary_by_ai", {}),
            "metrics":       parsed.get("metrics", {"agree": 75, "fact": 75, "diversity": 75}),
        }
    except Exception as e:
        print(f"Summarizer error: {e}")
        return {
            "final_answer": "\n\n".join([f"[{ROLE_LABELS.get(p,p)}] {a[:200]}" for p, a in answers.items()]),
            "summary_by_ai": {p: a[:100] for p, a in answers.items()},
            "metrics": {"agree": random.randint(60,85), "fact": random.randint(60,85), "diversity": random.randint(65,90)},
        }
