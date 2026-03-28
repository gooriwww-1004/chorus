import asyncio, random, json
from typing import Any, Dict, List
import google.generativeai as genai
from config import CATEGORY_PROVIDERS, GEMINI_API_KEY
from providers_registry import PROVIDERS, ProviderFunc

SUMMARIZER_MODEL = "gemini-2.5-flash"
summarizer_model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    summarizer_model = genai.GenerativeModel(SUMMARIZER_MODEL)

ROLE_LABELS = {
    "gemini_A": "분석가 (Gemini-A)",
    "gemini_B": "검증가 (Gemini-B)",
    "gemini_C": "선생님 (Gemini-C)",
    "gemini_D": "브레인스토머 (Gemini-D)",
}

async def run_ensemble(question: str, category: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "final_answer": "", "scores": {"agree":0,"fact":0,"diversity":0},
        "accordion_items": [], "models_used": [], "error_type": None,
    }
    provider_names = CATEGORY_PROVIDERS.get(category)
    if not provider_names:
        out["final_answer"] = f"ERROR: '{category}' 카테고리에 할당된 에이전트가 없습니다."
        out["error_type"] = "full"
        return out

    tasks, called = [], []
    for name in provider_names:
        fn: ProviderFunc = PROVIDERS.get(name)
        if fn:
            tasks.append(fn(question))
            called.append(name)

    responses = await asyncio.gather(*tasks, return_exceptions=True)

    raw, successful, errors = {}, {}, 0
    for i, name in enumerate(called):
        r = responses[i]
        if isinstance(r, Exception) or (isinstance(r, str) and r.startswith("ERROR")):
            raw[name] = str(r); errors += 1
        else:
            raw[name] = r; successful[name] = r

    out["models_used"] = called
    if not successful:
        out["final_answer"] = "모든 AI 에이전트가 응답 실패했습니다. 잠시 후 다시 시도해주세요."
        out["error_type"] = "full"
        for n in called:
            out["accordion_items"].append({"model": n, "summary": raw.get(n,"오류")[:100]+"…"})
        return out

    if errors > 0:
        out["error_type"] = "partial"

    summarized = await summarize_answers(question, successful)
    out["final_answer"] = summarized["final_answer"]
    out["scores"]       = summarized["metrics"]
    for n in called:
        s = summarized["summary_by_ai"].get(n)
        if s is None:
            s = (raw.get(n,"")[:100]+"…")
        out["accordion_items"].append({"model": n, "summary": s})
    return out


async def summarize_answers(question: str, answers: Dict[str, str]) -> Dict[str, Any]:
    if not summarizer_model:
        return {
            "final_answer": "Gemini API 키 미설정.",
            "summary_by_ai": {p: a[:100]+"…" for p,a in answers.items()},
            "metrics": {"agree": random.randint(60,90), "fact": random.randint(60,90), "diversity": random.randint(60,90)},
        }

    combined = f"질문: {question}\n\n"
    for p, a in answers.items():
        combined += f"--- {ROLE_LABELS.get(p, p)} ---\n{a}\n\n"

    prompt = f"""
당신은 여러 AI 에이전트의 답변을 종합하는 앙상블 지휘자입니다.
아래 답변들을 분석하고 반드시 JSON만 출력하세요. 설명 없이 JSON만.

{{
  "final_answer": "최종 결론 3~5문단 (한국어)",
  "summary_by_ai": {{"gemini_A": "2줄 요약", "gemini_B": "2줄 요약"}},
  "metrics": {{"agree": 정수, "fact": 정수, "diversity": 정수}}
}}

{combined}
"""
    try:
        resp = await summarizer_model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        parsed = json.loads(resp.text)
        return {
            "final_answer":  parsed.get("final_answer", "요약 실패"),
            "summary_by_ai": parsed.get("summary_by_ai", {}),
            "metrics":       parsed.get("metrics", {"agree":75,"fact":75,"diversity":75}),
        }
    except Exception as e:
        print(f"Summarizer error: {e}")
        return {
            "final_answer": "요약 중 오류 발생. 개별 답변을 참조하세요.",
            "summary_by_ai": {p: a[:100]+"…" for p,a in answers.items()},
            "metrics": {"agree": random.randint(60,90), "fact": random.randint(60,90), "diversity": random.randint(60,90)},
        }
