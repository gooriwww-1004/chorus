import google.generativeai as genai
from config import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"  # ← 2.5-flash 업그레이드

SYSTEM_PROMPTS = {
    "gemini_A": "당신은 통계와 데이터에 강한 분석 전문가입니다. 숫자, 확률, 패턴을 중심으로 근거 있는 수치를 제시하며 논리적으로 답변하세요. 반드시 한국어로 답변하세요.",
    "gemini_B": "당신은 냉철하게 정보를 검증하는 비판적 사고 전문가입니다. 오해와 편향을 지적하고 균형 잡힌 시각으로 사실에 집중해 답변하세요. 반드시 한국어로 답변하세요.",
    "gemini_C": "당신은 복잡한 내용을 누구나 이해하기 쉽게 설명하는 선생님입니다. 전문 용어를 피하고 친근한 예시를 들어 핵심을 명확하게 전달하세요. 반드시 한국어로 답변하세요.",
    "gemini_D": "당신은 창의적인 아이디어와 다양한 관점을 제시하는 브레인스토밍 전문가입니다. 일반적인 답변 외에 색다른 시각과 참신한 아이디어를 적극 제안하세요. 반드시 한국어로 답변하세요.",
}

async def _call(role_key: str, user_prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "ERROR: GEMINI_API_KEY가 설정되지 않았습니다."
    try:
        model = genai.GenerativeModel(MODEL, system_instruction=SYSTEM_PROMPTS[role_key])
        resp = await model.generate_content_async(user_prompt)
        return resp.text
    except Exception as e:
        return f"ERROR: {role_key} 호출 실패 — {e}"

async def call_gemini_A(prompt: str) -> str: return await _call("gemini_A", prompt)
async def call_gemini_B(prompt: str) -> str: return await _call("gemini_B", prompt)
async def call_gemini_C(prompt: str) -> str: return await _call("gemini_C", prompt)
async def call_gemini_D(prompt: str) -> str: return await _call("gemini_D", prompt)
