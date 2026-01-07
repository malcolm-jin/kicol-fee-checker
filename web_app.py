import streamlit as st

# ====== 1. 고정 값 및 로직 설정 ======
LESSON_MINUTES = 45
MONTHLY_FEE_WON = 110_000
SEARCH_MAX_SESSIONS = 20

def fmt_won(n: float) -> str:
    return f"{int(round(n)):,}원"

def fmt_num(n: float, digits: int = 2) -> str:
    return f"{n:.{digits}f}".rstrip("0").rstrip(".")

def eval_min(rate: int, weeks: float, sessions: int):
    mins = weeks * sessions * LESSON_MINUTES
    per_min = MONTHLY_FEE_WON / mins
    per_hour = per_min * 60
    max_fee = rate * mins
    ok = max_fee >= MONTHLY_FEE_WON
    return ok, per_min, per_hour, max_fee

def eval_hour(rate: int, weeks: float, sessions: int):
    hours = weeks * sessions * (LESSON_MINUTES / 60)
    per_hour = MONTHLY_FEE_WON / hours
    per_min = per_hour / 60
    max_fee = rate * hours
    ok = max_fee >= MONTHLY_FEE_WON
    return ok, per_min, per_hour, max_fee

def find_sessions(is_min_mode: bool, rate: int, weeks: float):
    for s in range(1, SEARCH_MAX_SESSIONS + 1):
        if is_min_mode:
            ok, per_min, per_hour, max_fee = eval_min(rate, weeks, s)
        else:
            ok, per_min, per_hour, max_fee = eval_hour(rate, weeks, s)
        if ok:
            return s, ok, per_min, per_hour, max_fee
    return SEARCH_MAX_SESSIONS, False, 0, 0, 0

# ====== 2. 웹 화면 구성 (UI) ======
st.set_page_config(page_title="키즈스콜레 리딩클럽 교습비 계산기", layout="centered")

st.title("키즈스콜레 리딩클럽 교습비 계산기")

st.markdown(
"""
**<사용 방법>** ① 관할 교육지원청 연락하여 '교습과정의 교습비 단가'와 '1개월 주 환산 값' 찾기  
② 아래 입력 후 **판정하기** 클릭  
③ TYPE 1 및 TYPE 2 참고하여 신고서에 작성
"""
)

# --- 입력값 초기화 로직 추가 ---
# '다시 계산하기' 버튼을 눌렀을 때 입력창을 비우기 위한 설정입니다.
if 'rate_val' not in st.session_state:
    st.session_state.rate_val = ""
if 'weeks_val' not in st.session_state:
    st.session_state.weeks_val = ""

# 계산 방식 선택
mode = st.radio("계산 방식", ["분당 단가 기준(원/분)", "시간당 단가 기준(원/시간)"], horizontal=True)
is_min = mode.startswith("분당")

# 입력창 (session_state와 연결하여 버튼 클릭 시 지워지게 설정)
rate_input = st.text_input("① 최대 단가 입력", value=st.session_state.rate_val, key="rate_input_field", placeholder="분당: 1~999 / 시간당: 1000 이상")
weeks_input = st.text_input("② 한 달 주 환산 수", value=st.session_state.weeks_val, key="weeks_input_field", placeholder="예: 4, 4.2, 4.3, 4.5")

# 버튼 배치
col1, col2 = st.columns(2)

with col1:
    btn_calc = st.button("판정하기", use_container_width=True)

with col2:
    # ✅ 다시 계산하기 버튼 클릭 시 모든 입력값 초기화
    if st.button("다시 계산하기", use_container_width=True):
        st.session_state.rate_val = ""
        st.session_state.weeks_val = ""
        # 텍스트 입력 필드의 내부 키값도 직접 초기화
        st.session_state.rate_input_field = ""
        st.session_state.weeks_input_field = ""
        st.rerun()

# 판정 결과 실행
if btn_calc:
    try:
        # 입력값 확인
        rate_num = int(rate_input.replace(",", "").strip())
        weeks_num = float(weeks_input.replace(",", "").strip())
        if weeks_num <= 0 or rate_num <= 0:
            raise ValueError
    except:
        st.error("① 최대 단가, ② 한 달 주 환산 수를 숫자로 정확히 입력해 주세요.")
        st.stop()

    if is_min:
        if not (1 <= rate_num <= 999):
            st.error("분당 단가 기준일 때는 1~999 사이만 입력 가능합니다.")
            st.stop()
    else:
        if rate_num < 1000:
            st.error("시간당 단가 기준일 때는 1000 이상만 입력 가능합니다.")
            st.stop()

    # 계산 실행
    sessions, ok, per_min, per_hour, max_fee = find_sessions(is_min, rate_num, weeks_num)

    st.markdown("---")
    st.subheader("📋 신고서 작성용")
    
    type1_text = f"**TYPE