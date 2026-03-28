# app.py — CHORUS AI v0.4  |  Gemini 2.5-Flash Ensemble  |  Cyberpunk UI

import asyncio
import streamlit as st
from ensemble import run_ensemble
from config import CATEGORY_PROVIDERS, CATEGORY_LABELS

st.set_page_config(
    page_title="CHORUS AI · 앙상블 Q&A",
    page_icon="🔮",
    layout="centered",
)

if "category" not in st.session_state:
    st.session_state.category = "sports"

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #060410 !important; }
[data-testid="stAppViewContainer"] { background: #060410; }
[data-testid="stHeader"] { background: transparent; }

/* 회로기판 패턴 */
.stApp::before {
    content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Cpath d='M0 40 H30 M50 40 H80 M40 0 V30 M40 50 V80' stroke='%231a0840' stroke-width='1' fill='none'/%3E%3Ccircle cx='40' cy='40' r='4' fill='none' stroke='%231a0840' stroke-width='1'/%3E%3Ccircle cx='30' cy='40' r='2' fill='%231a0840'/%3E%3Ccircle cx='50' cy='40' r='2' fill='%231a0840'/%3E%3Ccircle cx='40' cy='30' r='2' fill='%231a0840'/%3E%3Ccircle cx='40' cy='50' r='2' fill='%231a0840'/%3E%3Cpath d='M5 5 H20 V20 H5 Z' stroke='%231a0840' stroke-width='.5' fill='none'/%3E%3Cpath d='M60 60 H75 V75 H60 Z' stroke='%231a0840' stroke-width='.5' fill='none'/%3E%3C/svg%3E");
}
.stApp::after {
    content:""; position:fixed; inset:0; z-index:1; pointer-events:none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1' height='4'%3E%3Crect width='1' height='2' fill='%23000' opacity='.05'/%3E%3C/svg%3E");
    background-size: 1px 4px;
}
[data-testid="stAppViewContainer"] > * { position:relative; z-index:2; }

* { font-family:'Courier New','D2Coding',monospace !important; }
p, span, label, div { color:#c4b5fd !important; }
h1,h2,h3,h4 { color:#e2d9f3 !important; letter-spacing:-0.02em; }

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
.block-container { background:transparent !important; padding-top:1.5rem !important; }

textarea, input[type="text"] {
    background:#08031a !important; border:1px solid #2d0f60 !important;
    border-radius:10px !important; color:#a78bfa !important; font-size:14px !important;
}
textarea:focus, input:focus {
    border-color:#7c3aed !important;
    box-shadow:0 0 0 2px rgba(124,58,237,0.25) !important;
}

/* 카테고리 버튼 — 기본: 2줄 높이 확보 */
.stButton > button {
    background:transparent !important;
    border:1px solid #2d0f60 !important;
    border-radius:8px !important;
    color:#5a4f8a !important;
    font-size:11px !important;
    letter-spacing:0.03em !important;
    transition:all 0.15s !important;
    white-space:pre-wrap !important;
    line-height:1.5 !important;
    padding:8px 4px !important;
    min-height:52px !important;
}
.stButton > button:hover {
    background:#12063a !important;
    border-color:#7c3aed !important;
    color:#c4b5fd !important;
}

/* 실행 버튼 */
.exec-btn > div > button {
    background:#6d28d9 !important;
    border:1px solid #5b21b6 !important;
    color:#ffffff !important;
    font-weight:700 !important;
    font-size:14px !important;
    letter-spacing:0.06em !important;
    min-height:48px !important;
}
.exec-btn > div > button:hover { background:#5b21b6 !important; }

/* 네온 구분선 — 앱 전체 공통 */
hr {
    border: none !important;
    border-top: 2px solid #c084fc !important;
    box-shadow: 0 0 6px rgba(192,132,252,0.5) !important;
    margin: 14px 0 !important;
}
.neon-divider {
    border: none;
    border-top: 2px solid #c084fc;
    box-shadow: 0 0 6px rgba(192,132,252,0.5);
    margin: 14px 0;
}

[data-testid="stMetric"] {
    background:#08031a; border:1px solid #2d0f60;
    border-radius:10px; padding:14px 16px;
}
[data-testid="stMetricLabel"] p { color:#5a4f8a !important; font-size:11px !important; }
[data-testid="stMetricValue"] { color:#a78bfa !important; font-size:22px !important; font-weight:700 !important; }

[data-testid="stExpander"] {
    background:#08031a !important; border:1px solid #2d0f60 !important; border-radius:8px !important;
}
[data-testid="stExpander"] summary { color:#6b5fa0 !important; font-size:12px !important; }
[data-testid="stExpander"] p { color:#5a4f8a !important; font-size:12px !important; line-height:1.7 !important; }

[data-testid="stAlert"] {
    background:#08031a !important; border-left:3px solid #7c3aed !important; border-radius:6px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── 브랜드 헤더 ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:flex-start;padding:8px 0 4px;">
  <div>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
      <div style="width:28px;height:28px;border:1.5px solid #7c3aed;transform:rotate(45deg);
           display:flex;align-items:center;justify-content:center;">
        <div style="width:10px;height:10px;background:#7c3aed;"></div>
      </div>
      <span style="color:#c4b5fd !important;font-size:22px;font-weight:800;letter-spacing:0.18em;">CHORUS AI</span>
    </div>
    <div style="color:#6b5fa0 !important;font-size:12px;">질문 하나로 AI 팀 전체를 움직이세요.</div>
    <div style="color:#3b1a6e !important;font-size:10px;margin-top:2px;">// Gemini 2.5-Flash 4-Role Ensemble · v0.4-beta</div>
  </div>
  <div style="display:flex;align-items:center;gap:6px;border:1px solid #2d0f60;
       border-radius:20px;padding:5px 12px;background:#0a0520;">
    <div style="width:6px;height:6px;border-radius:50%;background:#10b981;"></div>
    <span style="color:#6ee7b7 !important;font-size:10px;letter-spacing:0.1em;">4 AGENTS READY</span>
  </div>
</div>
<hr class="neon-divider">
""", unsafe_allow_html=True)

# ─── 질문 입력 ───────────────────────────────────────────────────────────────
st.markdown('<div style="color:#3b1a6e;font-size:10px;letter-spacing:0.1em;margin-bottom:8px;">QUERY_INPUT://</div>',
            unsafe_allow_html=True)

question = st.text_area(
    " ", label_visibility="collapsed",
    placeholder="무엇이든 물어보세요. Gemini 2.5-Flash 4명의 팀이 함께 답을 찾습니다.",
    height=130,
)

# ─── 카테고리 선택 ───────────────────────────────────────────────────────────
st.markdown('<div style="color:#3b1a6e;font-size:10px;letter-spacing:0.1em;margin:14px 0 8px;">MODULE_SELECT://</div>',
            unsafe_allow_html=True)

# 2라인 레이블 (이모지 + 텍스트 줄바꿈)
CAT_BTN_LABELS = {
    "sports":  "🏆\n스포츠·로또",
    "science": "🔬\n과학·기술",
    "work":    "📚\n일·공부",
    "daily":   "💬\n연애·일상",
}

cat_cols = st.columns(4)
for i, key in enumerate(CAT_BTN_LABELS.keys()):
    with cat_cols[i]:
        is_active = (st.session_state.category == key)
        # 활성 상태: 이모지 앞에 ▮ 추가, 괄호 없음
        label = ("▮ " if is_active else "") + CAT_BTN_LABELS[key]
        if st.button(label, key=f"cat_{key}", use_container_width=True):
            st.session_state.category = key
            st.rerun()

selected_label = CATEGORY_LABELS[st.session_state.category]
st.markdown(f'<div style="color:#7c3aed;font-size:10px;margin:6px 0 16px;">// SELECTED: {selected_label}</div>',
            unsafe_allow_html=True)

# ─── 실행 버튼 ───────────────────────────────────────────────────────────────
st.markdown('<div class="exec-btn">', unsafe_allow_html=True)
run_clicked = st.button("▶  EXECUTE ENSEMBLE  ·  앙상블 실행", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── 대기 에이전트 상태 (텍스트) ─────────────────────────────────────────────
if not run_clicked:
    st.markdown("""
    <div style="margin-top:20px;">
      <div style="color:#3b1a6e;font-size:10px;letter-spacing:0.1em;margin-bottom:6px;">AGENT_STATUS://</div>
      <div style="color:#2d0f60;font-size:11px;font-family:monospace;line-height:1.8;">
        GMN-A · 분석가 &nbsp;|&nbsp; GMN-B · 검증가 &nbsp;|&nbsp;
        GMN-C · 선생님 &nbsp;|&nbsp; GMN-D · 브레인스토머 &nbsp;|&nbsp; GMN-∑ · 지휘자
      </div>
      <div style="color:#1e0845;font-size:10px;margin-top:4px;">// 대기 중 · 질문 입력 후 실행하세요</div>
    </div>
    """, unsafe_allow_html=True)

# ─── 앙상블 실행 ─────────────────────────────────────────────────────────────
def run_sync(q, cat):
    return asyncio.run(run_ensemble(q, cat))

if run_clicked:
    if not question.strip():
        st.warning("// QUERY_EMPTY: 질문을 입력해 주세요.")
    else:
        # 처리 중 — 텍스트로 단순화
        st.markdown("""
        <div style="margin:12px 0 10px;padding:12px 16px;background:#08031a;
             border-left:2px solid #a78bfa;border-radius:6px;">
          <div style="color:#8b5cf6;font-size:11px;margin-bottom:4px;">// PROCESSING...</div>
          <div style="color:#5a4f8a;font-size:10px;line-height:1.8;">
            GMN-A 생각 중 &nbsp;·&nbsp; GMN-B 생각 중 &nbsp;·&nbsp;
            GMN-C 생각 중 &nbsp;·&nbsp; GMN-D 생각 중 &nbsp;·&nbsp; GMN-∑ 생각 중
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("// Gemini 2.5-Flash 4명이 회의 중이에요…"):
            try:
                result = run_sync(question, st.session_state.category)
            except Exception as e:
                st.error(f"// ENGINE_ERROR: {e}")
                result = None

        if result:
            final_answer    = result.get("final_answer", "답변 생성 실패")
            scores          = result.get("scores", {})
            accordion_items = result.get("accordion_items", [])
            models_used     = result.get("models_used", [])
            error_type      = result.get("error_type")

            # 완료 상태 — 텍스트
            st.markdown("""
            <div style="margin:0 0 16px;padding:10px 16px;background:#08031a;
                 border-left:2px solid #10b981;border-radius:6px;">
              <div style="color:#6ee7b7;font-size:10px;">
                ✓ GMN-A 완료 &nbsp;·&nbsp; ✓ GMN-B 완료 &nbsp;·&nbsp;
                ✓ GMN-C 완료 &nbsp;·&nbsp; ✓ GMN-D 완료 &nbsp;·&nbsp; ✓ GMN-∑ 완료
              </div>
            </div>
            """, unsafe_allow_html=True)

            # 최종 답변 카드
            st.markdown('<div style="color:#7c3aed;font-size:10px;letter-spacing:0.1em;margin-bottom:6px;">// ENSEMBLE_RESULT · FINAL_OUTPUT</div>',
                        unsafe_allow_html=True)
            st.markdown(f'''
            <div style="background:#08031a;border:1px solid #2d0f60;border-left:2px solid #7c3aed;
                 border-radius:10px;padding:16px 18px;margin-bottom:16px;">
              <p style="color:#c4b5fd !important;font-size:14px;line-height:1.8;margin:0;">{final_answer}</p>
            </div>
            ''', unsafe_allow_html=True)

            st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)

            # 지표
            st.markdown('<div style="color:#3b1a6e;font-size:10px;letter-spacing:0.1em;margin-bottom:10px;">CONFIDENCE_METRICS://</div>',
                        unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("의견 일치도",     f"{scores.get('agree', 0)} %")
            with c2: st.metric("사실 기반 자신감", f"{scores.get('fact', 0)} %")
            with c3: st.metric("아이디어 다양성",  f"{scores.get('diversity', 0)} %")

            # 참여 팀원
            role_map = {
                "gemini_A": "GMN-A · 분석가",
                "gemini_B": "GMN-B · 검증가",
                "gemini_C": "GMN-C · 선생님",
                "gemini_D": "GMN-D · 브레인스토머",
            }
            if models_used:
                team = " &nbsp;|&nbsp; ".join(role_map.get(m, m) for m in models_used)
                st.markdown(f'<div style="color:#3b1a6e;font-size:10px;margin:14px 0 4px;">// TEAM: {team}</div>',
                            unsafe_allow_html=True)

            # 원본 아코디언
            if accordion_items:
                st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
                st.markdown('<div style="color:#3b1a6e;font-size:10px;letter-spacing:0.1em;margin-bottom:8px;">RAW_OUTPUTS:// (펼치기)</div>',
                            unsafe_allow_html=True)
                for item in accordion_items:
                    name = item.get("model", "unknown")
                    with st.expander(role_map.get(name, name)):
                        st.write(item.get("summary", ""))

            # 오류 안내
            if error_type == "partial":
                st.info("// 오늘은 한 AI가 말을 안 듣네요. 나머지 팀으로 답을 만들어 봤어요.")
            elif error_type == "full":
                st.error("// 팀 전체가 잠깐 쉬는 중이에요. 잠시 후 다시 시도해 주세요.")
            elif error_type == "quota":
                st.warning("// 오늘 자리가 모두 찼어요. 내일 자정에 다시 열립니다.")

            st.markdown('<hr class="neon-divider">', unsafe_allow_html=True)
            if st.button("↩  RESET  ·  다시 물어보기"):
                st.rerun()
