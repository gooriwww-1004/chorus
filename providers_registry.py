from typing import Awaitable, Callable, Dict
from providers import call_gemini_A, call_gemini_B, call_gemini_C, call_gemini_D

ProviderFunc = Callable[[str], Awaitable[str]]

PROVIDERS: Dict[str, ProviderFunc] = {
    "gemini_A": call_gemini_A,  # 분석가
    "gemini_B": call_gemini_B,  # 검증가
    "gemini_C": call_gemini_C,  # 선생님
    "gemini_D": call_gemini_D,  # 브레인스토머
}
