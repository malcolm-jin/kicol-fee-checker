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

# 계산 방식 선택
mode = st.radio("계산 방식", ["분당 단가 기준(원/분)", "시간당 단가 기준(원/시간)"], horizontal=True)
is_min = mode.startswith("분당")

# 입력창
rate = st.text_input("① 최대 단가 입력", placeholder="분당: 1~999 / 시간당: 1000 이상")
weeks = st.text_input("② 한 달 주 환산 수", placeholder="예: 4, 4.2, 4.3, 4.5")

# ✅ 버튼 배치 (가로로 나란히)
col1, col2 = st.columns(2)

with col1:
    btn_calc = st.button("판정하기", use_container_width=True)

with col2:
    if st.button("다시 계산하기", use_container_width=True):
        st.rerun()

# 판정 결과 실행
if btn_calc:
    try:
        # 입력값 정제 (쉼표 제거 등)
        rate_val = int(rate.replace(",", "").strip())
        weeks_val = float(weeks.replace(",", "").strip())
        if weeks_val <= 0 or rate_val <= 0:
            raise ValueError
    except:
        st.error("① 최대 단가, ② 한 달 주 환산 수를 숫자로 정확히 입력해 주세요.")
        st.stop()

    # 단가 제한 체크
    if is_min:
        if not (1 <= rate_val <= 999):
            st.error("분당 단가 기준일 때는 1~999 사이만 입력 가능합니다.")
            st.stop()
    else:
        if rate_val < 1000:
            st.error("시간당 단가 기준일 때는 1000 이상만 입력 가능합니다.")
            st.stop()

    # 계산 실행
    sessions, ok, per_min, per_hour, max_fee = find_sessions(is_min, rate_val, weeks_val)

    st.markdown("---")
    st.subheader("📋 신고서 작성용")
    
    # 결과 출력 (TYPE 1 & 2)
    type1_text = f"**TYPE 1 (시간당 단가 기입)**\n\n월 {fmt_won(MONTHLY_FEE_WON)}\n\n시간 당 {fmt_won(round(per_hour))}"
    type2_text = f"**TYPE 2 (산식 기입)**\n\n월 {fmt_won(MONTHLY_FEE_WON)}\n\n({LESSON_MINUTES}분 * {sessions}회 * {fmt_num(weeks_val)}주)"

    st.info(type1_text)
    st.info(type2_text)

    st.subheader("🔍 판정 상세")
    st.write(f"- 결과: **{'✅ 신고 가능' if ok else '⚠️ 조정 필요'}**")
    st.write(f"- 한 달 주 환산 수: {fmt_num(weeks_val)}주")
    st.write(f"- 주 수업수(자동 조정됨): {sessions}회")
    st.write(f"- 현재 분당 단가: {per_min:.2f}원/분")
    st.write(f"- 현재 시간당 단가: {per_hour:.0f}원/시간")
    st.write(f"- 최대 교습비(입력 단가 기준): {fmt_won(max_fee)}")