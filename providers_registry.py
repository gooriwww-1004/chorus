from typing import Callable, Dict
from providers import call_gemini_A, call_gemini_B, call_gemini_C, call_gemini_D

# 동기 함수 타입
ProviderFunc = Callable[[str], str]

PROVIDERS: Dict[str, ProviderFunc] = {
    "gemini_A": call_gemini_A,
    "gemini_B": call_gemini_B,
    "gemini_C": call_gemini_C,
    "gemini_D": call_gemini_D,
}
